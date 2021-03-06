# githass ![Home Assistant CI](https://github.com/fronzbot/githass/workflows/Home%20Assistant%20CI/badge.svg?branch=master)

## Home Assistant Configuration
Currently running on a home media server using [unRAID](https://lime-technology.com/) (Home Assistant runs in a docker)

### Components Used:
- Weather:
  - [OpenWeatherMap](https://home-assistant.io/integrations/openweathermap/)
- Climate:
  - [Nexia](https://home-assistant.io/integrations/nexia/)
- Lights:
  - [Phillips Hue](https://home-assistant.io/components/light.hue/)
      - 5x 2nd Gen Color Ambience Bulbs
      - 8x White Ambience Bulbs
- [Zwave](https://home-assistant.io/docs/z-wave/):
  - Aeotec Z-wave Stick
      -  1x GE Z-wave Switches
      -  1x Aeotec Smart Switch 
      -  3x First Alert ZCOMBO Smoke/CO detectors
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
- HA Reset notifications and memory leak notifications
- Nightly data storage for daily average/max/min to be displayed as a graph in the front end (to get long-term history)


(Images last updated March 3, 2019 may not reflect current configuration)
![](https://github.com/fronzbot/githass/blob/master/images/ha_home_page.png)
![](https://github.com/fronzbot/githass/blob/master/images/ha_thermostat.png)
