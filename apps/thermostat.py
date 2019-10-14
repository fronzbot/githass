'''
Thermostat

AppDaemon module to set thermostat based on presence and weather
conditions.  Uses input_number instances in frontend to determine
desired set points for Home, Away, Sleep
--------------------------
appdaemon.yaml setup example:

thermostat:
    module: thermostat
    class: Thermostat
    constrain_input_boolean: input_boolean.thermostat_enable
    climate: climate.thermostat_name
    sensors: sensor.whatever, sensor.another

'''

import appdaemon.plugins.hass.hassapi as hass
import datetime as dt
import pytz

DEBUG = False

AC_THRESHOLD = 75
HEAT_THRESHOLD = 56
MAX_DEWPOINT = 60
SLEEP_TIME = [5, 21]

THERMOSTAT = 'climate.thermostat_73_5c_83'

def utc_to_est(datetime_obj):
    """Naive timezone conversion because I'm lazy AF."""
    tz_offset = dt.timedelta(hours=-5)
    return datetime_obj + tz_offset


class Thermostat(hass.Hass):

    def initialize(self):
        self.ac = {
            'home': float(self.get_state('input_number.ac_home')),
            'away': float(self.get_state('input_number.ac_away')), 
            'sleep': float(self.get_state('input_number.ac_sleep'))
        }
        self.heat = {
            'home': float(self.get_state('input_number.heat_home')),
            'away': float(self.get_state('input_number.heat_away')),
            'sleep': float(self.get_state('input_number.heat_sleep'))
        }

        self.current_time = utc_to_est(dt.datetime.now()).time()

        self.run_minutely(self.update_thermostat, self.current_time)

        for value in self.split_device_list(self.args['input_number']):
            self.listen_state(self.update_on_change, value)

    def update_on_change(self, entity, attribute, old, new, kwargs):
        if DEBUG:
            self.log("Updating thermostat on change")
        self.get_input_numbers()
        self.update_thermostat(None)

    def get_input_numbers(self):
        self.ac = {
            'home': float(self.get_state('input_number.ac_home')),
            'away': float(self.get_state('input_number.ac_away')), 
            'sleep': float(self.get_state('input_number.ac_sleep'))
        }
        self.heat = {
            'home': float(self.get_state('input_number.heat_home')),
            'away': float(self.get_state('input_number.heat_away')),
            'sleep': float(self.get_state('input_number.heat_sleep'))
        }
        return None

    def get_desired_mode(self):
        current_temp = float(self.get_state('sensor.dark_sky_temperature'))
        current_feel = float(self.get_state('sensor.dark_sky_apparent_temperature'))
        current_dewpoint = float(self.get_state('sensor.dark_sky_dew_point'))
        if current_temp >= AC_THRESHOLD:
            return 'cool'
        elif current_dewpoint >= MAX_DEWPOINT and current_feel >= AC_THRESHOLD:
            return 'cool'
        elif current_temp <= HEAT_THRESHOLD:
            return 'heat'
        return 'off'

    def get_state_key(self):
        is_home = (self.get_state('sensor.occupancy') == 'home')
        guest = (self.get_state('input_boolean.guest_mode') == 'on')
        on_the_way_home = (self.get_state('input_boolean.on_the_way_home') == 'on')
        now = utc_to_est(dt.datetime.now())
        if now.hour <= SLEEP_TIME[0] or now.hour >= SLEEP_TIME[1]:
            return 'sleep'
        elif is_home or guest or on_the_way_home:
            return 'home'
        return 'away'

    def get_target_temp(self, state_key, mode):
        if mode == 'cool':
            return self.ac[state_key]
        elif mode == 'heat':
            return self.heat[state_key]
        return None

    def set_temperature(self, temp, mode):
        if mode == 'off':
            return self.call_service('climate/turn_off', entity_id=THERMOSTAT)

        return self.call_service('climate/set_temperature', entity_id=THERMOSTAT, temperature=temp, hvac_mode=mode)
        
    def set_mode(self, mode='off', **kwargs):
        if mode == 'off':
            return self.call_service('climate/turn_off', entity_id=THERMOSTAT)

        return self.call_service('climate/set_hvac_mode', entity_id=THERMOSTAT, hvac_mode=mode)

    def update_thermostat(self, time, **kwargs): 
        self.get_input_numbers()
        mode = self.get_desired_mode()
        state_key = self.get_state_key()
        target_temp = self.get_target_temp(state_key, mode)

        current_mode = self.get_state(THERMOSTAT)
        current_temp = self.get_state(THERMOSTAT, attribute='temperature')
        if DEBUG:
            self.log("Current Mode={}, Mode={}, State={}, Target={}, Current Temp={}".format(current_mode, mode, state_key, target_temp, current_temp))

        if current_mode != mode or target_temp != current_temp:
            self.set_mode(mode=mode)
            if target_temp is not None:
                self.set_temperature(target_temp, mode)
            if DEBUG:
                self.log("Called thermostat service.")

