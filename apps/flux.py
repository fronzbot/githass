'''
Flux

Module uses AppDaemon to dynamically set light color temperatures
based on time of day.  Note that this is similar to the homeassistant
component flux switch, but built in a custom way to not have race
conditions within the core (occasionally automations won't trigger
and turning the switch off won't actually do anything... at least in
my experience, that is)

There are two color-changing segments:

sunrise --> from sunrise+offset to day+offset
sunset --> from sunset+offset to night+offset

in between sunrise and sunset, we are at day
in between sunset and sunrise we are at night

--------------------------
appdaemon.yaml setup example:

flux:
    module: flux
    class: Flux
    constrain_input_boolean: input_boolean.flux
    light: light.couch_left,light.couch_right,light.corner

'''

import appdaemon.plugins.hass.hassapi as hass
import datetime as dt
import pytz

DEBUG = False


def utc_to_est(datetime_obj):
    """Naive timezone conversion because I'm lazy AF."""
    tz_offset = dt.timedelta(hours=-5)
    return datetime_obj + tz_offset


class Flux(hass.Hass):

    def initialize(self):
        # Colors dict contains:
        # Color temperature
        # Starting offset in minutes
        self.colors = {
            'sunrise': {'temp': 3000, 'offset': -45},
            'day': {'temp': 5000, 'offset': 30},
            'sunset': {'temp': 3000, 'offset': -45},
            'night': {'temp': 2700, 'offset': 60}
        }
        self.offsets = {}
        for key, value in self.colors.items():
            self.offsets[key] = dt.timedelta(minutes=value['offset'])

        self.current_time = utc_to_est(dt.datetime.now()).time()

        self.run_minutely(self.update_color, self.current_time)

        for light in self.split_device_list(self.args['light']):
            self.listen_state(self.update_on_change, light)

    def sunrise_tz(self):
        return utc_to_est(self.sunrise())

    def sunset_tz(self):
        return utc_to_est(self.sunset())

    def update_on_change(self, entity, attribute, old, new, kwargs):
        if self.get_state(entity) == "on" and old == "off":
            self.update_color(None)

    def determine_color_state(self, now):
        sunrise = self.sunrise_tz() - dt.timedelta(days=1)
        sunset = self.sunset_tz() - dt.timedelta(days=1)

        self.times = {
            'sunrise': sunrise + self.offsets['sunrise'],
            'day': sunrise + self.offsets['day'],
            'sunset': sunset + self.offsets['sunset'],
            'night': sunset + self.offsets['night']
        }
        
        now_time = now.time()

        if DEBUG:
            self.log("now: {}, sunset: {}, night: {}".format(now_time, self.times['sunrise'].time(), self.times['night'].time()))

        if now_time <= self.times['sunrise'].time():
            return 'night'
        elif now_time >= self.times['sunrise'].time() and now_time < self.times['day'].time():
            return 'sunrise'
        elif now_time >= self.times['day'].time() and now_time < self.times['sunset'].time():
            return 'day'
        elif now_time >= self.times['sunset'].time() and now_time < self.times['night'].time():
            return 'sunset'
        elif now_time >= self.times['night'].time():
            return 'night'

        # If something errored, just assume we are in night mode
        return 'night'
    
    def calculate_progress(self, now, state):
        if state == 'sunrise':
            start = self.times['sunrise']
            end = self.times['day']
        elif state == 'sunset':
            start = self.times['sunset']
            end = self.times['night']
        else:
            return 1

        progress = round((now - start) / (end - start), 2)

        return progress

    def calculate_color(self, state, progress):
        if state == 'sunrise':
            color_delta = self.colors['day']['temp'] - self.colors['night']['temp']
            new_color = self.colors['night']['temp'] + progress*color_delta
            if new_color > self.colors['day']['temp']:
                new_color = self.colors['day']['temp']
        elif state == 'sunset':
            color_delta = self.colors['day']['temp'] - self.colors['night']['temp']
            new_color = self.colors['day']['temp'] - progress*color_delta
            if new_color < self.colors['night']['temp']:
                new_color = self.colors['night']['temp']
        elif state == 'day':
            new_color = self.colors['day']['temp']
        elif state == 'night':
            new_color = self.colors['night']['temp']

        return new_color

    def update_color(self, kwargs):
        
        now = utc_to_est(dt.datetime.now())
        color_state = self.determine_color_state(now)
        progress = self.calculate_progress(now, color_state)
        new_color = self.calculate_color(color_state, progress)
        mired = int(1e6 / new_color)
        brightness = 254

        if DEBUG:
            self.log("Now={}: Sunrise={}, Sunset={}, State={}, Progress={}, Color={}".format(
                now.time(), self.sunrise_tz().time(), self.sunset_tz().time(),  color_state, progress, new_color))

        for light in self.split_device_list(self.args["light"]):
            if self.get_state(light) == 'on':
                self.turn_on(light, color_temp=mired, brightness=brightness)
