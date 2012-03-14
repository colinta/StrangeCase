import os
import yaml

from configurators import *


CONFIG = {}
# first the lowest-level configs are merged with these defaults.
defaults = {
    'project_path': os.getcwd(),
    'site_path': u'site/',
    'deploy_path': u'public/',
    'remove_stale_files': True,
    'dont_remove': ['.*'],
    'config_file': u'config.yaml',
    'html_extension': u'.html',

    ##|  HOOKS
    'config_hook': None,

    ##|  EXTENSIONS
    'extensions': [],
    'filters': {},
    'processors': [],
    'configurators': [
        # most of these configurators are *very*
        # important, so if you're gonna go messing
        # with them, be warned.
        file_types,
        merge_files_config,
        setdefault_name,
        setdefault_target_name,
        folder_config_file,
        front_matter_config,
        ignore,
        date_from_name,
        order_from_name,
        date_from_name,  # yup, try again!
        title_from_name,
    ],
}
defaults.update(CONFIG)
CONFIG.update(defaults)

# this can change per folder, but please don't, that's just weird.
html_ext = CONFIG['html_extension']

more_defaults = {
    'host': 'http://localhost:8000',
    'index': 'index' + html_ext,
    'rename_extensions': {
        '.j2': html_ext,
        '.jinja2': html_ext,
    },
    'ignore': [
        '.*',
        CONFIG['config_file'],
    ],
    'dont_inherit': [
        'type',
        'name',
        'target_name',
        'title',
        'created_at',
        'order',
    ],
    'file_types': [
        ('page', ('*.j2', '*.jinja2', '*.html', '*.txt', '*.md')),
        ('asset', ('*')),
    ]
}
more_defaults.update(CONFIG)
CONFIG.update(more_defaults)

# normalize paths
for conf in ['project_path', 'site_path', 'deploy_path']:
    if CONFIG[conf][0] == '~':
        CONFIG[conf] = os.path.expanduser(CONFIG[conf])
    elif CONFIG[conf][0] == '.':
        CONFIG[conf] = os.path.abspath(CONFIG[conf])

# now we can look for the app config
config_path = os.path.join(CONFIG['project_path'], CONFIG['config_file'])

if os.path.isfile(config_path):
    with open(config_path, 'r') as config_file:
        yaml_config = yaml.load(config_file)
    if yaml_config:
        CONFIG.update(yaml_config)
