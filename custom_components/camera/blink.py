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
from homeassistant.helpers import config_validation as cv
from homeassistant.util.async import run_coroutine_threadsafe
from homeassistant.util import Throttle

DEPENDENCIES = ['blink']

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=120)

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup a Blink Camera."""
    if discovery_info is None:
        return
        
    data = hass.data[blink.DOMAIN].blink
    
    devs = list()
    for name, device in data.cameras.items():
        devs.append(BlinkCamera(hass, data, name))

    add_devices(devs)
    

class BlinkCamera(Camera):
    """An implementation of a Blink Camera"""
    def __init__(self, hass, data, name):
        """Initialize a camera"""
        super().__init__()
        self.data = data
        self.hass = hass
        self._name = name
        self.notifications = self.data.cameras[self._name].notifications
        self.response = None

        _LOGGER.info("Initialized blink camera %s", self._name)

    @property
    def name(self):
        """Returns camera name"""
        return self._name
    
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def request_image(self):
        _LOGGER.info("Requesting new image from blink servers")
        image_url = self.check_for_motion()
        header = self.data.cameras[self._name].header
        self.response = requests.get(image_url, headers=header, stream=True)
        
    def check_for_motion(self):
        self.data.refresh()
        notifs = self.data.cameras[self._name].notifications
        if notifs > self.notifications:
            # We detected motion at some point
            self.data.last_motion()
            self.notifications = notifs
            return self.data.cameras[self._name].motion['image']
        elif notifs < self.notifications:
            self.notifications = notifs

        return self.data.camera_thumbs[self._name]

    def camera_image(self):
        """Return bytes of camera image."""
        return run_coroutine_threadsafe(
            self.async_camera_image(), self.hass.loop).result()

    @asyncio.coroutine
    def async_camera_image(self):
        """Return a still image reponse from the camera."""
        self.request_image()
        return self.response.content
