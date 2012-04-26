import os

from strange_case.configurators import provides


@provides('is_index')
def setdefault_is_index(source_file, config):
    ##|  ASSIGN DEFAULT NAME

    config['is_index'] = False
    if os.path.isfile(source_file):
        if config['target_name'] == config['index.html'] and hasattr(config, 'parent'):
            config['is_index'] = True
    return config
