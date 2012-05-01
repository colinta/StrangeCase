from strange_case.registry import Registry
from strange_case.extensions import *
from strange_case.support import *
from strange_case.nodes import *
from strange_case.processors import *

from fnmatch import fnmatch
import sys
import pickle

notifier = None
try:
    from gntp import notifier
    import socket
except ImportError:
    pass

from strange_case.processors import build_node


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


def __scan(folder):
    ret = []
    for f in os.listdir(folder):
        if f.startswith('.'):
            continue

        f = os.path.join(folder, f)
        ret.append(f)
        if os.path.isdir(f):
            ret.extend(__scan(f))
    return ret


def strange_case(config):
    # pull out important values.
    site_path = config['site_path']
    deploy_path = config['deploy_path']

    # look for files in content/
    if not os.path.isdir(site_path):
        raise IOError('Could not find site_path folder "%s"' % site_path)

    # this is the one folder that *doesn't* get processed by processors.build_page_tree,
    # so it needs special handling here.
    config.setdefault('type', 'root')
    Node.files_written = []
    root_node = build_node(config, site_path, deploy_path, '')[0]
    Registry.set('root', root_node)

    remove_stale_files = config['remove_stale_files']
    dont_remove = config['dont_remove']
    existing_files = []
    if os.path.isdir(deploy_path):
        existing_files = __scan(deploy_path)
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
