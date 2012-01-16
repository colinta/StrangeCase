import yaml
import os
from fnmatch import fnmatch
from copy import deepcopy

from node import *  # imports Node, Page, TemplatePage, and Folder

# these will eventually be command-line configurable:
CONFIG_FILE = u'config.yaml'
CONFIG_PATH = u'./' + CONFIG_FILE
CONTENT_PATH = u'content/'
DEPLOY_PATH = u'public/'
PORT = 8000

DEFAULT_CONFIG = {
    'host': 'http://localhost:' + str(PORT),
    'rename_extensions': {
        '.j2': '.html',
        '.jinja2': '.html',
    },
    'ignore': [
        CONFIG_FILE
    ],
    'dont_process': [
        '*.js', '*.css',
    ]
}


def build_node_tree(content_path, target_path, config, parent_node):
    # don't modify node_config
    node_config = deepcopy(config)

    # merge folder config
    config_path = os.path.join(content_path, CONFIG_FILE)
    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            yaml_config = yaml.load(config_file)
            if yaml_config:
                node_config.update(yaml_config)

    # if { ignore: true }, the entire directory is ignored
    if isinstance(node_config['ignore'], bool) and node_config['ignore']:
        return

    for name in os.listdir(content_path):
        if any(pattern for pattern in node_config['ignore'] if fnmatch(name, pattern)):
            continue

        leaf_config = deepcopy(node_config)

        path = os.path.join(content_path, name)
        target_name, ext = os.path.splitext(name)
        if leaf_config.get('name'):
            target_name = leaf_config.get('name')
        # .jinja2 should be served as .html
        if leaf_config.get('rename_extensions', {}).get(ext):
            ext = leaf_config['rename_extensions'].get(ext)
        target = os.path.join(target_path, target_name + ext)

        if os.path.isdir(path):
            folder_node = FolderNode(parent_node, name, leaf_config, target)

            build_node_tree(path, target, node_config, folder_node)
        else:
            print target

            # an entire folder can be marked 'dont_process' using 'dont_process': true
            # or it can contain a list of glob patterns
            should_process = True
            if isinstance(node_config['dont_process'], bool) and not node_config['dont_process']:
                should_process = False
            elif any(pattern for pattern in node_config['dont_process'] if fnmatch(name, pattern)):
                should_process = False

            if should_process:
                # no need to assign this anywhere,
                # parent_node will add this node as a child.
                TemplatePageNode(parent_node, name, leaf_config, target, path)
            else:
                AssetPageNode(parent_node, name, leaf_config, target, path)

# actual work is done here:
with open(CONFIG_PATH, 'r') as config_file:
    config = {}
    config.update(DEFAULT_CONFIG)
    yaml_config = yaml.load(config_file)
    if yaml_config:
        config.update(yaml_config)

    # look for files in content/
    if not os.path.isdir(CONTENT_PATH):
        raise "Could not find CONTENT_PATH folder \"%s\"" % CONTENT_PATH

    root_node = FolderNode(None, '', config, folder=DEPLOY_PATH)

    build_node_tree(CONTENT_PATH, DEPLOY_PATH, config, root_node)

    root_node.build(site=root_node)
