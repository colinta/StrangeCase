import os
from fnmatch import fnmatch


def ignore(source_file, config):
    file_name = os.path.basename(source_file)

    if config['ignore'] is True or \
            config['ignore'] and any(pattern for pattern in config['ignore'] if fnmatch(file_name, pattern)):
        return
    return config


ignore.defaults = {
    'ignore': [
        u'.*',
        u'config.yaml',
    ],
}
