from strange_case.configurators.set_url import set_url
from strange_case.registry import Registry


def strip_extensions(source_file, config):
    for extension in config['strip_extensions']:
        if config['url'].endswith(extension):
            config['url'] = config['url'][:-len(extension)]
            break
    return config


def on_start(config):
    # move strip_extensions configurator to after set_url
    Registry.configurators.remove(strip_extensions)
    my_index = Registry.configurators.index(set_url)
    Registry.configurators.insert(my_index + 1, strip_extensions)


strip_extensions.on_start = on_start

strip_extensions.defaults = {
    'strip_extensions': ['.html', '.xml']
}
