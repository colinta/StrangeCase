import urllib


def strip_extensions(source_file, config):
    if 'url' not in config:
        config['url'] = urllib.quote(config['target_name'])

    for extension in config.get('strip_extensions', ['.html', '.xml']):
        if config['url'].endswith(extension):
            config['url'] = config['url'].rstrip(extension)
            break
    return config
