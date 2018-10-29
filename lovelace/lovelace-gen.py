"""Generates lovelace config from multiple files."""
import os
import sys

try:
    import yaml
except ImportError:
    import pip
    if hasattr(pip, 'main'):
        pip.main(['install', pyyaml])
    else:
        pip._internal.main(['install', pyyaml])
    import yaml

DEFAULT_TITLE = "Home Assistant"
LOVELACE_FILE = 'ui-lovelace.yaml'
LOVELACE_DIR = 'lovelace'
CONFIG = {'title': DEFAULT_TITLE, 'views': []}


def get_files(directory):
    """Get all files in directory."""
    yaml_files = []
    all_files = os.listdir(directory)
    for filename in all_files:
        full_path = os.path.join(directory, filename)
        if os.path.isfile(full_path):
            if full_path.endswith(".yaml"):
                yaml_files.append(full_path)
    return yaml_files


def merge_config(files):
    """Merge all files into a config."""
    configs = []
    for yaml_file in files:
        with open(yaml_file, 'r') as openfile:
            configs.append(yaml.load(openfile))

    CONFIG['views'] = configs

    return CONFIG


def write_to_config(config, config_path='/config'):
    """Write the config to main lovelace file."""
    config_file = os.path.join(config_path, LOVELACE_FILE)
    with open(config_file, 'w') as outfile:
        yaml.dump(config, outfile)


if __name__ == '__main__':
    config_path = '/config'
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    lovelace_path = os.path.join(config_path, LOVELACE_DIR)
    files = get_files(lovelace_path)
    config = merge_config(files)
    write_to_config(config, config_path=config_path)
    print("Done.")
