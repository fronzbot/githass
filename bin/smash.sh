#!/bin/bash
python3 smash.py --source automation/ --dest automations.yaml --ext yaml --use-ids --force-overwrite
python3 smash.py --source scripts/ --dest scripts.yaml --ext yaml --force-overwrite
python3 smash.py --source customize/ --dest customize.yaml --ext yaml --force-overwrite

