'''
Uses blink api from https://github.com/fronzbot/blinkpy
'''
import logging

import requests
import voluptuous as vol

from homeassistant.components.camera import (Camera, PLATFORM_SCHEMA)
from homeassistant.components.http import (CONF_BASE_URL, CONF_SERVER_PORT)
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import config_validation as cv

REQUIREMENTS = ['blinkpy==0.2.0']

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup a Blink Camera."""
    global NETWORK
    global DEVICE_DICT
    import blinkpy

    NETWORK = blinkpy.Blink(
        username=config.get(CONF_USERNAME),
        password=config.get(CONF_PASSWORD))

    NETWORK.setup_system()
    
    _LOGGER.info("Initialized Blink Module")
    
    devs = list()
    DEVICE_DICT = dict()
    for device in NETWORK.cameras:
        devs.append(BlinkCamera(device))
        new_name = "blink_" + device.name.replace(" ", "_")
        DEVICE_DICT[new_name] = device

    add_devices(devs)


class BlinkCamera(Camera):
    """An implementation of a Blink Camera"""

    def __init__(self, device):
        """Initialize a camera"""
        super().__init__()
        self._name = "blink_" + device.name.replace(" ", "_")
        self._thumbnail = device.thumbnail
        self._clip = device.clip
        self._header = device.header

        _LOGGER.info("Initialized Blink Camera %s", self._name)

    @property
    def name(self):
        """Returns camera name"""
        return self._name

    def camera_image(self):
        """Return a still image reponse from the camera."""
        NETWORK.refresh()
        self._thumbnail = DEVICE_DICT[self._name].thumbnail
        self._clip = DEVICE_DICT[self._name].clip
        response = requests.get(self._thumbnail, headers=self._header)
        return response.content