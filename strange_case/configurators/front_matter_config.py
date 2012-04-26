import os
import re
import yaml


def front_matter_config(source_file, config):
    if config['type'] == 'page' and os.path.isfile(source_file):
        with open(source_file, 'r') as f:
            contents = f.read()
            front_config_match = re.match(r"\A([`]{3,})$", contents, re.MULTILINE)
            if front_config_match:
                offset = len(front_config_match.group(0)) + 1  # +1 for newline
                delim = re.compile("^" + front_config_match.group(1) + "$")
                front_config = ""
                lines = contents.split("\n")[1:]
                for line in lines:
                    offset += len(line) + 1
                    if delim.match(line):
                        break
                    front_config += line + "\n"

                config_code = compile(front_config, 'config.py', 'exec')
                eval(config_code, config, config)
                return config

            front_matter_match = re.match(r"\A([-]{3,})$(.*\n)*?\1", contents, re.MULTILINE)
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
                    config.update(yaml_config)
                    return config
    return config
