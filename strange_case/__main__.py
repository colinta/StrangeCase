import imp
import os
import sys
import yaml

from strange_case import strange_case


def run():
    import logging
    logging.basicConfig()

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
        'verbose',
    ]
    parser.add_argument('-x', '--exclude', nargs='*', dest='exclude_paths', default=None)
    parser.add_argument('-p', '--project', dest='project_path')
    parser.add_argument('-s', '--site', dest='site_path')
    parser.add_argument('-d', '--deploy', dest='deploy_path')
    parser.add_argument('-r', '--remove', dest='remove_stale_files', action='store_true', default=None)
    parser.add_argument('-n', '--no-remove', dest='remove_stale_files', action='store_false', default=None)
    parser.add_argument('-c', '--config', dest='config_file')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False)
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
        config_module = imp.load_source('config', os.path.join(project_path, 'config.py'))
        try:
            CONFIG.update(config_module.CONFIG)
        except AttributeError:
            sys.stderr.write("Could not load CONFIG from config.py\n")
            sys.exit(1)
    config_path = os.path.join(project_path, CONFIG['config_file'])

    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            yaml_config = yaml.load(config_file)
        if yaml_config:
            CONFIG.update(yaml_config)

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

    try:
        assert CONFIG['project_path'], "project_path is required"
        assert CONFIG['site_path'], "site_path is required"
        assert CONFIG['deploy_path'], "deploy_path is required"
    except AssertionError as e:
        sys.stderr.write("\033[1;31mError:\033[0m \033[1m" + e.message + "\033[0m\n")
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


if __name__ == '__main__':
    run()
