import logging
import os
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_USERNAME, CONF_PASSWORD, CONF_PATH)
from homeassistant.helpers import discovery
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'blink'
REQUIREMENTS = ['blinkpy==0.4.1']
DEFAULT_PATH = '/tmp/'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_PATH, default=DEFAULT_PATH): cv.string
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
    path = config[DOMAIN][CONF_PATH]
    if not os.path.isdir(path):
        _LOGGER.error("Could not set up Blink component because given path is not a directory: %s", path)
        return False
    hass.data[DOMAIN] = BlinkSystem(config)
    discovery.load_platform(hass, 'camera', DOMAIN, {CONF_PATH: path}, config)
    return True