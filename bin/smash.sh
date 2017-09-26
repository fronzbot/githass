#!/bin/bash
python3 smash.py --source automation/ --dest automations.yaml --ext yaml --use-ids --force-overwrite
python3 smash.py --source scripts/ --dest scripts.yaml --ext yaml --force-overwrite
python3 smash.py --source customize/ --dest customize.yaml --ext yaml --force-overwrite
if [[ $* == *--travis* ]]; then
	echo "Using travis flag, skipping chown"
else
	sudo chown hass /home/hass/.homeassistant/automations.yaml
	sudo chown hass /home/hass/.homeassistant/scripts.yaml
	sudo chown hass /home/hass/.homeassistant/customize.yaml
fi
