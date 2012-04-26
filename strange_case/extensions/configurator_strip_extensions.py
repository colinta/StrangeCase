

def strip_extension(source_file, config):
    for extension in config.get('strip_extensions', ['.html', '.xml']):
        if config['url'].endswith(extension):
            config['url'] = config['url'].rstrip(extension)
            break
    return config
