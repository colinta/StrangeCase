import urllib


def set_url(source_file, config):
    if config['is_index']:
        config['url'] = ''
    else:
        config['url'] = urllib.quote(config['target_name'])
    return config

set_url.require_before = ['root_url']
set_url.require_after = ['url']

set_url.dont_inherit = [
    'url'
]
