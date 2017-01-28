from homeassistant.components import blink
from homeassistant.components.switch import SwitchDevice

DEPENDENCIES = ['blink']


def setup_platform(hass, config, add_devices, discovery_info=None):
    data = hass.data[blink.DOMAIN].blink
    
    for name, devices in data.cameras.items():
        add_devices([BlinkSwitch(name, data, 'snap_picture')])
        add_devices([BlinkSwitch(name, data, 'motion')])
        
    add_devices([BlinkArmSystem(data)])


class BlinkSwitch(SwitchDevice):
    def __init__(self, name, data, type):
        self._name = 'blink ' + name + ' ' + type
        self._camera_name = name
        self.data = data
        self.type = type
        if self.type == 'motion':
            self._state = self.data.cameras[self._camera_name].armed == 'armed'
        elif self.type == 'snap_picture':
            self._state = False
        else:
            self._state = None
            
    @property
    def name(self):
        return self._name.replace(" ", "_")
        
    @property
    def is_on(self):
        return self._state
        
    def turn_on(self, **kwargs):
        camera = self.data.cameras[self._camera_name]
        if self.type == 'motion':
            camera.set_motion_detect(True)
            self._state = True
        elif self.type == 'snap_picture':
            camera.snap_picture()
            self.turn_off()
        else:
            self._state = None
        
    def turn_off(self, **kwargs):
        camera = self.data.cameras[self._camera_name]
        if self.type == 'motion':
            camera.set_motion_detect(False)
            self._state = False
        elif self.type == 'snap_picture':
            self._state = False
        else:
            self._state = None

class BlinkArmSystem(SwitchDevice):
    def __init__(self, data):
        self._name = 'blink_arm_system'
        self.data = data
        self._state = self.data.arm
    
    @property
    def name(self):
        return self._name
        
    @property
    def is_on(self):
        return self._state
        
    def turn_on(self, **kwargs):
        self.data.arm = True
        self._state = True
        
    def turn_off(self, **kwargs):
        self.data.arm = False
        self._state = False