import os

from strange_case.config_dict import ConfigDict
from strange_case.configurators import *

CONFIG = ConfigDict({
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
        setdefault_is_index,
        folder_config_file,
        front_matter_config,
        ignore,
        date_from_name,
        order_from_name,
        date_from_name,  # yup, try again!
        title_from_name,
    ],
    'dont_inherit': [
        'type',
        'name',
        'target_name',
        'title',
        'created_at',
        'order',
        'is_index',
    ],
    'file_types': [
        ('page', ('*.j2', '*.jinja2', '*.jinja', '*.md', '*.html', '*.txt')),
    ],
    'default_type': 'asset',
    'host': u'http://localhost:8000',
    'index.html': u'index.html',
    'rename_extensions': {
        '.j2': u'.html',
        '.jinja2': u'.html',
        '.jinja': u'.html',
        '.md': u'.html',
    },
    'ignore': [
        u'.*',
        u'config.yaml',
    ],
})
