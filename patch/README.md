# ha_patch.py
## Custom patching utility for homeassistant

This directory contains a python script that will patch certain files to provide
behavior that I want (and is probably not a good idea to push to everyone)

### Usage
To run, navigate to ```<HA INSTALL DIR>/patch``` and type
```sudo python ha_patch.py```
on the commandline.  

It is recommended to add the following to your .bash_aliases file (or whatever you use)
and then run the alias after upgrading homeassistant
```alias ha_patch='sudo python <HA INSTALL DIR>/patch/ha_patch.py```

In order to work correctly, the patch.ini file must be setup with the following information, where anything in curly braces is optional:

```
[Setup]
hass: <HA INSTALL DIR>

[filename1.py]
dir: <DIR FOR FILENAME1>
{find}: <TEXT TO REPLACE>
{replace}: <NEW TEXT>
{file}: <PATCHED FILE TO COPY>

[filename2.py]
dir: ...
...
```

### Example patch.ini
```
[Setup]
hass: /home/hass/.homeassistant/

[nmap_tracker.py]
dir: /srv/hass/hass_venv/lib/python3.4/site-packages/homeassistant/components/device_tracker/
find: options = '-F --host-timeout 5s '
replace: options = '-sS --privileged --host-timeout 5s '
```

### What the script does
The first time this script is run, it will create a directory that contains the original contents
of each python file in the patch.ini configuration file.  This serves as reference points to determine if 
it's safe to make a change or if it requires more user interaction.  After an upgrade, run the script and it 
will diff the new file with the saved copy to determine any differences.  If there are none, it will peform 
the find and replace indicated in the patch.ini file if the 'find' and 'replace' properties are defined.  Otherwise,
the script will copy the file given by the file property.  Note that the file MUST be located within the 'hass' directory
otherwise the copy will fail.  If there ARE differences, the script will notify the user and display the differences.  
The user can either then continue with the find/replace action, or postpone it to rectify the differences and 
determine if any changes need to be made.  The new file is only copied over if changes are accepted (and the file 
is copied BEFORE changes are made in order to serve as a fresh reference point for future homeassistant versions)


