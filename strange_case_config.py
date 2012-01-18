import yaml
import os

##|                                               |##
##|  Don't extend or mess with any of this stuff  |##
##|  -------------------------------------------  |##
##|    this used to be in strange_case.py, but    |##
##|     that file was getting fat and bloated     |##
##|                                               |##

CONFIG = None
try:
    from config import CONFIG
except ImportError:
    if not CONFIG:
        CONFIG = {}

# first the lowest-level configs are merged with these defaults.
default_config = {
    'project_path': os.getcwd(),
    'site_path': u'site/',
    'deploy_path': u'public/',
    'config_file': u'config.yaml',
    'html_extension': u'.html',
}
default_config.update(CONFIG)
CONFIG = default_config

# this can only be set in config.py (config.yaml is expected to be in this folder)
PROJECT_PATH = CONFIG['project_path']

# this can change per folder
html_ext = CONFIG['html_extension']

more_defaults = {
    'host': 'http://localhost:8000',
    'index': 'index' + html_ext,
    'rename_extensions': {
        '.md': html_ext,
        '.j2': html_ext,
        '.jinja2': html_ext,
    },
    'ignore': [
        '.*',
        CONFIG['config_file']
    ],
    'dont_process': [
        '*.js', '*.css',
    ],
}
more_defaults.update(CONFIG)
CONFIG = more_defaults

# we should now know
config_path = os.path.join(PROJECT_PATH, CONFIG['config_file'])

with open(config_path, 'r') as config_file:
    yaml_config = yaml.load(config_file)
if yaml_config:
    CONFIG.update(yaml_config)
