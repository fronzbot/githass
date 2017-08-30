'''
Name: smash.py
Author: Kevin Fronczak
Date: August 29, 2017

Usage:
    python3 smash.py --source <directory> --dest <destination> [opts]

Use --help flag to see available options.
    
Description:
    Parses a directory and merges contents of each file into a destination file.
    If the destination already exists, it is diff'd against the new contents and
    merged if possible.  If not, a manual edit is needed (with offending lines
    highlighted in terminal).
'''

from os import listdir, getcwd
from os.path import isfile, join
from datetime import datetime
import sys
import argparse
import difflib

class Smasher(object):
    '''Class that creates a generic smashing object.'''

    def __init__(self, args):
        '''Instantiates class.'''
        self.opts = self.get_options(args)
        self.src  = self.opts['source']
        if self.src.endswith('/'):
            self.src = self.src[:-1]
        self.dest = self.opts['dest']
        self.color = ColorLog()

    def get_options(self, args):
        '''Returns dictionary of command line arguments.'''
        opts = dict()
        for arg in vars(args):
            opts[arg] = getattr(args, arg)

        return opts

    def begin(self):
        '''Start smashing routine.'''
        file_lines = list()
        for line in self.lines_file_top():
            file_lines.append(line)
        for line in self.get_source_contents():
            file_lines.append(line)
        if self.diff_with_destination(file_lines):
            self.write_source(self.dest, file_lines)
            sys.exit(0)
        else:
            self.color.colorize('Smash aborted.  Manually merge files and run again.', 'red')
            sys.exit(1)

    def diff_with_destination(self, lines):
        '''Check if destination exists, if it does, diff files.'''
        if isfile(self.dest) and not self.opts['force_overwrite']:
            tempfile = self.dest + ' NEW'
            with open(self.dest) as f:
                content = f.readlines()
            # Perform diff
            diff_lines = list()
            for line in difflib.unified_diff(content, lines, fromfile=self.dest, tofile=tempfile, lineterm='\n'):
                if line.startswith('-'):
                    color_line = self.color.colorize(line, 'red')
                elif line.startswith('+'):
                    color_line = self.color.colorize(line, 'green')
                else:
                    color_line = self.color.colorize(line, 'white')
                
                diff_lines.append(line)
                print(color_line)
            
            return self.continue_prompt()
        else:
            return True
            

    def write_source(self, file, lines):
        '''Writes lines to file.'''
        with open(file, mode='w') as f:
            f.write(''.join(lines))

    def continue_prompt(self):
        '''Prompt to determine is smash should continue or abort.'''
        prompt = self.color.colorize('File differences found!\nContinue with smash anyways? y/n:\n', 'yellow')
        response = input(prompt)
        print(self.color.colors['reset'])
        if response.lower() in ['y', 'yes']:
            return True
        else:
            return False
            
    def lines_file_top(self):
        '''String to append to top of file.'''
        top_lines = list()
        if not self.opts['no_comment']:
            comment = self.opts['comment']
            top_lines.append('{}---------------- SMASH.PY ------------------\n'.format(comment))
            if not self.opts['no_date']:
                date_string = 'Generated: {:%Y-%b-%d %H:%M:%S}'.format(datetime.now())
                top_lines.append('{} {} \n'.format(comment, date_string))
            top_lines.append('{}--------------------------------------------\n'.format(comment))
        return top_lines

    def get_source_contents(self):
        '''Retrieves source file contents.'''
        lines = list()
        files = list()
        for file in listdir(self.src):
            if file.endswith(self.opts['ext']) and file not in self.opts['exclude']:
                files.append(file)

        for filename in files:
            full_file = '{}/{}'.format(self.src, filename)

            with open(full_file) as f:
                content = f.readlines()
        
            if not self.opts['no_comment']:
                lines.append('\n{}--- {} ---\n'.format(self.opts['comment'], full_file))
    
            for line in content:
                # Add newline if missing
                if not line.endswith('\n'):
                    line = line + '\n'
                # Just copy comments over directly
                if line.startswith(self.opts['comment']):
                    lines.append(line)
    
                # Check alias line and use as id
                elif self.opts['use_ids'] and line.startswith('alias:'):
                    clean_line = line
                    clean_line = clean_line.replace('alias: ', "")
                    clean_line = clean_line.replace(" ", "_")
                    clean_line = clean_line.replace("/", "_")
                    clean_line = clean_line.replace("-", "_")
                    id_line = '- id: ' + clean_line.lower()
                    lines.append(id_line)
                    lines.append('  ' + line)
                else:
                    lines.append('  ' + line)

        return lines
            
class Parser(object):
    '''Argument parsing object.'''

    def __init__(self):
        '''Initialize arguments for parser.'''
        self.parser = argparse.ArgumentParser(__name__)
        self.parser.add_argument('--source', help='Source directory of files to be smashed',
                                 type=str, required=True)
        self.parser.add_argument('--dest', help='Destination file for smashing',
                                 type=str, required=True)
        self.parser.add_argument('--ext', help='Extension of files to smash',
                                 type=str, required=False, default='yaml')
        self.parser.add_argument('--exclude', help='Space seperated list of files to exclude from smashing',
                                 nargs='+', required=False, default=[])
        self.parser.add_argument('--comment', help='Comment flag for file (default is "#")',
                                 type=str, required=False, default='#')
        self.parser.add_argument('--no-date', help='Do not append date to contents of destination file',
                                 action='store_true')
        self.parser.add_argument('--no-comment', help='Do not add additional comments to contents of destination file',
                                 action='store_true')
        self.parser.add_argument('--force-overwrite', help='Do not attempt a file merge, overwrite the destination file',
                                 action='store_true')
        self.parser.add_argument('--use-ids', help='Adds an "id" line to file (used for home assistant automations)',
                                 action='store_true')
                            
        self.args = self.parser.parse_args()

class ColorLog(object):
    '''Class to colorize log output'''

    def __init__(self):
        from colorama import init, Fore, Style
       
        init(autoreset=True)
        self.colors = {'red': Fore.RED,
                       'yellow': Fore.YELLOW,
                       'green': Fore.GREEN,
                       'white': Fore.WHITE,
                       'cyan': Fore.CYAN,
                       'reset': Style.RESET_ALL
                      }

    def colorize(self, string, type):
        try:
            return (self.colors[type] + string)
        except KeyError:
            print('Unkown key {}'.format(type))
            sys.exit(1)

if __name__ == '__main__':
    p = Parser()
    smash = Smasher(p.args)
    smash.begin()
