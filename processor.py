import yaml
import os
import re
import urllib
from fnmatch import fnmatch
from copy import deepcopy
from node import FolderNode, AssetNode, JinjaNode


##|
##|  The long and short of it:
##|  * extend Processor
##|  * implement process()
##|  * return (nodes, ...).
##|
##|  optionally:
##|  * implement
##|


def process_front_matter(source_path):
    with open(source_path, 'r') as f:
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


def folder_processor(config, source_path, target_path, public_path):
    node = FolderNode(config, public_path, source_path, target_path)
    build_node_tree(node, config, source_path, target_path, public_path)
    return (node, )


def build_node_tree(parent_node, config, source_path, target_path, public_path):
    # don't modify parent's node_config
    node_config = deepcopy(config)

    # merge folder/config.yaml
    config_path = os.path.join(source_path, config['config_file'])
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
        source_file = os.path.join(source_path, file_name)
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
        # remove 'index.html' from the end of the url
        if url.endswith(leaf_config['index']):
            url = url[0:-len(leaf_config['index'])]
        url = urllib.quote(url)

        ### DEBUG
        ### print 'name:%s >> target:%s || target_name:%s @ url:%s' % (name, target, target_name, url)

        # create node(s). if you specify a 'processor' it will override the default.
        if os.path.isdir(source_file):
            # add a trailing slash.  this gives folders the same
            # url as their index page (assuming they have one)
            url += '/'

            if 'processor' in leaf_config:
                processor = leaf_config['processor']
            else:
                processor = 'folder'

            nodes = Processor.get(processor, leaf_config, source_file, target, url)
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
                    leaf_config.update(process_front_matter(source_file))

                if 'processor' in leaf_config:
                    processor = leaf_config['processor']
                elif should_process:
                    processor = 'page'
                else:
                    processor = 'asset'

            # if this file is an index file, it will not be included in the pages iterator.
            # all other pages are iterable.
            if 'iterable' not in leaf_config:
                if target_name != leaf_config['index']:
                    leaf_config['iterable'] = True

            nodes = Processor.get(processor, leaf_config, source_file, target, url)
        parent_node.extend(nodes)


def asset_processor(config, source_path, target_path, public_path):
    node = AssetNode(config, public_path, source_path, target_path)
    return (node, )


def page_processor(config, source_path, target_path, public_path):
    node = JinjaNode(config, public_path, source_path, target_path)
    return (node, )


class Processor(object):
    processors = {}

    @classmethod
    def register(cls, name, processor):
        cls.processors[name] = processor

    @classmethod
    def registerDefault(cls, name, processor):
        if not name in cls.processors:
            cls.processors[name] = processor

    @classmethod
    def get(cls, name, *args, **kwargs):
        try:
            processor = cls.processors[name]
            return processor(*args, **kwargs)
        except KeyError:
            raise NotImplementedError('Unknown processor "%s"' % name)


Processor.registerDefault('root', folder_processor)
Processor.registerDefault('folder', folder_processor)
Processor.registerDefault('asset', asset_processor)
Processor.registerDefault('page', page_processor)
