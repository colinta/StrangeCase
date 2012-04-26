import os
import sys
import yaml
import pickle

from strange_case.registry import Registry
from strange_case.nodes import Node
from strange_case.config_dict import ConfigDict
from strange_case import strange_case


def fancy_import(import_name):
    """
    This takes a fully qualified object name, like
    'strange_case.extensions.markdown', and returns the last
    object.  equivalent to `from strange_case.extensions import markdown`.
    """

    import_path, import_me = import_name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)


def run():
    import logging
    logging.basicConfig()

    # so that strange_case.py can be executed from any project folder, add CWD to the import paths
    sys.path.insert(0, os.getcwd())

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-w', '--watch', dest='watch', action='store_const',
                       const=True, default=False,
                       help='watch the site_path for changes (default: find the max)')
    conf_overrides = [
        'project_path',
        'site_path',
        'deploy_path',
        'remove_stale_files',
        'config_file',
    ]
    parser.add_argument('-x', '--exclude', nargs='*', dest='exclude_paths', default=None)
    parser.add_argument('-p', '--project', dest='project_path')
    parser.add_argument('-s', '--site', dest='site_path')
    parser.add_argument('-d', '--deploy', dest='deploy_path')
    parser.add_argument('-r', '--remove', dest='remove_stale_files', action='store_true', default=None)
    parser.add_argument('-n', '--no-remove', dest='remove_stale_files', action='store_false', default=None)
    parser.add_argument('-c', '--config', dest='config_file')
    parser.add_argument('configs', nargs='*')

    # config section catches assertion errors and prints them as error messages
    try:
        if os.path.isfile(os.path.join(os.getcwd(), 'config.py')):
            from config import CONFIG
            if not isinstance(CONFIG, ConfigDict):
                CONFIG = ConfigDict(CONFIG)
        else:
            from strange_case.strange_case_config import CONFIG

        # normalize paths
        for conf in ['project_path', 'site_path', 'deploy_path']:
            if CONFIG[conf][0] == '~':
                CONFIG[conf] = os.path.expanduser(CONFIG[conf])
            elif CONFIG[conf][0] == '.':
                CONFIG[conf] = os.path.abspath(CONFIG[conf])

        # now we can look for the app config
        config_path = os.path.join(CONFIG['project_path'], CONFIG['config_file'])

        if os.path.isfile(config_path):
            with open(config_path, 'r') as config_file:
                yaml_config = yaml.load(config_file)
            if yaml_config:
                CONFIG.update(yaml_config)

        args = parser.parse_args()
        for conf in conf_overrides:
            if getattr(args, conf) is not None:
                CONFIG[conf] = getattr(args, conf)

        assign = None
        for confs in args.configs:
            if assign:
                CONFIG[assign] = confs
                assign = None
            elif ':' in confs:
                key, val = confs.split(':', 1)
                CONFIG[key] = val
            else:
                assign = confs

        if CONFIG['config_hook']:
            CONFIG['config_hook'](CONFIG)
            del CONFIG['config_hook']

        assert CONFIG['project_path'], "project_path is required"
        assert CONFIG['site_path'], "site_path is required"
        assert CONFIG['deploy_path'], "deploy_path is required"
    except AssertionError as e:
        sys.stderr.write("\033[1;31mError:\033[0m \033[1m" + e.message + "\033[0m\n")
        return

    if not os.path.isdir(CONFIG['deploy_path']):
        os.mkdir(CONFIG['deploy_path'])

    from strange_case.support.jinja import StrangeCaseEnvironment

    extensions = []
    if 'extensions' in CONFIG:
        for extension in CONFIG['extensions']:
            if isinstance(extension, basestring):
                try:
                    extension = fancy_import(extension)
                except ImportError:
                    sys.error.write('Error in processors: Could not find "%s"\n' % extension)
                    raise
            extensions.append(extension)
        del CONFIG['extensions']

    if not Registry.get('jinja_environment', None):
        jinja_environment = StrangeCaseEnvironment(extensions=extensions, project_path=CONFIG['project_path'])
        Registry.set('jinja_environment', jinja_environment)
    else:
        jinja_environment = Registry.get('jinja_environment')

    if 'filters' in CONFIG:
        for filter_name, method in CONFIG['filters'].iteritems():
            if isinstance(method, basestring):
                try:
                    method = fancy_import(method)
                except ImportError:
                    sys.error.write('Error in filters: Could not find "%s"\n' % method)
                    raise
            jinja_environment.filters[filter_name] = method
        del CONFIG['filters']

    if 'processors' in CONFIG:
        for processor in CONFIG['processors']:
            try:
                fancy_import(processor)
            except ImportError:
                sys.error.write('Error in processors: Could not find "%s"\n' % processor)
                raise
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
        del CONFIG['configurators +']

    # additional file_types
    for entry in Registry.file_types:
        CONFIG['file_types'].append(entry)

    if 'file_types +' in CONFIG:
        CONFIG['file_types'].extend(CONFIG['file_types +'])

    # read timestamps file
    timestamps_file = os.path.join(CONFIG['project_path'], '.timestamps')
    if os.path.exists(timestamps_file):
        CONFIG['file_mtimes'] = pickle.load(open(timestamps_file))

    timestamps = {}
    for file_tracked in Node.files_tracked:
        f = os.path.abspath(file_tracked)
        timestamps[f] = os.stat(file_tracked).st_mtime

    if args.watch:
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class Regenerate(FileSystemEventHandler):
            last_run = None

            def on_any_event(self, event, alert=True):
                if self.last_run and time.time() - self.last_run < .1:
                    return

                if alert:
                    sys.stderr.write("Change detected.  Running StrangeCase\n")
                strange_case(CONFIG)
                sys.stderr.write("StrangeCase generated at %i\n" % int(time.time()))
                self.last_run = time.time()

        exclude_paths = [
            os.path.abspath('.git'),
            os.path.abspath(CONFIG['deploy_path']),
        ]
        if args.exclude_paths:
            exclude_paths.extend([os.path.abspath(path) for path in args.exclude_paths])

        observer = Observer()
        handler = Regenerate()
        for path in os.listdir(os.getcwd()):
            path = os.path.abspath(path)
            if os.path.isdir(path) and path not in exclude_paths:
                sys.stderr.write('Watching "%s" for changes\n' % path)
                observer.schedule(handler, path=path, recursive=True)
        observer.start()
        try:
            handler.on_any_event(None, False)  # run the first time, no alert
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.stderr.write("Stopping\n")
            observer.stop()
        observer.join()
    else:
        strange_case(CONFIG)


if __name__ == '__main__':
    run()
