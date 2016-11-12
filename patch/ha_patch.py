#================================================================
# ha_patch.py
# Author: Kevin Fronczak
# Date: November 12, 2016
# Desc: Performs custom patches to home-assistant files
#================================================================

import os
import sys
import shutil
import difflib
import re
import fileinput
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read(os.path.dirname(os.path.abspath(__file__))+'/patch.ini')

def main():
  filenames = Config.sections()[1:]
  
  #-------------------------------------
  # Set homeassistant directory
  #-------------------------------------
  try:
    hadir = ConfigSectionMap("Setup")['hass'] + 'patch/refs/'
  except:
    raise KeyError("Exception on 'hass' option")
  
  if not os.path.isdir(hadir):
    raise OSError('Home Assistant Path Incorrectly Configured: '+hadir)   
  
    #-------------------------------------
    # Walk through each file and perform patch
    #-------------------------------------
  for file in filenames:
    # Create full path names
    dir         = ConfigSectionMap(file)['dir']
    find        = ConfigSectionMap(file)['find']
    replace     = ConfigSectionMap(file)['replace']
    
    source_file = dir   + file
    ref_file    = hadir + file
    
    # Copy source file if reference doesn't exist
    if not os.path.isfile(ref_file):
      shutil.copy(source_file, ref_file)
    
    # Diff the source and ref files
    line_diffs = []
    with open(source_file, 'r') as src:
      with open(ref_file, 'r') as ref:
        diff = difflib.unified_diff(src.readlines(), ref.readlines(), fromfile=ref, tofile=src, lineterm='\n', n=0)    
        for line in diff:
          line_diffs.append(line)
    
    # Check if differences found.  If there are, prompt user before continuing
    if not line_diffs:
      print('No Differences Found in '+file)
      choice = True
    else:
      for line in line_diffs:
        sys.stdout.write(line)
        
      choice = query_yes_no('Differences found, continue with patch for '+file+'?', default="yes")
      
    if(choice):
      shutil.copy(source_file, ref_file)
      perform_patch(file, dir, find, replace)
    else:
      print('Exited without patching\n')
    
def perform_patch(file, dir, find, replace):
  src = dir + file
  f = open(src, 'r')
  filedata = f.read()
  f.close()

  newdata = filedata.replace(find, replace)

  f = open(src,'w')
  f.write(newdata)
  f.close()
  print(file + ' patched!')

def ConfigSectionMap(section):
  # From: https://wiki.python.org/moin/ConfigParserExamples
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1   
    
def query_yes_no(question, default="yes"):
  # From: http://code.activestate.com/recipes/577058/
  """Ask a yes/no question via raw_input() and return their answer.

  "question" is a string that is presented to the user.
  "default" is the presumed answer if the user just hits <Enter>.
      It must be "yes" (the default), "no" or None (meaning
      an answer is required of the user).
  The "answer" return value is True for "yes" or False for "no".
  """
  valid = {"yes": True, "y": True, "ye": True,
           "no": False, "n": False}
  if default is None:
      prompt = " [y/n] "
  elif default == "yes":
      prompt = " [Y/n] "
  elif default == "no":
      prompt = " [y/N] "
  else:
      raise ValueError("invalid default answer: '%s'" % default)

  while True:
      sys.stdout.write(question + prompt)
      choice = raw_input().lower()
      if default is not None and choice == '':
          return valid[default]
      elif choice in valid:
          return valid[choice]
      else:
          sys.stdout.write("Please respond with 'yes' or 'no' "
                           "(or 'y' or 'n').\n")
    
if __name__ == "__main__":
  main()