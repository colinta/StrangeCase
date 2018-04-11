import urllib.parse


def set_url(source_file, config):
    if config['is_index']:
        config['url'] = ''
    else:
        config['url'] = urllib.parse.quote(config['target_name'])
    return config


def on_start(config):
    root_url = config.get('root_url', '/')
    if not root_url.endswith('/'):
        root_url += '/'
    if not root_url.startswith('/'):
        root_url = '/' + root_url
    config['root_url'] = root_url

set_url.require_before = ['root_url']
set_url.require_after = ['url']
set_url.on_start = on_start

set_url.dont_inherit = [
    'url'
]
