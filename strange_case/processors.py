"""
The long and short of it:
* write a function that looks like this:
      def your_processor(config, source_file, target_path):
          return (nodes, ...)
* Registry.register('your_processor', your_processor)

If you return multiple nodes, they will all be added as children to the parent node.
If instead you need to create some kind of tree structure, build the tree first and
then return the top-level node (still in a tuple).  `build_node` might be your
friend, it handles the configurating.
"""

import os
from strange_case.nodes import FolderNode, RootFolderNode, AssetNode
# import nodes for supported engines
from strange_case.nodes import JinjaNode, PlywoodNode
from strange_case.registry import Registry
from strange_case.configurators import configurate


def build_node(config, source_path, target_path, file_name):
    source_file = os.path.abspath(os.path.join(source_path, file_name))

    config = configurate(source_file, config)
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
Registry.register('root', root_processor)


def folder_processor(config, source_path, target_path):
    node = FolderNode(config, source_path, target_path)

    target_path = os.path.join(target_path, node.target_name)
    if source_path and os.path.isdir(source_path):
        build_node_tree(node, source_path, target_path)
    return (node, )
Registry.register('folder', folder_processor)


def asset_processor(config, source_path, target_path):
    node = AssetNode(config, source_path, target_path)
    return (node, )
Registry.register('asset', asset_processor)


def page_processor(config, source_path, target_path):
    page_type = config['page_type']
    node_class = Registry.get_engine(page_type)
    node = node_class(config, source_path, target_path)
    return (node, )
Registry.register('page', page_processor)
