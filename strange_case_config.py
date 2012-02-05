import yaml
import os


# first the lowest-level configs are merged with these defaults.
CONFIG = {
    'project_path': os.getcwd(),
    'site_path': u'site/',
    'deploy_path': u'public/',
    'config_file': u'config.yaml',
    'html_extension': u'.html',
    'extensions': [],
    'filters': {},
    'processors': [],
}

# this can change per folder, but please don't, that's just weird.
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

# now we can look for the app config
config_path = os.path.join(CONFIG['project_path'], CONFIG['config_file'])

with open(config_path, 'r') as config_file:
    yaml_config = yaml.load(config_file)
if yaml_config:
    CONFIG.update(yaml_config)
