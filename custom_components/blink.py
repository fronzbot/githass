import logging
import os
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import discovery
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'blink'
REQUIREMENTS = ['blinkpy==0.4.2']

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
    })
}, extra=vol.ALLOW_EXTRA)


class BlinkSystem(object):
    def __init__(self, config_info):
        import blinkpy
        self.blink = blinkpy.Blink(username=config_info[DOMAIN][CONF_USERNAME], password=config_info[DOMAIN][CONF_PASSWORD])
        self.blink.setup_system()

    def update(self):
        pass


def setup(hass, config):
    """Your controller/hub specific code."""
    hass.data[DOMAIN] = BlinkSystem(config)
    discovery.load_platform(hass, 'camera', DOMAIN, {}, config)
    discovery.load_platform(hass, 'sensor', DOMAIN, {}, config)
    discovery.load_platform(hass, 'switch', DOMAIN, {}, config)
    return True