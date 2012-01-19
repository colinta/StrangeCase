import os
from processor import Registry

from strange_case_config import CONFIG

# pull out important values.
# these are not going to change after this point
PROJECT_PATH = CONFIG['project_path']
SITE_PATH = CONFIG['site_path']
DEPLOY_PATH = CONFIG['deploy_path']


if __name__ == '__main__':
    # look for files in content/
    if not os.path.isdir(SITE_PATH):
        raise IOError("Could not find SITE_PATH folder \"%s\"" % SITE_PATH)

    root_node = Registry.get('root', CONFIG, SITE_PATH, DEPLOY_PATH)[0]

    Registry.startup(root_node)
    root_node.generate()
