import urllib

from strange_case.configurators import provides, is_index


@provides('url')
def setdefault_url(source_file, config):
    if is_index(config):
        config['url'] = ''
    else:
        config['url'] = urllib.quote(config['target_name'])
    return config
