from strange_case.configurators import provides


@provides('iterable')
def setdefault_iterable(source_file, config):
    config['iterable'] = not config['is_index']
    return config
