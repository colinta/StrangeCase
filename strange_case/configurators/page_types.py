import os
from fnmatch import fnmatch

from strange_case.configurators import provides


@provides('page_type')
def page_types(source_file, config):
    types = list(config.get('page_types', []))

    file_name = os.path.basename(source_file)
    for node_type, globs in types:
        if isinstance(globs, str):
            globs = [globs]
        for pattern in globs:
            if fnmatch(file_name, pattern):
                config['page_type'] = node_type
                return config
    if not config.get('default_page_type'):
        return None
    config['page_type'] = config['default_page_type']
    return config

page_types.defaults = {
    'page_types': [
        ('jinja', ('*.j2', '*.jinja2', '*.jinja', '*.txt', '*.html', '*.xml')),
        ('plywood', ('*.ply', '*.plywood', '*.xply')),
    ],
    'default_page_type': 'jinja',
}

page_types.dont_inherit = [
    'page_type'
]
