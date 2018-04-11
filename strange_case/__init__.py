from fnmatch import fnmatch
import sys

from strange_case.registry import Registry
from strange_case.support import *
from strange_case.support.fancy_import import fancy_import
from strange_case.nodes import *
from strange_case.processors import *
from strange_case.nodes import Node


def require_package(pkg, reason=None):
    sys.stderr.write("\033[1m" + pkg + "\033[0m is required.\n  > pip install " + pkg + "\n")

    if reason:
        sys.stderr.write(reason + "\n")
    sys.exit(1)


def recommend_package(pkg, reason=None):
    sys.stderr.write("\033[1m" + pkg + "\033[0m is recommend.\n  > pip install " + pkg + "\n")

    if reason:
        sys.stderr.write(reason + "\n")


def find_files(folder):
    ret = []
    for f in os.listdir(folder):
        if f.startswith('.'):
            continue

        f = os.path.join(folder, f)
        ret.append(f)
        if os.path.isdir(f):
            ret.extend(find_files(f))
    return ret


def strange_case(config):
    # pull out important values.
    config['site_path'] = site_path = os.path.abspath(config['site_path'])
    config['deploy_path'] = deploy_path = os.path.abspath(config['deploy_path'])

    # check for site/ folder (required)
    if not os.path.isdir(site_path):
        raise IOError('Could not find site_path folder "%s"' % site_path)

    # create the public/ folder
    if not os.path.isdir(config['deploy_path']):
        os.mkdir(config['deploy_path'])

    from strange_case.support.jinja import StrangeCaseEnvironment
    from plywood import PlywoodEnv, PlywoodFunction

    ##|
    ##|  EXTENSIONS
    ##|  these are Jinja2 extensions that get loaded into the Environment object
    ##|
    extensions = []
    if 'extensions' in config:
        for extension in config['extensions']:
            if isinstance(extension, str):
                try:
                    extension = fancy_import(extension)
                except ImportError:
                    sys.stderr.write('Error in processors: Could not find "%s"\n' % extension)
                    raise
            extensions.append(extension)
        del config['extensions']

    if not Registry.get('jinja_environment'):
        jinja_environment = StrangeCaseEnvironment(extensions=extensions, project_path=config['project_path'])
        Registry.set('jinja_environment', jinja_environment)
    else:
        jinja_environment = Registry.get('jinja_environment')

    if not Registry.get('plywood_environment'):
        plywood_environment = PlywoodEnv()
        Registry.set('plywood_environment', plywood_environment)
    else:
        plywood_environment = Registry.get('plywood_environment')

    ##|
    ##|  FILTERS
    ##|  Jinja2 filter functions (`{{ var|filter }}`).  These are inserted into
    ##|  the Environment object's `filter` property.
    ##|
    if 'filters' in config:
        for filter_name, method in config['filters'].items():
            if isinstance(method, str):
                try:
                    method = fancy_import(method)
                except ImportError:
                    sys.stderr.write('Error in filters: Could not find "%s"\n' % method)
                    raise
            jinja_environment.filters[filter_name] = method
            if filter_name not in plywood_environment.scope:
                plywood_environment.scope[filter_name] = PlywoodFunction(method)
        del config['filters']

    ##|
    ##|  PROCESSORS
    ##|  A processors function registers itself using `Registry.register`, so
    ##|  all that is needed here is to load the module.
    ##|
    if 'processors' in config:
        for processor in config['processors']:
            try:
                fancy_import(processor)
            except ImportError:
                sys.stderr.write('Error in processors: Could not find "%s"\n' % processor)
                raise
        del config['processors']
    configurators = get_configurators(config)

    # register configurators - I broke this out into a separate function (below)
    Registry.reset_configurators()
    for configurator in configurators:
        Registry.add_configurator(configurator)

    # configurators can respond to the 'on_start' hook
    # skip_if_not_modified configurator uses this to read in the .timestamps
    # file, and strip_extensions makes sure that set_url is run before itself.
    for configurator in configurators:
        # configurators might be removed (?)
        if configurator in Registry.configurators:
            try:
                configurator.on_start(config)
            except AttributeError:
                pass

    # generic Registry hooks can listen for 'on_start'
    # category plugin uses this to reset when --watch is used
    Registry.trigger('on_start', config)

    # each node class should add files to these properties, so that watchdog and
    # stale-file-removal work.
    Node.files_written = []
    Node.files_tracked = []

    # create the list of existing files.  files that aren't generated will be
    # removed (unless dont_remove config is True)
    remove_stale_files = config['remove_stale_files']
    dont_remove = config['dont_remove']
    existing_files = []
    if os.path.isdir(deploy_path):
        existing_files = find_files(deploy_path)
    else:
        os.makedirs(deploy_path)

    # this is the one folder that *doesn't* get processed by
    # processors.build_page_tree - it needs special handling here.
    root_node = build_node(config, site_path, deploy_path, '')[0]
    Registry.set('root', root_node)
    root_node.generate()

    # configurators can respond to the 'on_finish' hook
    for configurator in Registry.configurators:
        try:
            configurators.on_finish(config)
        except AttributeError:
            pass

    if remove_stale_files and existing_files:
        paths = []
        for f in existing_files:
            if f not in Node.files_written:
                f = os.path.abspath(f)
                f_rel = os.path.relpath(f)
                if any(pattern for pattern in dont_remove if fnmatch(f, pattern)):
                    sys.stderr.write("\033[32mignoring\033[0m \033[1m" + f_rel + "\033[0m\n")
                    continue

                if os.path.isdir(f):
                    paths.insert(0, f)
                else:
                    sys.stderr.write("\033[31mrm\033[0m \033[1m" + f_rel + "\033[0m\n")
                    os.remove(f)
        # filter out directories that are not empty
        paths = [p for p in paths if not os.listdir(p)]
        for p in paths:
            p_rel = os.path.relpath(p)
            sys.stderr.write("\033[31mrmdir\033[0m \033[1m" + p_rel + "\033[0m\n")
            os.removedirs(p)


def get_configurators(config):
    configurators = []
    # load built-in pre configurators
    for configurator in config['__configurators_pre__']:
        if isinstance(configurator, str):
            configurator = fancy_import(configurator)
        configurators.append(configurator)

    # load user configurators
    if 'configurators' in config:
        for configurator in config['configurators']:
            if isinstance(configurator, str):
                configurator = fancy_import(configurator)
            configurators.append(configurator)

    # additional configurators, in addition to the all-important defaults
    if 'configurators +' in config:
        sys.stderr.write('''Built-in Configurators are now considered "protected",
so the "configurators +" hack is no longer needed.

However, you will probably want to make sure to include the defaults:
- order_from_name
- created_at_from_name
- title_from_name''')
        for configurator in config['configurators +']:
            if isinstance(configurator, str):
                configurator = fancy_import(configurator)
            configurators.append(configurator)

    # load built-in post configurators
    for configurator in config['__configurators_post__']:
        if isinstance(configurator, str):
            configurator = fancy_import(configurator)
        configurators.append(configurator)

    return configurators
