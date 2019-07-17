"""Builds a strange case, or starts a new strange case project
    scase [options] [config:value [config:value ...]]
    scase --scaffold name project_name

-w --watch                Watch the site_path for changes
--exclude=paths           Exclude files or folders from the --watch command
-n --no-remove            Do not remove "stale" files in the deploy path
-p=path --project=path    Specify the project path [default: os.getcwd()]
-s=path --site=path       Specify the site path [default: site/]
-d=path --deploy=path     Specify the deploy path [default: public/]
-c=file --config=file     Specify a different config.yaml file [default: config.yaml]
-v --verbose              Output warnings and debug messages
--serve[=PORT]            Run a simple http server (on PORT) [default: 8000]

Any other arguments will be parsed as configuration values, e.g.:

    scase seo.title:'My new title'

Will assign "My new title" to config['meta']['title'].  All argument overrides
happen just after config.yaml and config.py are processed, so these act as
project-level overrides.
"""
import os
import sys
import traceback
import yaml
from importlib.machinery import SourceFileLoader

from strange_case import strange_case

def load_source(name, path):
    return SourceFileLoader(name, path).load_module()

def run():
    import logging
    logging.basicConfig()

    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('-w', '--watch', dest='watch', action='store_const',
                       const=True, default=False,
                       help='watch the site_path for changes')
    conf_overrides = [
        'project_path',
        'site_path',
        'deploy_path',
        'remove_stale_files',
        'config_file',
        '__verbose',
    ]
    parser.add_argument('-x', '--exclude', nargs='*', dest='exclude_paths', default=None)
    parser.add_argument('-p', '--project', dest='project_path')
    parser.add_argument('-s', '--site', dest='site_path')
    parser.add_argument('-d', '--deploy', dest='deploy_path')
    parser.add_argument('-r', '--remove', dest='remove_stale_files', action='store_true', default=None)
    parser.add_argument('-n', '--no-remove', dest='remove_stale_files', action='store_false', default=None)
    parser.add_argument('-c', '--config', dest='config_file')
    parser.add_argument('-v', '--verbose', dest='__verbose', action='store_true', default=False)
    parser.add_argument('--serve', dest='port', nargs="?", type=int, default=argparse.SUPPRESS, const=8000)
    parser.add_argument('configs', nargs='*')
    args = parser.parse_args()

    if args.project_path:
        if args.project_path[0] == '~':
            project_path = os.path.expanduser(args.project_path)
        else:
            project_path = os.path.abspath(args.project_path)
    else:
        project_path = os.getcwd()

    # config section catches assertion errors and prints them as error messages
    from strange_case.strange_case_config import CONFIG
    CONFIG['project_path'] = project_path

    if 'site_path' not in CONFIG:
        CONFIG['site_path'] = os.path.join(project_path, u'site/')

    if 'deploy_path' not in CONFIG:
        CONFIG['deploy_path'] = os.path.join(project_path, u'public/')

    # normalize paths
    for conf in ['site_path', 'deploy_path']:
        if CONFIG[conf][0] == '~':
            CONFIG[conf] = os.path.expanduser(CONFIG[conf])
        elif CONFIG[conf][0] == '.':
            CONFIG[conf] = os.path.abspath(CONFIG[conf])

    # now we can look for the app config
    if os.path.isfile(os.path.join(project_path, 'config.py')):
        config_module = load_source('config', os.path.join(project_path, 'config.py'))
        if hasattr(config_module, 'CONFIG'):
            CONFIG.update(config_module.CONFIG)

    config_path = os.path.join(project_path, CONFIG['config_file'])

    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            yaml_config = yaml.load(config_file, Loader=yaml.FullLoader)
        if yaml_config:
            CONFIG.update(yaml_config)

    for conf in conf_overrides:
        if getattr(args, conf) is not None:
            CONFIG[conf] = getattr(args, conf)

    for conf in args.configs:
        if ':' not in conf:
            raise TypeError('Cannot read config "{0}". Does not contain a ":"'.format(conf))
        key, val = conf.split(':', 1)
        assign = CONFIG
        while ('.' in key) or ('[' in key and ']' in key):
            if '.' in key:
                dot = key.index('.')
                assign_key = key[:dot]
                key = key[dot + 1:]
            elif key[0] == '[':
                closing_bracket = key.index(']')
                assign_key = key[1:closing_bracket]
                key = key[closing_bracket + 1:]
            else:
                opening_bracket = key.index('[')
                assign_key = key[:opening_bracket]
                key = key[opening_bracket:]
            assign = CONFIG.get(assign_key, {})
        assign[key] = val

    if CONFIG['config_hook']:
        CONFIG['config_hook'](CONFIG)
        del CONFIG['config_hook']

    try:
        assert CONFIG['project_path'], "project_path is required"
        assert CONFIG['site_path'], "site_path is required"
        assert CONFIG['deploy_path'], "deploy_path is required"
    except AssertionError as e:
        sys.stderr.write("\033[1;31mError:\033[0m \033[1m" + str(e) + "\033[0m\n")
        return

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
                try:
                    strange_case(CONFIG)
                except Exception as e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stderr)
                    sys.stderr.write("Error (%s): %s\n" % (type(e).__name__, str(e)))
                else:
                    sys.stderr.write("StrangeCase generated at %i\n" % int(time.time()))
                self.last_run = time.time()

        exclude_paths = [
            os.path.abspath('.git'),
            os.path.abspath('.hg'),
            os.path.abspath('.svn'),
            os.path.abspath(CONFIG['deploy_path']),
        ]
        if args.exclude_paths:
            exclude_paths.extend([os.path.abspath(path) for path in args.exclude_paths])

        observer = Observer()
        handler = Regenerate()
        for path in os.listdir(project_path):
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

    if hasattr(args, 'port'):
        import SimpleHTTPServer
        import SocketServer

        args.port = args.port

        os.chdir(CONFIG['deploy_path'])
        Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

        httpd = SocketServer.TCPServer(("", args.port), Handler)

        sys.stderr.write("serving at http://localhost:{port}\n".format(port=args.port))
        httpd.serve_forever()


if __name__ == '__main__':
    run()
