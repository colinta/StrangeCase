from strange_case.configurators import provides


@provides('url')
def strip_extensions(source_file, config):
    for extension in config.get('strip_extensions', ['.html', '.xml']):
        if config['target_name'].endswith(extension):
            config['url'] = config['target_name'].rstrip(extension)
            break
    return config
