import os
from processor import Registry


def strange_case(config):
    # pull out important values.
    # these are not going to change after this point
    site_path = config['site_path']
    deploy_path = config['deploy_path']

    # look for files in content/
    if not os.path.isdir(site_path):
        raise IOError("Could not find site_path folder \"%s\"" % site_path)

    root_node = Registry.get('root', config, site_path, deploy_path)[0]

    Registry.startup(root_node)
    root_node.generate()


if __name__ == '__main__':
    # so that strange_case.py can be executed from any project folder, add CWD to the import paths
    import sys
    sys.path.append(os.getcwd())

    from strange_case_config import CONFIG
    strange_case(CONFIG)
