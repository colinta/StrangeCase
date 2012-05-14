

def override(source_file, config):
    for key, value in config['override'].iteritems():
        if key not in config:
            config[key] = value
    return config


override.defaults = {
    'override': {}
}
