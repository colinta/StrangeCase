import yaml
import os
from fnmatch import fnmatch
from copy import deepcopy
from jinja2 import Environment
from strange_case_jinja import YamlFrontMatterLoader, YamlFrontMatterTemplate

from node import *  # imports Node, Page, TemplatePage, and Folder


DEFAULT_CONFIG = {
    'rename_extensions': {
        '.j2': '.html'
    },
    'ignore': [],  # CONFIG_FILE gets added to this
    # 'dont_process': [
    #     '*.js', '*.png', '*.jpg', '*.jpeg',
    #     '*.css'
    # ]
}


# these will eventually be command-line configurable
CONFIG_FILE = u'config.yaml'
CONFIG_PATH = u'./' + CONFIG_FILE
CONTENT_PATH = u'content/'
DEPLOY_PATH = u'public/'

DEFAULT_CONFIG['ignore'] = [CONFIG_FILE]

loader = YamlFrontMatterLoader(os.getcwd())
env = Environment(loader=loader)
env.template_class = YamlFrontMatterTemplate


def build_templates_in(content_path, target_path, config, parent_node):
    # don't modify folder_config
    folder_config = deepcopy(config)

    # merge folder config
    config_path = os.path.join(content_path, CONFIG_FILE)
    if os.path.isfile(config_path):
        with open(config_path, 'r') as config_file:
            yaml_config = yaml.load(config_file)
            if yaml_config:
                folder_config.update(yaml_config)

    if isinstance(folder_config['ignore'], bool) and folder_config['ignore']:
        return

    for name in os.listdir(content_path):
        if any(pattern for pattern in folder_config['ignore'] if fnmatch(name, pattern)):
            continue

        path = os.path.join(content_path, name)
        target = os.path.join(target_path, name)

        local_config = deepcopy(folder_config)

        if os.path.isdir(path):
            folder_node = FolderNode(parent_node, name, local_config, target)

            build_templates_in(path, target, folder_config, folder_node)
        else:
            name, ext = os.path.splitext(name)
            target_name, ext = os.path.splitext(target)
            if ext in local_config['rename_extensions'].keys():
                target = target_name + unicode(local_config['rename_extensions'][ext])

            if True:  # if 'should_process'
                template = env.get_template(path, globals=local_config)

                # parent_node will add this node as a child
                TemplatePageNode(parent_node, name, local_config, target, template)
            else:
                # parent_node will add this node as a child
                AssetPageNode(parent_node, name, local_config, target, path)


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

    build_templates_in(CONTENT_PATH, DEPLOY_PATH, config, root_node)

    root_node.build(site=root_node)
    # for template in templates:
    #     target = template.globals['target']

    #     target_path, target_name = os.path.split(target)

    #     if not os.path.isdir(target_path):
    #         os.mkdir(target_path, 0755)

    #     content = template.render()
    #     with open(target, 'w') as dest:
    #         dest.write(content)
