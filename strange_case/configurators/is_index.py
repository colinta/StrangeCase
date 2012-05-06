from strange_case.configurators import provides


@provides('is_index')
def is_index(source_file, config):
    config['is_index'] = config['target_name'] == config['index.html']
    return config


is_index.defaults = {
    'index.html': 'index.html'
}

is_index.dont_inherit = [
    'is_index'
]
