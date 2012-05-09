from strange_case.configurators.set_url import set_url
from strange_case.registry import Registry


def strip_extensions(source_file, config):
    for extension in config.get('strip_extensions', ['.html', '.xml']):
        if config['url'].endswith(extension):
            config['url'] = config['url'].rstrip(extension)
            break
    return config


def on_start(config):
    # move strip_extensions configurator to after set_url
    Registry.configurators.remove(strip_extensions)
    my_index = Registry.configurators.index(set_url)
    Registry.configurators.insert(my_index + 1, strip_extensions)


strip_extensions.on_start = on_start
