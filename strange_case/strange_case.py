import os
from registry import Registry
from processors import *


def strange_case(config):
    # pull out important values.
    site_path = config['site_path']
    deploy_path = config['deploy_path']

    # look for files in content/
    if not os.path.isdir(site_path):
        raise IOError("Could not find site_path folder \"%s\"" % site_path)

    # this is the one folder that *doesn't* get processed by processers.build_page_tree,
    # so it needs special handling here.
    # config_path = os.path.join(deploy_path, config['config_file'])
    # config.update(check_for_config(config_path))
    config.setdefault('type', 'root')
    root_node = build_node(config, site_path, deploy_path, '')[0]

    # root_node = Registry.nodes('root', config, site_path, deploy_path)[0]

    root_node.generate()


def fancy_import(name):
    """
    This takes a fully qualified object name, like
    'extensions.Markdown2.markdown', and returns the last
    object.  equivalent to `from extensions.Markdown2 import markdown`.
    """

    import_path, import_me = name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)


if __name__ == '__main__':
    # so that strange_case.py can be executed from any project folder, add CWD to the import paths
    import sys
    sys.path.insert(0, os.getcwd())

    CONFIG = None
    if os.path.isfile(os.path.join(os.getcwd(), 'config.py')):
        from config import CONFIG
    else:
        from strange_case_config import CONFIG

    from support.jinja import StrangeCaseEnvironment

    extensions = []
    if 'extensions' in CONFIG:
        for extension in CONFIG['extensions']:
            if isinstance(extension, basestring):
                extension = fancy_import(extension)
            extensions.append(extension)
        del CONFIG['extensions']

    if not Registry.get('jinja_environment', None):
        jinja_environment = StrangeCaseEnvironment(extensions=extensions)
        Registry.set('jinja_environment', jinja_environment)
    else:
        jinja_environment = Registry.get('jinja_environment')

    if 'filters' in CONFIG:
        for filter_name, method in CONFIG['filters'].iteritems():
            if isinstance(method, basestring):
                method = fancy_import(method)
            jinja_environment.filters[filter_name] = method
        del CONFIG['filters']

    if 'processors' in CONFIG:
        for processor in CONFIG['processors']:
            __import__(processor)
        del CONFIG['processors']

    configurators = []
    if 'configurators' in CONFIG:
        for configurator in CONFIG['configurators']:
            if isinstance(configurator, basestring):
                configurator = fancy_import(configurator)
            configurators.append(configurator)
            Registry.add_configurator(configurator)
        del CONFIG['configurators']

    # additional configurators, in addition to the all-important defaults
    if 'configurators +' in CONFIG:
        for configurator in CONFIG['configurators +']:
            if isinstance(configurator, basestring):
                configurator = fancy_import(configurator)
            configurators.append(configurator)
            Registry.add_configurator(configurator)
        del CONFIG['configurators']

    strange_case(CONFIG)
