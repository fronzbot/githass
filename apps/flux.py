'''
Flux

Module uses AppDaemon to dynamically set light color temperatures
based on time of day.  Note that this is similar to the homeassistant
component flux switch, but built in a custom way to not have race
conditions within the core (occasionally automations won't trigger
and turning the switch off won't actually do anything... at least in
my experience, that is)

There are four segments:

sunrise-offset <--> sunrise         ==> nighttime to twilight
sunrise        <--> sunrise+offset  ==> twlight to daytime
sunset-offset  <--> sunset          ==> daytime to twlight
sunset         <--> sunset+offset   ==> twlight to nighttime

--------------------------
appdaemon.yaml setup:

flux:
    module: flux
    class: Flux
    constrain_input_boolean: input_boolean.flux
    light: light.couch_left,light.couch_right,light.corner

'''

import appdaemon.plugins.hass.hassapi as hass
import datetime

DEBUG = False

class Flux(hass.Hass):

    def initialize(self):
        # Colors in Kelvin
        self.sun_offset_mins = [-45, 90, -60, 120]
        self.daytime_color   = 4500
        self.twilight_color  = 3000
        self.nighttime_color = 2200
        self.perc_complete   = 0
        self.brightness      = 254
        self.color_dict      = {'twilight_day': self.nighttime_color, 'daytime': self.twilight_color, 'twilight_night': self.daytime_color, 'nighttime': self.twilight_color}

        # Get the start time for the intital segment
        self.current_time = self.datetime()
        self.get_start_time()

        self.run_minutely(self.update_color, datetime.datetime.now())

        for light in self.split_device_list(self.args["light"]):
            self.listen_state(self.update_on_change, light)

    def update_on_change(self, entity, attribute, old, new, kwargs):
        if self.get_state(entity) == "on" and old == "off":
            #self.log(entity + " just turned on")
            self.update_color(None)

    def update_color(self, kwargs):
        self.get_start_time()
        self.perc_complete    = min(1, (self.current_time - self.start_time)/self.segment_length)

        for light in self.split_device_list(self.args["light"]):
            if DEBUG:
                self.log("Light {} state: {}".format(light, self.get_state(entity=light, attribute='color_temp')))
            if self.get_state(light) == "on":
                new_color = self.color_dict[self.segment] + self.perc_complete*self.offset

                # Clamp color
                if new_color > self.daytime_color:
                    new_color = self.daytime_color
                elif new_color < self.nighttime_color:
                    new_color = self.nighttime_color
                elif (self.segment == 'twlight_night' or self.segment == 'twlight_day') and self.perc_complete > 0.99:
                    new_color = self.twilight_color
                
                mired = int(1e6/new_color)
                self.turn_on(light, color_temp=mired, brightness=self.brightness)
                self.log("Setting Light {} to {}".format(light, mired))
 
                if DEBUG:
                    self.log("Current Time is {} in {} cycle and it is {}% Complete --> {} ({})".format(self.current_time, self.segment, self.perc_complete*100, mired, light))
            
    def get_start_time(self):
        self.current_time = self.datetime()

        if self.sun_up():
            # sun is up, we must be in state 2 or 3
            if self.current_time >= (self.sunset() + datetime.timedelta(minutes=self.sun_offset_mins[2])):
                # Must be in state 3
                self.segment         = 'twilight_night'
                self.offset          = self.twilight_color - self.daytime_color
                self.start_time      = self.sunset() + datetime.timedelta(minutes=self.sun_offset_mins[2])
                self.segment_length  = datetime.timedelta(minutes=abs(self.sun_offset_mins[2]))
            else:
                # We are in state 2
                self.segment         = 'daytime'
                self.offset          = self.daytime_color - self.twilight_color
                self.start_time      = self.sunrise() - datetime.timedelta(days=1)
                self.segment_length  = datetime.timedelta(minutes=abs(self.sun_offset_mins[1]))
        else:
            if self.current_time >= (self.sunrise() + datetime.timedelta(minutes=self.sun_offset_mins[0])):
                # Must be state 1
                self.segment         = 'twilight_day'
                self.offset          = self.twilight_color - self.nighttime_color
                self.start_time      = self.sunrise() + datetime.timedelta(minutes=self.sun_offset_mins[0])
                self.segment_length  = datetime.timedelta(minutes=abs(self.sun_offset_mins[0]))
            else:
                # Must be state 4
                self.segment         = 'nighttime'
                self.start_time      = self.sunset() - datetime.timedelta(days=1)
                self.offset          = self.nighttime_color - self.twilight_color
                self.segment_length  = datetime.timedelta(minutes=abs(self.sun_offset_mins[3]))

