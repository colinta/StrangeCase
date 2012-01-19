"""
The long and short of it:
* write a function that looks like this:
      def your_processor(config, source_file, target_path):
          return (nodes, ...)
* Registry.register('your_name', your_processor)

If you return multiple nodes, they will all be added as children to the parent node.
If instead you need to create some kind of tree structure, build the tree first and
then return the top-level node (still in a tuple).  `build_node_tree` might be your
friend.

All files will be parsed for front matter unless it matches an entry in
'dont_process' (using `fnmatch`).
"""

import yaml
import os
import re
from types import FunctionType
from fnmatch import fnmatch
from copy import deepcopy
from node import FolderNode, RootFolderNode, AssetNode, JinjaNode


def process_config_yaml(config_path):
    # merge folder/config.yaml
    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            yaml_config = yaml.load(config_file)

        if yaml_config:
            return yaml_config
    return {}


def process_front_matter(source_file):
    with open(source_file, 'r') as f:
        contents = f.read()
        front_matter_match = re.match(r"\A([-]{3,})$", contents, re.MULTILINE)
        if front_matter_match:
            offset = len(front_matter_match.group(0)) + 1  # +1 for newline
            delim = re.compile("^" + front_matter_match.group(1) + "$")
            front_matter = ""
            lines = contents.split("\n")[1:]
            for line in lines:
                offset += len(line) + 1
                if delim.match(line):
                    break
                front_matter += line + "\n"

            yaml_config = yaml.load(front_matter)
            if yaml_config:
                return yaml_config
    return {}


def build_node_tree(parent_node, config, source_path, target_path):
    # don't modify parent's node_config
    node_config = parent_node.config_copy()

    # if { ignore: true }, the entire directory is ignored
    if node_config['ignore'] is True:
        return

    for file_name in os.listdir(source_path):
        if any(pattern for pattern in node_config['ignore'] if fnmatch(file_name, pattern)):
            continue

        leaf_config = deepcopy(node_config)

        # figure out source path and base_name, ext to help get us started on the name mangling
        source_file = os.path.join(source_path, file_name)
        base_name, ext = os.path.splitext(file_name)

        ##|  MERGE FILES CONFIG
        # these use the "real" file_name
        if 'files' in leaf_config:
            if file_name in leaf_config['files']:
                leaf_config.update(leaf_config['files'][file_name])
            # the 'files' setting is not passed on to child pages
            del leaf_config['files']

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
            leaf_config['target_name'] = target_name

        ### DEBUG
        ### print 'name:%s >> target_file:%s || target_name:%s @ url:%s' % (name, target_file, target_name)

        # create node(s). if you specify a 'processor' it will override the default.
        if os.path.isdir(source_file):
            # this also happens in the root_processor.  I would prefer these be DRYer, but I
            # don't have a clear idea how to remove one or the other.  RootNode is created
            # imperatively, and so must explicitly look for it.  Folders are detected
            # after that point, but in order to be consistent with files' front matter parsing timing,
            # the config is read *before* its processor is invoked (so no matter what processor you
            # use, it is guaranteed that YAML info)
            config_path = os.path.join(source_file, leaf_config['config_file'])
            leaf_config.update(process_config_yaml(config_path))

            if 'processor' in leaf_config:
                processor = leaf_config['processor']
            else:
                processor = 'folder'

            nodes = Registry.get(processor, leaf_config, source_file, target_path)
        else:
            if 'processor' in leaf_config:
                processor = leaf_config['processor']
            else:
                # an entire folder can be marked 'dont_process' using 'dont_process': true
                # or it can contain a list of glob patterns
                # note, this doesn't apply to *folders*, they are ignored using 'ignore: true'
                # or 'ignore: [glob patterns]'
                should_process = True
                if isinstance(node_config['dont_process'], bool):
                    should_process = not node_config['dont_process']
                elif any(pattern for pattern in node_config['dont_process'] if fnmatch(file_name, pattern)):
                    should_process = False

                if should_process:
                    yaml_config = process_front_matter(source_file)
                    if 'dont_process' in yaml_config:
                        raise KeyError('"dont_process" is not allowed in yaml front matter.')
                    leaf_config.update(yaml_config)

                if 'processor' in leaf_config:
                    processor = leaf_config['processor']
                elif should_process:
                    processor = 'page'
                else:
                    processor = 'asset'

            nodes = Registry.get(processor, leaf_config, source_file, target_path)
        parent_node.extend(nodes)


def root_processor(config, deploy_path, target_path):
    # see note above about why root_processor has this code but folder_processor doesn't
    config_path = os.path.join(deploy_path, config['config_file'])
    config.update(process_config_yaml(config_path))

    node = RootFolderNode(config, deploy_path, target_path)

    build_node_tree(node, config, deploy_path, target_path)
    return (node, )


def folder_processor(config, source_path, target_path):
    node = FolderNode(config, source_path, target_path)

    target_path = os.path.join(target_path, node.target_name)
    if os.path.isdir(source_path):
        build_node_tree(node, config, source_path, target_path)
    return (node, )


def asset_processor(config, source_path, target_path):
    node = AssetNode(config, source_path, target_path)
    return (node, )


def page_processor(config, source_path, target_path):
    node = JinjaNode(config, source_path, target_path)
    return (node, )


class Processor(object):
    """
    If you *really* want to extend something, you can extend Processor.  You
    don't need to, extending object is just as well.  It's here for reference.
    """
    def populate(self, site):
        """
        Classes that implement this method have a chance to populate the 'site' node (and any children thereof,
        obviously) with more nodes.  This is where your Processor class has a chance to add nodes that were
        not discovered as part of the 'build' stage.
        """
        pass

    def process(self, config, source_path, target_path):
        """
        Called when a node registers itself with this processor.

        source_path can be None, if it doesn't refer to a source file.
        target_path is a definite, though.  This is a site generator.  What are you generating if it's not a file!?
        """
        return ()  # implementations should return a tuple of nodes.


class ConcreteMetaclass(type):
    """
    Disables the ability to extend a class.
    """
    def __new__(cls, name, bases, dict):
        for base in bases:
            if isinstance(base, ConcreteMetaclass):
                base_class_name = base.__name__
                raise TypeError("{0} cannot be extended".format(base_class_name))
        return super(ConcreteMetaclass, cls).__new__(cls, name, bases, dict)


class Registry(object):
    __metaclass__ = ConcreteMetaclass
    processors = {}

    def __new__(cls):
        raise TypeError("Don't instantiate Registry.")

    @classmethod
    def register(cls, name, processor):
        if isinstance(processor, type):  # You can pass a class object,
            cls.processors[name] = processor()  # and it gets instantiated
        else:
            cls.processors[name] = processor

    @classmethod
    def startup(cls, site):
        for processor in cls.processors.itervalues():
            # processor = cls.processors[name]
            if hasattr(processor, 'populate'):
                processor.populate(site)

    @classmethod
    def get(cls, name, *args, **kwargs):
        try:
            processor = cls.processors[name]

            if type(processor) is FunctionType:
                return processor(*args, **kwargs)
            else:
                return processor.process(*args, **kwargs)
        except KeyError:
            raise NotImplementedError('Unknown processor "%s"' % name)


Registry.register('root', root_processor)
Registry.register('folder', folder_processor)
Registry.register('asset', asset_processor)
Registry.register('page', page_processor)
