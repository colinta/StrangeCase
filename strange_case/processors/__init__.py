"""
The long and short of it:
* write a function that looks like this:
      def your_processor(config, source_file, target_path):
          return (nodes, ...)
* Registry.register('your_type', your_processor)

If you return multiple nodes, they will all be added as children to the parent node.
If instead you need to create some kind of tree structure, build the tree first and
then return the top-level node (still in a tuple).  `build_node` might be your
friend, it handles the configurating.

All files will be parsed for front matter unless it matches an entry in
'dont_process' (using `fnmatch`).
"""

import os
from strange_case.nodes import FolderNode, RootFolderNode, AssetNode, JinjaNode
from strange_case.registry import Registry


def build_node(config, source_path, target_path, file_name):
    source_file = os.path.join(source_path, file_name)

    configurators = Registry.configurators
    # Run the config through each configurator.
    # If a configurator returns a falsey
    # value, the node will be ignored.
    for configurator in configurators:
        config = configurator(source_file, config)
        if not config:
            return

    # create node(s). if you specify a 'type' it will override the default.
    # built-in types are 'page', 'folder', and 'asset'

    processor = config['type']
    return Registry.nodes(processor, config, source_file, target_path)


def build_node_tree(parent_node, source_path, target_path):
    # scan the folder
    files = os.listdir(source_path)
    files.sort()
    for file_name in files:
        nodes = build_node(parent_node.config_copy(), source_path, target_path, file_name)
        if nodes:
            parent_node.extend(nodes)


def root_processor(config, deploy_path, target_path):
    node = RootFolderNode(config, deploy_path, target_path)

    build_node_tree(node, deploy_path, target_path)
    return (node, )


def folder_processor(config, source_path, target_path):
    node = FolderNode(config, source_path, target_path)

    target_path = os.path.join(target_path, node.target_name)
    if source_path and os.path.isdir(source_path):
        build_node_tree(node, source_path, target_path)
    return (node, )


def asset_processor(config, source_path, target_path):
    node = AssetNode(config, source_path, target_path)
    return (node, )


def page_processor(config, source_path, target_path):
    node = JinjaNode(config, source_path, target_path)
    return (node, )


Registry.register('root', root_processor)
Registry.register('folder', folder_processor)
Registry.register('asset', asset_processor)
Registry.register('page', page_processor)
