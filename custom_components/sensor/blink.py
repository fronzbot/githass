import logging

from homeassistant.components import blink
from homeassistant.const import TEMP_FAHRENHEIT
from homeassistant.helpers.entity import Entity

DEPENDENCIES = ['blink']
SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_FAHRENHEIT],
    'battery': ['Battery', ''],
    'notifications': ['Notifications', '']
}

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    if discovery_info is None:
        return
        
    data = hass.data[blink.DOMAIN].blink
    devs = list()
    index = 0
    for name, device in data.cameras.items():
        devs.append(BlinkSensor(name, 'temperature', index, data))
        devs.append(BlinkSensor(name, 'battery', index, data))
        devs.append(BlinkSensor(name, 'notifications', index, data))
        index += 1
        
    add_devices(devs)
    

class BlinkSensor(Entity):
    def __init__(self, name, type, index, data):
        self._name = 'blink ' + name + ' ' + SENSOR_TYPES[type][0]
        self._camera_name = name
        self._type = type
        self.data = data
        self.index = index
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[type][1]
        self.update()
        
    @property
    def name(self):
        return self._name.replace(" ", "_")
        
    @property
    def state(self):
        return self._state
        
    @property
    def unique_id(self):
        return "sensor_blink_{}_{}".format(self._name, self.index)
        
    @property
    def unit_of_measurement(self):
        return self._unit_of_measurement
        
    def update(self):
        camera = self.data.cameras[self._camera_name]
        if self._type == 'temperature':
            self._state = camera.temperature
        elif self._type == 'battery':
            self._state = camera.battery
        elif self._type == 'notifications':
            self._state = camera.notifications
        else:
            self._state = None
            _LOGGER.warning("Could not retrieve state from %s", self.name)
            