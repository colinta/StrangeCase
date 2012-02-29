import os
from strange_case.registry import Registry
from strange_case.processors import build_node


def strange_case(config):
    # pull out important values.
    site_path = config['site_path']
    deploy_path = config['deploy_path']

    # look for files in content/
    if not os.path.isdir(site_path):
        raise IOError('Could not find site_path folder "%s"' % site_path)

    # this is the one folder that *doesn't* get processed by processers.build_page_tree,
    # so it needs special handling here.
    # config_path = os.path.join(deploy_path, config['config_file'])
    # config.update(check_for_config(config_path))
    config.setdefault('type', 'root')
    root_node = build_node(config, site_path, deploy_path, '')[0]

    root_node.generate()


def fancy_import(name):
    """
    This takes a fully qualified object name, like
    'strange_case.extensions.Markdown2.markdown', and returns the last
    object.  equivalent to `from strange_case.extensions.Markdown2 import markdown`.
    """

    import_path, import_me = name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)


def run():
    # so that strange_case.py can be executed from any project folder, add CWD to the import paths
    import sys
    sys.path.insert(0, os.getcwd())

    CONFIG = None
    if os.path.isfile(os.path.join(os.getcwd(), 'config.py')):
        from config import CONFIG
    else:
        from strange_case.strange_case_config import CONFIG

    from strange_case.support.jinja import StrangeCaseEnvironment

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

    import argparse
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--watch', dest='watch', action='store_const',
                       const=True, default=False,
                       help='watch the site_path for changes (default: find the max)')
    args = parser.parse_args()

    if args.watch:
        import time
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        exclude_paths = [
            os.path.abspath('.git'),
            os.path.abspath(CONFIG['deploy_path']),
        ]

        class Regenerate(FileSystemEventHandler):
            last_run = None

            def on_any_event(self, event, alert=True):
                if self.last_run and time.time() - self.last_run < .1:
                    return

                if alert:
                    print "Change detected.  Running StrangeCase"
                strange_case(CONFIG)
                print "StrangeCase generated at %i" % int(time.time())
                self.last_run = time.time()

        observer = Observer()
        handler = Regenerate()
        for path in os.listdir(os.getcwd()):
            path = os.path.abspath(path)
            if os.path.isdir(path) and path not in exclude_paths:
                print 'Watching "%s" for changes' % path
                observer.schedule(handler, path=path, recursive=True)
        observer.start()
        try:
            handler.on_any_event(None, False)  # run the first time, no alert
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print "Stopping"
            observer.stop()
        observer.join()
    else:
        strange_case(CONFIG)

if __name__ == '__main__':
    run()
