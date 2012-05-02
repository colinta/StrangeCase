from functools import wraps

from strange_case.registry import Registry


def provides(conf):
    def decorator(function):
        @wraps(function)
        def wrapper(source_file, config):
            if conf not in config:
                return function(source_file, config)
            return config
        return wrapper
    return decorator


def is_index(conf):
    return conf['target_name'] == conf.get('index.html', 'index.html')


def configurate(source_file, config):
    verbose = config.get('verbose')
    configurators = Registry.configurators
    # Run the config through each configurator.
    # If a configurator returns a falsey
    # value, the node will be ignored.
    for configurator in configurators:
        config = configurator(source_file, config)
        if not config:
            if verbose:
                print 'Ignoring "{}" due to configurator {}'.format(source_file, configurator.__name__)
            return
    return config


def meta_before(source_file, config):
    configurators = Registry.configurators
    for configurator in configurators:
        if hasattr(configurator, 'defaults'):
            for key, value in configurator.defaults.iteritems():
                if key not in config:
                    config[key] = value

        if hasattr(configurator, 'dont_inherit'):
            for dont_inherit in configurator.dont_inherit:
                if dont_inherit not in config:
                    config['dont_inherit'].append(dont_inherit)

        if hasattr(configurator, 'require_before'):
            for required in configurator.require_before:
                if required not in config:
                    raise TypeError('Missing required config["{required}"] '
                        'from {configurator.__name__}.require_before'.format(**locals()))
    return config

meta_before.defaults = {
    'dont_inherit': [],
}


def meta_after(source_file, config):
    configurators = Registry.configurators
    for configurator in configurators:
        if hasattr(configurator, 'require_after'):
            for required in configurator.require_after:
                if required not in config:
                    raise TypeError('Missing required config["{required}"] '
                        'from {configurator.__name__}.require_after'.format(**locals()))
    return config


from file_types import file_types
from folder_config_file import folder_config_file
from front_matter_config import front_matter_config
from ignore import ignore
from merge_files_config import merge_files_config
from setdefault_name import setdefault_name
from setdefault_target_name import setdefault_target_name
from set_url import set_url
from setdefault_iterable import setdefault_iterable
from skip_if_not_modified import skip_if_not_modified
