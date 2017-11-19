# Set color in living room based on what's playing on Plex

movie_color_mapping = {
    'Beauty and the Beast (1992)': 'yellow',
    'A Christmas Story (1983)': 'christmas',
    'Finding Nemo (2003)': 'blue',
    'Frozen (2013)': 'cyan',
    'Halloweentown (1998)': 'orange',
    'The Lion King (1994)': 'orange',
    'The Martian (2015)': 'orange',
    'Monsters, Inc. (2001)': 'purple',
    'Tangled (2010)': 'green',
    'Up (2009)': 'pink'
}

media_title = hass.states.get('sensor.media_title').state 
media_type = hass.states.get('sensor.media_type').state
media_status = hass.states.get('sensor.media_state').state

if media_type == 'Movies' and media_status == 'playing':
    hass.services.call('input_boolean', 'turn_off', {'entity_id': 'input_boolean.flux_living_room'})
    if media_title in movie_color_mapping.keys():
        color = movie_color_mapping[media_title]
        logger.warn('Using color {}'.format(color))
        hass.services.call('scene', 'turn_on', {'entity_id': 'scene.{}'.format(color)})
    else:
        hass.services.call('scene', 'turn_on', {'entity_id': 'scene.movie_mode'})
elif media_type == 'Movies' and media_status == 'paused':
    hass.services.call('input_boolean', 'turn_on', {'entity_id': 'input_boolean.flux_living_room'})
    hass.services.call('light', 'turn_off', {'entity_id': 'light.corner'})
    hass.services.call('light', 'turn_on', {'entity_id': 'light.corner'})
elif media_status == 'idle':
    hass.services.call('input_boolean', 'turn_on', {'entity_id': 'input_boolean.flux_living_room'})
