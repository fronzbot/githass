'''
Reads a ban list assuming the following structure:

[Month] [Day] [HH:MM:SS] [iptable] [Type=Ban/Unban] [ipAddress]

'''

import sys
import json

FILE = sys.argv[1]
JSON_FILE = sys.argv[2]

DATA = {'ssh': [], 'hassiptables': []}

''' Read file '''
with open(FILE) as fh:
  banlist = fh.readlines()

''' Get Banned IPs '''
for line in banlist:
  line_split = line.split(' ')
  ban_type = ''.join(line_split[3].split('-'))
  ban_ip = line_split[5].strip()
  if ban_type not in DATA.keys() and line_split[4] == 'Ban':
    DATA[ban_type] = list()
  if ban_ip in DATA[ban_type] and line_split[4] == 'Unban':
    DATA[ban_type].remove(ban_ip)
  else:
    DATA[ban_type].append(ban_ip)

''' Replace empty ban list with "None" '''
for key, value in DATA.items():
    if not value:
        DATA[key] = "None"
    else:
        DATA[key] = ','.join(value)

''' Write to JSON file for HASS processing '''
with open(JSON_FILE, 'w') as fp:
    json.dump(DATA, fp)
