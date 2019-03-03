# githass [![Build Status](https://travis-ci.org/fronzbot/githass.svg?branch=master)](https://travis-ci.org/fronzbot/githass)
## Home Assistant Configuration
Currently running on a home media server using [unRAID](https://lime-technology.com/) (Home Assistant runs in a docker)

### Components Used:
- Weather:
  - [darksky](https://home-assistant.io/components/sensor.wunderground/)
- Device Tracking:
  - [gpslogger](https://home-assistant.io/components/device_tracker.gpslogger/)
- Climate:
  - [Ecobee](https://home-assistant.io/components/climate.ecobee/) Version 3 with one remote sensor
- Lights:
  - [Phillips Hue](https://home-assistant.io/components/light.hue/)
      - 5x 2nd Gen Color Ambience Bulbs
      - 8x White Ambience Bulbs
- [Zwave](https://home-assistant.io/docs/z-wave/):
  - Aeotec Z-wave Stick
      -  2x GE Z-wave Switches
      -  1x Leviton Z-wave+ Switch
      -  1x Aeotec Smart Switch 
      -  3x First Alert ZCOMBO Smoke/CO2 detectors
- [Emulated Hue](https://home-assistant.io/components/emulated_hue/)
  - 1x Amazon Echo
  - 2x Amazon Echo Dot
- [Google Assistant](https://home-assistant.io/components/google_assistant/)
  - 2x Google Home
  - 1x Google Home Mini
- Notifications:
  - [HTML5](https://home-assistant.io/components/notify.html5/) Push Notifications
- Other Components:
  - [Blink Camera](https://home-assistant.io/components/blink/)
  - [Google Wifi](https://home-assistant.io/components/sensor.google_wifi/)
  - [PiHole](https://home-assistant.io/components/sensor.pi_hole/)
  - [Speedtest](https://home-assistant.io/components/sensor.speedtest/)
  - [Fast.com](https://home-assistant.io/components/sensor.fastdotcom/)
- Databases:
  - MySQL for default recorder
  - [Influx and Grafana](https://home-assistant.io/blog/2015/12/07/influxdb-and-grafana/) for more long-term trend plotting

### Automations:
- Light control based on device presence and sun status
- Theromstat control based on outside temperature and device presence
- HA Reset notifications and memory leak notifications
- Nightly data storage for daily average/max/min to be displayed as a graph in the front end (to get long-term history)

### Notes:
1. I use secrets.yaml to hide sensitive information (like API keys)
2. Currently, Home Assistant has local control over only Hue and Z-wave devices (Ecobee talks to cloud).  My goal is to force everything to be local so if the interenet goes out, my home will still be automated.
 
(Images last updated March 3, 2019 may not reflect current configuration)
![](https://github.com/fronzbot/githass/blob/master/images/ha_home_page.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_thermostat.png)
