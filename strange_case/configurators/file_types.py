import os
from fnmatch import fnmatch

from strange_case.configurators import provides


@provides('type')
def file_types(source_file, config):
    if os.path.isdir(source_file):
        config['type'] = 'folder'
        return config
    else:
        file_name = os.path.basename(source_file)
        for node_type, globs in config.get('file_types', []):
            if isinstance(globs, basestring):
                globs = [globs]
            for pattern in globs:
                if fnmatch(file_name, pattern):
                    config['type'] = node_type
                    return config
        if not config.get('default_type', None):
            return None
        config['type'] = config['default_type']
        return config
