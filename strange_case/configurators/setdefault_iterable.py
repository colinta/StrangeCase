from strange_case.configurators import provides, is_index


@provides('iterable')
def setdefault_iterable(source_file, config):
    config['iterable'] = not is_index(config)
    return config
