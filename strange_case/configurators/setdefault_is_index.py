from strange_case.configurators import provides


@provides('is_index')
def setdefault_is_index(source_file, config):
    config['is_index'] = False
    if config['target_name'] == config['index.html']:
        config['is_index'] = True
    return config
