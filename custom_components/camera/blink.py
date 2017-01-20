"""
This component provides basic support for Blink cameras
API info from https://github.com/MattTW/BlinkMonitorProtocol
"""
import logging

import requests
import voluptuous as vol

from homeassistant.components.camera import (Camera, PLATFORM_SCHEMA)
from homeassistant.components.http import (CONF_BASE_URL, CONF_SERVER_PORT)
from homeassistant.const import (
    CONF_NAME, CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_USERNAME): cv.string
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup a Blink Camera."""
    add_devices([BlinkCamera(config)])
    
class BlinkCamera(Camera):
    """An implementation of a Blink camera."""

    def __init__(self, device_info):
        """Initialize a Blink system."""
        super().__init__()
        self._base_url = 'https://prod.immedia-semi.com'
        self._host     = 'prod.immeda-semi.com'
        self._username = device_info.get(CONF_USERNAME)
        self._password = device_info.get(CONF_PASSWORD)
        self._name     = device_info.get(CONF_NAME)
        self._picture_url = CONF_BASE_URL+':'+CONF_SERVER_PORT \
                            + '/local/' + self._name+'.jpg'
        
        self._authtoken = self.get_authtoken()
        self._headers   = {'Host':self._host, 'TOKEN_AUTH':self._authtoken}
        self._id        = self.get_ids()
        
        
        
        _LOGGER.info('Using the following URL for %s: %s',
                     self._name, self._picture_url)

    def get_authtoken(self):
        """Returns authtoken"""
        headers = {'Host':self._host, 'Content-Type':'application/json'}
        data    = '{"password" : "'+self._password+'", \
                    "client_specifier" : "iPhone 9.2 | 2.2. | 222", \
                    "email" : "'+self._username+'" }'
      
        response = requests.post(self._base_url+'/login', headers=headers, data=data)
      
        return response.json()['authtoken']['authtoken']
      
    def get_ids(self):
        """Returns network and account ids"""
        response = requests.get(self._base_url+'/networks', headers=self._headers)
        ids = {'network_id':response.json()['networks'][0]['id'], \
               'account_id':response.json()['networks'][0]['account_id'] \
              }
            
        return ids      
    
    def camera_image(self):
        """Return a still image reponse from the camera."""
        # Send the request to get last image from video
        response = requests.get(self._base_url+'/events/network/'+str(self._id['network_id']), headers=self._headers, timeout=10)
        events   = response.json()['event']
        
        for i in range(0, len(events)):
            if 'video_url' in events[i]:
                last_event = events[i]['video_url']
                break
                
        if last_event:
          image_url = self._base_url+'/'+last_event[:-3]+'jpg'
          response = requests.get(image_url, headers=self._headers)

          return response.content
        
    @property
    def name(self):
        """Return the name of this camera."""
        return self._name