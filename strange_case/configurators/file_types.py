import os
from fnmatch import fnmatch

from strange_case.configurators import provides
from strange_case.registry import Registry


@provides('type')
def file_types(source_file, config):
    if os.path.isdir(source_file):
        if source_file == config['site_path']:
            config['type'] = config['default_root_type']
        else:
            config['type'] = config['default_folder_type']
        return config
    else:
        types = list(config.get('file_types', []))
        # built-in file_types
        for entry in Registry.file_types:
            types.append(entry)

        file_name = os.path.basename(source_file)
        for node_type, globs in types:
            if isinstance(globs, str):
                globs = [globs]
            for pattern in globs:
                if fnmatch(file_name, pattern):
                    config['type'] = node_type
                    return config
        if not config.get('default_type'):
            return None
        config['type'] = config['default_type']
        return config

file_types.defaults = {
    'file_types': [
        ('page', ('*.j2', '*.jinja2', '*.jinja', '*.txt', '*.html', '*.xml', '*.ply', '*.plywood', '*.xply')),
    ],
    'default_type': 'asset',
    'default_root_type': 'root',
    'default_folder_type': 'folder',
}

file_types.require_after = [
    'type',
]

file_types.dont_inherit = [
    'type'
]
