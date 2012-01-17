import yaml
import os
import re
import urllib
from fnmatch import fnmatch
from copy import deepcopy

from node import *  # imports Node, Page, TemplatePage, and Folder

# this will eventually be command-line configurable:
CONFIG_PATH = u'./config.yaml'

# these can all be gleaned from the config file
CONFIG_FILE = u'config.yaml'
SITE_PATH = u'site/'
DEPLOY_PATH = u'public/'
HTML_EXT = '.html'

DEFAULT_CONFIG = {
    'host': 'http://localhost:8000',
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
    ],
    ##|  PATHS
    'config_file': CONFIG_FILE,
    # PROTECTED
    'site_path':   SITE_PATH,
    'deploy_path': DEPLOY_PATH
}


# these settings cannot be overidden on a per-folder basis
PROTECTED = ['site_path', 'deploy_path']


def yamlload(config_path, protected=True):
    with open(config_path, 'r') as config_file:
        yaml_config = yaml.load(config_file)

    if yaml_config and protected:
        for key in PROTECTED:
            try:
                del yaml_config[key]
            except KeyError:
                pass
    return yaml_config


def build_node_tree(source_path, target_path, public_path, config, parent_node):
    # don't modify parent's node_config
    node_config = deepcopy(config)

    # merge folder/config.yaml
    config_path = os.path.join(source_path, config['config_file'])
    folder_config = {}
    if os.path.isfile(config_path):
        yaml_config = yamlload(config_path)

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
        file_path = os.path.join(source_path, file_name)
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
            # no error checking is done if you specify the name yourself.
            name = leaf_config['name']
        else:
            name = base_name

            ##|  FIX NAME
            # modify the name: add the extension if it exists
            # and isn't ".html", and replace non-word characters with _
            if ext and ext != leaf_config['html_extension']:
                name += '_' + ext[1:]  # pluck off the "." in front

            # remove offending characters:
            # non-word, hyphens, and spaces
            name = re.sub(r'[\W -]', '_', name, re.UNICODE)
            leaf_config['name'] = name.encode('ascii')

        ##|  ASSIGN TARGET_NAME
        # allow target_name override, otherwise it is
        # `name + ext`
        if 'target_name' in leaf_config:
            target_name = leaf_config['target_name']
        else:
            target_name = base_name + ext

            ### if ''fix_target_name'' ?
            ### this code makes target names "look purty", like their name counterpart

            # target_name = target_name.replace('-', '_')
            # target_name = target_name.replace(' ', '_')
            # target_name = re.sub(r'/\W/', '_', target_name)

        target = os.path.join(target_path, target_name)

        url = os.path.join(public_path, target_name)

        ##|  ASSIGN URL
        if 'url' in leaf_config:
            raise KeyError('You cannot specify "url" in config.  It is determined by its location in the tree, and the target_names of itself and all its parents')
        leaf_config['url'] = url
        # remove 'index.html' from the end of the url
        if leaf_config['url'].endswith(leaf_config['index']):
            leaf_config['url'] = leaf_config['url'][0:-len(leaf_config['index'])]
        leaf_config['url'] = urllib.quote(url)

        ### DEBUG
        ### print '%s >> %s || %s @ %s' % (name, target, target_name, leaf_config['url'])

        # create node(s)
        if os.path.isdir(file_path):
            # add a trailing slash.  this gives folders the same
            # url as their index page (assuming they have one)
            leaf_config['url'] += '/'
            folder_node = FolderNode(leaf_config, target)
            parent_node.add_child(folder_node)

            build_node_tree(file_path, target, os.path.join(public_path, target_name), node_config, folder_node)
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
                parent_node.add_child(TemplatePageNode(leaf_config, target, file_path))
            else:
                parent_node.add_child(StaticPageNode(leaf_config, target, file_path))

# actual work is done here:
config = {}
config.update(DEFAULT_CONFIG)

yaml_config = yamlload(CONFIG_PATH, protected=False)
if yaml_config:
    config.update(yaml_config)

# look for files in content/
if not os.path.isdir(config['site_path']):
    raise "Could not find SITE_PATH folder \"%s\"" % config['site_path']

root_node = FolderNode(config, folder=config['deploy_path'])
root_node.name = ''

build_node_tree(config['site_path'], config['deploy_path'], '/', config, root_node)

root_node.build(site=root_node)
