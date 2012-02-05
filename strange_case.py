import os
from registry import Registry
from processors import *


def strange_case(config):
    # pull out important values.
    # these are not going to change after this point
    site_path = config['site_path']
    deploy_path = config['deploy_path']

    # look for files in content/
    if not os.path.isdir(site_path):
        raise IOError("Could not find site_path folder \"%s\"" % site_path)

    root_node = Registry.node('root', config, site_path, deploy_path)[0]

    root_node.generate()


if __name__ == '__main__':
    # so that strange_case.py can be executed from any project folder, add CWD to the import paths
    import sys
    sys.path.append(os.getcwd())

    CONFIG = None
    try:
        from config import CONFIG
    except ImportError:
        if not CONFIG:
            from strange_case_config import CONFIG

    from support.jinja import StrangeCaseEnvironment

    extensions = []
    if 'extensions' in CONFIG:
        for extension in CONFIG['extensions']:
            if isinstance(extension, basestring):
                imp, frm = extension.rsplit('.', 1)
                ext = __import__(imp, globals(), locals(), [frm], -1)
                extension = getattr(ext, frm)
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
                imp, frm = method.rsplit('.', 1)
                ext = __import__(imp, globals(), locals(), [frm], -1)
                method = getattr(ext, frm)
            jinja_environment.filters[filter_name] = method
        del CONFIG['filters']

    if 'processors' in CONFIG:
        for processor in CONFIG['processors']:
            __import__(processor)
        del CONFIG['processors']

    strange_case(CONFIG)
