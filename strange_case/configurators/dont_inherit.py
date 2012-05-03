

def dont_inherit(source_file, config):
    for key in config['dont_inherit']:
        try:
            del config[key]
        except AttributeError:
            pass
    return config


dont_inherit.defaults = {
    'dont_inherit': [
        'type',
        'name',
        'target_name',
        'title',
        'created_at',
        'order',
        'iterable',
        'url',
        'skip',
    ],
}
