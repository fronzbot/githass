'''
Notify

Module uses AppDaemon in order to push notifcations using notify
service to determine if devices are offline (or when they come
back online).

appdaemon.cfg setup:

[Notify]
module = notify
class = Notify
notify = 1
device_tracker = device_tracker.baratheon,device_tracker.echo,device_tracker.ecobee,device_tracker.google_home,device_tracker.hue_hub,device_tracker.tablo,device_tracker.winkhub

'''


import appdaemon.appapi as appapi
import datetime

class Notify(appapi.AppDaemon):
  
  def initialize(self):
    if "device_tracker" in self.args:
      for tracker in self.split_device_list(self.args["device_tracker"]):
        self.listen_state(self.notify_change, tracker)
   
    
  def notify_change(self, entity, attribute, old, new, kwargs):
    if(new == "not_home" and old == "home"):
      self.log("{} is Offline".format(self.friendly_name(entity)))
      self.notify("{} is Offline".format(self.friendly_name(entity)))
    if(new == "home" and old == "not_home"):
      self.log("{} back Online".format(self.friendly_name(entity)))
      self.notify("{} back Online".format(self.friendly_name(entity)))
    