# ha_patch.py
## Custom patching utility for homeassistant

This directory contains a python script that will patch certain files to provide
behavior that I want (and is probably not a good idea to push to everyone)

### Usage
To run, navigate to <homeassistant install directoy>/patch and type
- sudo python ha_patch.py
on the commandline.  

It is recommended to add the following to your .bash_aliases file (or whatever you use)
and then run the alias after upgrading homeassistant
- alias ha_patch='sudo python <homeassistant install directory>/patch/ha_patch.py'
In order to work correctly, the patch.ini file must be setup with the following information:

[Setup]
hass: <homeassistant install directory>

[filename1.py]
dir: <location of file>
find: <text to replace>
replace: <new text that will replace 'find'>

[filename2.py]
dir: ...
...

### Example patch.ini
[Setup]
hass: /home/hass/.homeassistant/

[nmap_tracker.py]
dir: /srv/hass/hass_venv/lib/python3.4/site-packages/homeassistant/components/device_tracker/
find: options = '-F --host-timeout 5s '
replace: options = '-sS --privileged --host-timeout 5s '


### What the script does
The first time this script it run, it will create a directory that contains the original contents
of each file listed below.  This serve as reference points to determine if it's safe to make a change
or if it requires more user interaction.  After an upgrade, run the script and it will diff the new file 
with the saved copy to determine any differences.  If there are none, it will peform the action described below.
If there ARE differences, the script will notify the user and display the differences (and also write
them to a log file).  The user can either then continue with the action described below, or postpone
it to rectify the differences and determine if any changes need to be made by the action.  In either
case, the new file will be copied over and used as the new reference file.


