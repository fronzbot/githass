# githass [![Build Status](https://travis-ci.org/fronzbot/githass.svg?branch=master)](https://travis-ci.org/fronzbot/githass)
## Home Assistant Configuration
Currently running on 3rd gen RaspberryPi (OS: Raspbian Jessie)

### Components Used:
- Weather:
  - ![wunderground](https://home-assistant.io/components/sensor.wunderground/) 
  - ![darksky](https://home-assistant.io/components/sensor.wunderground/)
- Device Tracking:
  - ![nmap](https://home-assistant.io/components/device_tracker.nmap_tracker/)
- Climate:
  - ![Ecobee](https://home-assistant.io/components/climate.ecobee/) Version 3 with one remote sensor
- Lights:
  - ![Phillips Hue](https://home-assistant.io/components/light.hue/)
      - 5x 2nd Gen Color Ambience Bulbs
      - 5x White Ambience Bulbs
- ![Zwave](https://home-assistant.io/docs/z-wave/):
  - Aeotec Z-wave Stick
      -  2x GE Z-wave Switches
      -  1x Leviton Z-wave+ Switch
      -  1x Aeotec Smart Switch 
      -  3x First Alert ZCOMBO Smoke/CO2 detectors
- Media Players:
  - ![Plex](https://home-assistant.io/components/media_player.plex/)
      - NVIDIA Shield TV
      - Amazon Fire TV
      - Chrome Web Browser
  - ![Google Cast](https://home-assistant.io/components/media_player.cast/)
      - NVIDIA Shield TV
      - 2x Google Home
- ![Emulated Hue](https://home-assistant.io/components/emulated_hue/)
  - 1x Amazon Echo
  - 2x Amazon Echo Dot
  - 2x Google Home
- Notifications:
  - ![HTML5](https://home-assistant.io/components/notify.html5/) Push Notifications
- Other Components:
  - ![Blink Camera](https://home-assistant.io/components/blink/)
  - ![Google Wifi](https://home-assistant.io/components/sensor.google_wifi/)
  - ![PiHole](https://home-assistant.io/components/sensor.pi_hole/)
  - ![Glances](https://home-assistant.io/components/sensor.glances/)
  - ![Speedtest](https://home-assistant.io/components/sensor.speedtest/)
  - ![Fast.com](https://home-assistant.io/components/sensor.fastdotcom/)

### Automations:
- Light control based on device presence and sun status
- Theromstat control based on outside temperature and device presence
- HA Reset notifications and memory leak notifications
- Nightly data storage for daily average/max/min to be displayed as a graph in the front end (to get long-term history)

### Notes:
1. I use secrets.yaml to hide sensitive information (like API keys)
2. Currently, Home Assistant has local control over only Hue and Z-wave devices (Ecobee talks to cloud).  My goal is to force everything to be local so if the interenet goes out, my home will still be automated.
  * ~~Most likely I'll just slowly phase out Wink and get a zwave stick for future ZWAVE components~~.  I'll have to just live with the ecobee cloud-only BS for now...
 
### Future Improvements:
- ~~Automation override switches~~ (added 8/21/2016)
- ~~Rapberry pi status monitoring~~ (added 8/27/2016)
- ~~Integrate Alexa (![emulated_hue}(https://home-assistant.io/components/emulated_hue/) looks promising)~~ (added 10/23/2016)
- ~~Selectable scenes~~ (added 11/6/2016)
- Vacation Mode
- ~~Thermostat automations (instead of using built-in Ecobee scheduling)~~ (added 7/8/2017)
- Full local control (Ecobee does not allow local only)
- Intents
- More components:
  - ~~Z-wave stick (for future Wink removal)~~ (added 11/25/2016)
  - Home weather station
  - More Lights/switches
  - Door/window sensors
  - IP Cameras
  - Sprinkler/Irrigation automation
  - ~~Washer status~~
  - Dishwasher status (custom sensor, probably)
  
Current setup cost estimate: $1300

(Images last updated July 23, 2017, may not reflect current configuration)
![](https://github.com/fronzbot/githass/blob/master/images/ha_home_page.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_media.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_media2.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_thermostat.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_weather1.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_weather2.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_stats.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_stats2.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_override.png)
