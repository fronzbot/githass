'''
Name: gen_automations.py
Author: Kevin Fronczak
Date: July 1, 2017

Desc:
This file parses the automations directory within a home-assitant installation
and merges the files into an automations.yaml file.  If the automations.yaml
file already exists, the existing file is merged with the generated file.
This allows for the old automation style to be maintained, which is far easier
to maintain than the new single-file style.
'''
from os import listdir, getcwd
from os.path import isfile, join
from datetime import datetime

DEFPATH = getcwd()
AUTOPATH = DEFPATH + '/automation'

# Forces overwrite of automations.yaml
# DO NOT USE IF YOU USE THE AUTOMATION CONTROL PANEL!!
FORCE_OVERWRITE = True

# Need to get all the files first
files = [f for f in listdir(AUTOPATH) if isfile(join(AUTOPATH, f))]

# Now we can iterate over each file
all_lines = list()
all_lines.append('# -------------------------------------------\n')
all_lines.append('# FILE GENERATED USING gen_automations SCRIPT\n')
all_lines.append('# GENERATED ON {:%Y-%b-%d %H:%M:%S}\n'.format(datetime.now()))
all_lines.append('# -------------------------------------------\n\n')


for filename in files:
    with open(AUTOPATH + '/' + filename) as f:
        content = f.readlines()
    
    for line in content:
        # Add newline if missing
        if not line.endswith('\n'):
            line = line + '\n'
        # Just copy comments over directly
        if line.startswith('#'):
            all_lines.append(line)
        # Check alias line and use as id
        elif line.startswith('alias:'):
            clean_line = line
            clean_line = clean_line.replace('alias: ', "")
            clean_line = clean_line.replace(" ", "_")
            clean_line = clean_line.replace("/", "_")
            clean_line = clean_line.replace("-", "_")
            id_line = '- id: ' + clean_line.lower()
            all_lines.append(id_line)
            all_lines.append('  ' + line)
        else:
            all_lines.append('  ' + line)

# Check if automations.yaml exists, if it does, just pipe it to 
# a temp file and tell the user they need to manually merge
if isfile(DEFPATH + '/automations.yaml') and not FORCE_OVERWRITE:
    new_file = DEFPATH + '/automations_temp.yaml'
    print("automations.yaml already Exists!")
    print("Sending to automations_temp.yaml")
    print("REQUIRES MANUAL MERGE!!")
else:
    new_file = DEFPATH + '/automations.yaml'

with open(new_file, mode='w') as f:
    f.write(''.join(all_lines))

