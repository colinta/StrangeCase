import os
import yaml


def folder_config_file(source_file, config):
    if config['type'] == 'folder' or config['type'] == 'root':
        # the config is read *before* its processor is invoked (so no matter what processor you
        # use, it is guaranteed that its config is complete)
        config_path = os.path.join(source_file, config['config_file'])
        if os.path.isfile(config_path):
            with open(config_path, 'r') as config_file:
                yaml_config = yaml.load(config_file, Loader=yaml.FullLoader)

            if yaml_config:
                config.update(yaml_config)
    return config
