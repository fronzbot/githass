'''
Uses blink api from https://github.com/fronzbot/blinkpy
'''
import asyncio
import logging

import requests
import voluptuous as vol
from datetime import timedelta

from homeassistant.components import blink
from homeassistant.components.camera import Camera
from homeassistant.const import CONF_PATH
from homeassistant.helpers import config_validation as cv
from homeassistant.util.async import run_coroutine_threadsafe
from homeassistant.util import Throttle

DEPENDENCIES = ['blink']

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup a Blink Camera."""
    if discovery_info is None:
        return
        
    data = hass.data[blink.DOMAIN].blink
    
    devs = list()
    for name, device in data.cameras.items():
        devs.append(BlinkCamera(hass, data, name, discovery_info[CONF_PATH]))

    add_devices(devs)


class BlinkCamera(Camera):
    """An implementation of a Blink Camera"""

    def __init__(self, hass, data, name, path):
        """Initialize a camera"""
        super().__init__()
        self.data = data
        self.hass = hass
        self._name = name
        self._imagefile = path + name.replace(" ", "_") + '.jpg'
        self.last_thumb = data.cameras[self._name].thumbnail

        _LOGGER.info("Initialized blink camera %s", self._name)

    @property
    def name(self):
        """Returns camera name"""
        return self._name
    
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def write_image(self):
        _LOGGER.info("WRITING IMAGE TO FILE")
        self.last_thumb = self.data.camera_thumbs[self._name]
        self.data.cameras[self._name].image_to_file(self._imagefile)
        

    def camera_image(self):
        """Return bytes of camera image."""
        return run_coroutine_threadsafe(
            self.async_camera_image(), self.hass.loop).result()
    
    @asyncio.coroutine
    def async_camera_image(self):
        """Return a still image reponse from the camera."""
        _LOGGER.info("INSIDE IMAGE ROUTINE with %s", self.last_thumb)
        self.write_image()
        with open(self._imagefile, 'rb') as file:
            return file.read()