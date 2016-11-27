# githass
## Home Assistant Configuration
Currently running on 3rd gen RaspberryPi (OS: Raspbian Jessie)

###Components Used:
- Dark Sky  and Wunderground for weather
- NMAP Device Tracking
- Ecobee3 Thermostat + 1 Remote Sensor
- Phillips Hue Hub
  -  5x 2nd Gen Color Ambience Bulbs
- Aeotec Z-wave Stick
  -  2x GE Z-wave Switches
- Wink Hub
  -  7x GE Link Bulbs (Zigbee) [6/7 Used- trying to phase out Wink]
- NVIDIA Shield TV
- PLEX Server
- Emulated Hue (for Amazon Echo and future Google Home support)

###Automations:
- Light control based on device presence and sun status
- Theromstat control based on outside temperature and device presence (away mode)

###Notes:
1. I use secrets.yaml to hide sensitive information (like API keys)
2. Currently, Home Assistant has local control over only Hue and Z-wave devices (Wink talks to cloud, Ecobee talks to cloud).  My goal is to force everything to be local so if the interenet goes out, my home will still be automated.
  * Most likely I'll just slowly phase out Wink and ~~get a zwave stick for future ZWAVE components~~.  I'll have to just live with the ecobee cloud-only BS for now...
 
###Future Improvements:
- ~~Automation override switches~~ (added 8/21/2016)
- ~~Rapberry pi status monitoring~~ (added 8/27/2016)
- ~~Integrate Alexa (![emulated_hue}(https://home-assistant.io/components/emulated_hue/) looks promising)~~ (added 10/23/2016)
- ~~Selectable scenes~~ (added 11/6/2016)
- ~~Vacation Modes~~ (Covered by existing automations)
- Full local control
- More components:
  - ~~Z-wave stick (for future Wink removal)~~ (added 11/25/2016)
  - Home weather station (to replace forecast.io)
  - Lights/switches
  - Door/window sensors
  - IP Cameras
  - Sprinkler/Irrigation automation
  - [Washer/dryer status](https://home-assistant.io/blog/2016/08/03/laundry-automation-update/) (custom sensor, probably)
  - Dishwasher status (custom sensor, probably)
  
Current setup cost estimate: $1050

(Images last updated 11/25/2016, may not reflect current configuration)
![](https://github.com/fronzbot/githass/blob/master/images/ha_home_page.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_media.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_media2.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_thermostat.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_presence.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_weather1.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_weather2.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_stats.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_override.png)
