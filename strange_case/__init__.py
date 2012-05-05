from fnmatch import fnmatch
import sys
import pickle

from strange_case.registry import Registry
from strange_case.extensions import *
from strange_case.support import *
from strange_case.nodes import *
from strange_case.processors import *
from strange_case.nodes import Node

notifier = None
try:
    from gntp import notifier
    import socket
except ImportError:
    pass


def output_error(msg):
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)
    sys.exit(1)


def output_warning(msg):
    if msg[-1] != "\n":
        msg += "\n"
    sys.stderr.write(msg)


def require_package(pkg):
    output_error("\033[1m" + pkg + "\033[0m is required.\n  > pip install " + pkg)


def recommend_package(pkg):
    output_warning("\033[1m" + pkg + "\033[0m is recommend.\n  > pip install " + pkg)


def fancy_import(import_name):
    """
    This takes a fully qualified object name, like
    'strange_case.extensions.markdown', and returns the last
    object.  equivalent to `from strange_case.extensions import markdown`.
    """

    import_path, import_me = import_name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)


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
    site_path = config['site_path']
    deploy_path = config['deploy_path']

    # look for files in content/
    if not os.path.isdir(site_path):
        raise IOError('Could not find site_path folder "%s"' % site_path)

    if not os.path.isdir(config['deploy_path']):
        os.mkdir(config['deploy_path'])

    from strange_case.support.jinja import StrangeCaseEnvironment

    extensions = []
    if 'extensions' in config:
        for extension in config['extensions']:
            if isinstance(extension, basestring):
                try:
                    extension = fancy_import(extension)
                except ImportError:
                    sys.error.write('Error in processors: Could not find "%s"\n' % extension)
                    raise
            extensions.append(extension)
        del config['extensions']

    if not Registry.get('jinja_environment'):
        jinja_environment = StrangeCaseEnvironment(extensions=extensions, project_path=config['project_path'])
        Registry.set('jinja_environment', jinja_environment)
    else:
        jinja_environment = Registry.get('jinja_environment')

    if 'filters' in config:
        for filter_name, method in config['filters'].iteritems():
            if isinstance(method, basestring):
                try:
                    method = fancy_import(method)
                except ImportError:
                    sys.error.write('Error in filters: Could not find "%s"\n' % method)
                    raise
            jinja_environment.filters[filter_name] = method
        del config['filters']

    if 'processors' in config:
        for processor in config['processors']:
            try:
                fancy_import(processor)
            except ImportError:
                sys.error.write('Error in processors: Could not find "%s"\n' % processor)
                raise
        del config['processors']

    # register configurators
    for configurator in get_configurators(config):
        Registry.add_configurator(configurator)

    # read timestamps file
    timestamps_file = os.path.join(config['project_path'], '.timestamps')
    if os.path.exists(timestamps_file):
        config['file_mtimes'] = pickle.load(open(timestamps_file))

    # this is the one folder that *doesn't* get processed by processors.build_page_tree,
    # so it needs special handling here.
    Node.files_written = []
    root_node = build_node(config, site_path, deploy_path, '')[0]
    assert root_node.type == 'root'
    Registry.set('root', root_node)

    remove_stale_files = config['remove_stale_files']
    dont_remove = config['dont_remove']
    existing_files = []
    if os.path.isdir(deploy_path):
        existing_files = find_files(deploy_path)
    else:
        os.makedirs(deploy_path)
    root_node.generate()

    # create timestamps file
    timestamps = {}
    for file_tracked in Node.files_tracked:
        f = os.path.abspath(file_tracked)
        timestamps[f] = os.stat(file_tracked).st_mtime
    timestamps_file = os.path.join(config['project_path'], '.timestamps')
    pickle.dump(timestamps, open(timestamps_file, 'w'))

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

    if notifier:
        try:
            growl = notifier.GrowlNotifier(
                applicationName="StrangeCase",
                notifications=["New Messages"],
                defaultNotifications=["New Messages"],
            )
            growl.register()

            # Send one message
            growl.notify(
                noteType="New Messages",
                title="StrangeCase site generated",
                description="site is available at:\n"
                    "{config[deploy_path]}"\
                    .format(config=config),
            )
        except socket.error:
            pass


def get_configurators(config):
    configurators = []
    # load built-in pre configurators
    for configurator in config['__configurators_pre__']:
        if isinstance(configurator, basestring):
            configurator = fancy_import(configurator)
        configurators.append(configurator)
    del config['__configurators_pre__']

    # load user configurators
    if 'configurators' in config:
        for configurator in config['configurators']:
            if isinstance(configurator, basestring):
                configurator = fancy_import(configurator)
            configurators.append(configurator)
        del config['configurators']

    # additional configurators, in addition to the all-important defaults
    if 'configurators +' in config:
        sys.error.write('''Built-in Configurators are now considered "protected",
so the "configurators +" hack is no longer needed.

However, you will probably want to make sure to include the defaults:
- order_from_name
- created_at_from_name
- title_from_name''')
        for configurator in config['configurators +']:
            if isinstance(configurator, basestring):
                configurator = fancy_import(configurator)
            configurators.append(configurator)
        del config['configurators +']

    # load built-in post configurators
    for configurator in config['__configurators_post__']:
        if isinstance(configurator, basestring):
            configurator = fancy_import(configurator)
        configurators.append(configurator)
    del config['__configurators_post__']

    return configurators
