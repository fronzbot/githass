#-----------------------------------------------------------------------------
# Changes thermostat based on external and internal temps
#-----------------------------------------------------------------------------

# Thermostat thresholds
THRESHOLD_FOR_HEAT = 55
THRESHOLD_FOR_AC   = 77
AC   = {'home': 75, 'away': 82, 'sleep': 78}
HEAT = {'home': 67, 'away': 59, 'sleep': 64}

SLEEP_TIME = [5, 21]

# Get current temperatures
temp2 = hass.states.get('sensor.pws_temp_f').state
temp1 = hass.states.get('sensor.dark_sky_temperature').state

if temp1 is None:
    outside_temp = float(temp2)
else:
    outside_temp = float(temp1)
living_room_temp = float(hass.states.get('sensor.living_room_temperature').state)
try:
    bedroom_temp = float(hass.states.get('sensor.bedroom_temperature').state)
except ValueError:
    bedroom_temp = living_room_temp
living_room_humidity = float(hass.states.get('sensor.living_room_humidity').state)

# Get various system stats
thermostat_enable = (hass.states.get('input_boolean.thermostat_enable').state == 'on')
someone_home = (hass.states.get('sensor.occupancy').state == 'home' or hass.states.get('input_boolean.guest_mode').state == 'on')
on_the_way_home = (hass.states.get('input_boolean.on_the_way_home').state == 'on')
current_time = datetime.datetime.now()
current_hour = current_time.hour

# Determine home, away, or sleep
if someone_home or on_the_way_home:
    state_key = 'home'
    if current_hour <= SLEEP_TIME[0] or current_hour >= SLEEP_TIME[1]:
        state_key = 'sleep'
else:
    state_key = 'away'

# Some logic for high humidity or high indoor temp
too_humid = living_room_humidity > 59
too_hot_inside = (outside_temp > 74 and (living_room_temp >= (outside_temp + 1)))

# Only fire if thermostat is enabled
if thermostat_enable:
    target_high = 82
    target_low = 58
    mode = 'off'
    if outside_temp > THRESHOLD_FOR_AC:
        mode = 'auto'
        target_high = AC[state_key]
        nominal_temp = AC[state_key]
    elif outside_temp < THRESHOLD_FOR_HEAT:
        mode = 'auto'
        target_low = HEAT[state_key]
        nominal_temp = HEAT[state_key]
#    elif state_key != 'sleep' and (too_hot_inside or too_humid):
#        mode = 'auto'
#        target_high = living_room_temp - 1
#        nominal_temp = living_room_temp - 1
    # Now make service call

    logger.info('Mode: {}, Outside: {}, Target High: {}, Target Low: {}'.format(mode, outside_temp, target_high, target_low))
    data_mode = {'entity_id': 'climate.living_room', 'operation_mode': mode}
    hass.services.call('climate', 'set_operation_mode', data_mode)
    if mode != 'off':
        data_temps = {'entity_id': 'climate.living_room', 'temperature': nominal_temp, 'target_temp_high': target_high, 'target_temp_low': target_low}
        hass.services.call('climate', 'set_temperature', data_temps)

    hass.services.call('input_boolean', 'turn_off', {'entity_id': 'input_boolean.on_the_way_home'})
