import yaml
import os
import re
import urllib
from fnmatch import fnmatch
from copy import deepcopy

from node import *  # imports Node, Page, TemplatePage, and Folder

# these will eventually be command-line configurable:
CONFIG_FILE = u'config.yaml'
CONFIG_PATH = u'./' + CONFIG_FILE
SITE_PATH = u'site/'
DEPLOY_PATH = u'public/'
PORT = 8000
HTML_EXT = '.html'

DEFAULT_CONFIG = {
    'host': 'http://localhost:' + str(PORT),
    'html_extension': HTML_EXT,
    'index': 'index' + HTML_EXT,
    'rename_extensions': {
        '.md': HTML_EXT,
        '.j2': HTML_EXT,
        '.jinja2': HTML_EXT,
    },
    'ignore': [
        '.*',
        CONFIG_FILE
    ],
    'dont_process': [
        '*.js', '*.css',
    ]
}


def build_node_tree(source_path, target_path, config, parent_node):
    # don't modify parent's node_config
    node_config = deepcopy(config)

    # merge folder/config.yaml
    config_path = os.path.join(source_path, CONFIG_FILE)
    folder_config = {}
    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            yaml_config = yaml.load(config_file)
            if yaml_config:
                folder_config.update(yaml_config)
                node_config.update(folder_config)

                # the 'files' setting is not merged.  it is super special. :-(
                try:
                    del node_config['files']
                except KeyError:
                    pass

    # if { ignore: true }, the entire directory is ignored
    if node_config['ignore'] is True:
        return

    for file_name in os.listdir(source_path):
        if any(pattern for pattern in node_config['ignore'] if fnmatch(file_name, pattern)):
            continue

        leaf_config = deepcopy(node_config)

        # figure out source path and base_name, ext to help get us started on the name mangling
        path = os.path.join(source_path, file_name)
        base_name, ext = os.path.splitext(file_name)

        ##|  MERGE FILES CONFIG
        # these use the "real" file_name
        try:
            if folder_config['files'] and folder_config['files'][file_name]:
                leaf_config.update(folder_config['files'][file_name])
        except KeyError:
            pass

        ##|  FIX EXTENSION
        # .jinja2 should be served as .html
        if 'rename_extensions' in leaf_config and ext in leaf_config['rename_extensions']:
            ext = leaf_config['rename_extensions'][ext]

        ##|  ASSIGN NAME
        # name override
        if 'name' in leaf_config:
            name = leaf_config['name']
        else:
            name = base_name

        ##|  ASSIGN TARGET_NAME
        # allow target_name override, otherwise it is
        # `name + ext`
        if 'target_name' in leaf_config:
            target_name = leaf_config['target_name']
        else:
            target_name = base_name + ext

        ##|  FIX NAME
        # modify the name: add the extension if it exists
        # and isn't ".html", and replace non-word characters with _
        if ext and ext != HTML_EXT:
            name += '_' + ext[1:]
        name = name.replace('-', '_')
        name = name.replace(' ', '_')
        name = re.sub(r'/\W/', '_', name)

        target = os.path.join(target_path, target_name)

        public_path = source_path[len(SITE_PATH):]
        url = os.path.join('/' + public_path, target_name)

        ##|  ASSIGN URL
        leaf_config['url'] = url
        # remove 'index.html from the end of the url'
        if leaf_config['url'].endswith(leaf_config['index']):
            leaf_config['url'] = leaf_config['url'][0:-len(leaf_config['index'])]
        leaf_config['url'] = urllib.quote(url)

        ### DEBUG
        ### print '%s >> %s @ %s' % (name, target, leaf_config['url'])

        # create node(s)
        if os.path.isdir(path):
            # add a trailing slash.  this gives folders the same
            # url as their index page (assuming they have one)
            leaf_config['url'] += '/'
            folder_node = FolderNode(name, leaf_config, target)
            parent_node.add_child(folder_node)

            build_node_tree(path, target, node_config, folder_node)
        else:
            # an entire folder can be marked 'dont_process' using 'dont_process': true
            # or it can contain a list of glob patterns
            should_process = True
            if isinstance(node_config['dont_process'], bool):
                should_process = not node_config['dont_process']
            elif any(pattern for pattern in node_config['dont_process'] if fnmatch(file_name, pattern)):
                should_process = False

            # if this file is an index file, it will not be included in the pages iterator.
            # all other pages are iterable
            if 'iterable' not in leaf_config:
                if target_name != leaf_config['index']:
                    leaf_config['iterable'] = True

            if should_process:
                parent_node.add_child(TemplatePageNode(name, leaf_config, target, path))
            else:
                parent_node.add_child(StaticPageNode(name, leaf_config, target, path))

# actual work is done here:
with open(CONFIG_PATH, 'r') as config_file:
    config = {}
    config.update(DEFAULT_CONFIG)
    yaml_config = yaml.load(config_file)
    if yaml_config:
        config.update(yaml_config)

    # look for files in content/
    if not os.path.isdir(SITE_PATH):
        raise "Could not find SITE_PATH folder \"%s\"" % SITE_PATH

    root_node = FolderNode('', config, folder=DEPLOY_PATH)

    build_node_tree(SITE_PATH, DEPLOY_PATH, config, root_node)

    root_node.build(site=root_node)
