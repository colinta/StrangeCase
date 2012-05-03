import urllib

from strange_case.configurators import is_index


def set_url(source_file, config):
    if is_index(config):
        config['url'] = ''
    else:
        config['url'] = urllib.quote(config['target_name'])
    return config

set_url.defaults = {}
set_url.defaults.update(is_index.defaults)

set_url.require_before = ['root_url']
set_url.require_after = ['url']
