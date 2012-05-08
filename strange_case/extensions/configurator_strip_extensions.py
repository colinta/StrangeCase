from strange_case.configurators.set_url import set_url
from strange_case.registry import Registry


def strip_extensions(source_file, config):
    for extension in config.get('strip_extensions', ['.html', '.xml']):
        if config['url'].endswith(extension):
            config['url'] = config['url'].rstrip(extension)
            break
    return config


def on_start(config):
    # move set_url configurator to *just* before strip_extensions
    Registry.configurators.remove(set_url)
    my_index = Registry.configurators.index(strip_extensions)
    Registry.configurators.insert(my_index, set_url)
    return config


strip_extensions.on_start = on_start
