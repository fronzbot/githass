#-----------------------------------------------------------------------------
# Changes thermostat based on external and internal temps
#-----------------------------------------------------------------------------

# Thermostat thresholds
THRESHOLD_FOR_HEAT = 57
THRESHOLD_FOR_AC   = 77
AC   = {'home': 75, 'away': 79, 'sleep': 77}
HEAT = {'home': 68, 'away': 65, 'sleep': 67}

SLEEP_TIME = [5, 21]

# Get current temperatures
temp = hass.states.get('sensor.dark_sky_temperature').state

AC['home'] = hass.states.get('input_number.ac_home').state
AC['away'] = hass.states.get('input_number.ac_away').state
AC['sleep'] = hass.states.get('input_number.ac_sleep').state

HEAT['home'] = hass.states.get('input_number.heat_home').state
HEAT['away'] = hass.states.get('input_number.heat_away').state
HEAT['sleep'] = hass.states.get('input_number.heat_sleep').state

try:
    outside_temp = float(temp)
except TypeError:
    logger.error("Could not get temperature from dark sky sensor.")

living_room_temp = float(hass.states.get('sensor.living_room_temperature').state)

# Get various system stats
thermostat_enable = (hass.states.get('input_boolean.thermostat_enable').state == 'on')
someone_home = (hass.states.get('sensor.occupancy').state == 'home' or hass.states.get('input_boolean.guest_mode').state == 'on')
on_the_way_home = (hass.states.get('input_boolean.on_the_way_home').state == 'on')
current_time = datetime.datetime.now()
current_hour = current_time.hour

current_mode = hass.states.get('climate.thermostat_73_5c_83').state

# Determine home, away, or sleep
if someone_home or on_the_way_home:
    state_key = 'home'
    if current_hour <= SLEEP_TIME[0] or current_hour >= SLEEP_TIME[1]:
        state_key = 'sleep'
else:
    state_key = 'away'

# Some logic high indoor temp
too_hot_inside = (outside_temp > 74 and (living_room_temp >= (outside_temp + 1)))

logger.error("Outside: {}, Living Room: {}, Home: {}, Time: {}, State: {}".format(outside_temp, living_room_temp, someone_home, current_time, state_key))

# Only fire if thermostat is enabled

if thermostat_enable:
    target_high = 82
    target_low = 58
    nominal_temp = 70
    mode = 'off'
    if outside_temp > THRESHOLD_FOR_AC:
        mode = 'cool'
        target_high = AC[state_key]
        nominal_temp = AC[state_key]
    elif outside_temp < THRESHOLD_FOR_HEAT:
        mode = 'heat'
        target_low = HEAT[state_key]
        nominal_temp = HEAT[state_key]
    # Now make service call
    logger.error('Mode: {}, Outside: {}, Temperature: {}'.format(mode, outside_temp, nominal_temp))
    if current_mode != mode:
        data_mode = {'entity_id': 'climate.thermostat_73_5c_83', 'temperature': nominal_temp, 'operation_mode': mode}
        hass.services.call('climate', 'set_temperature', data_mode)
else:
    hass.services.call('climate', 'set_operation_mode', {'entity_id': 'climate.thermostat_73_5c_83', 'operation_mode': 'off'})

if on_the_way_home:
    hass.services.call('input_boolean', 'turn_off', {'entity_id': 'input_boolean.on_the_way_home'})
