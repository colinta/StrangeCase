import os
import re
import yaml


def front_matter_config(source_file, config):
    """
    There are two types of front matter supported by StrangeCase.

    1. YAML Front Matter.  This is the most common, it is delimited by two sets
       of equal number of three or more dashes::

           ----
           yaml: [goes, here]
           ----
    2. The second type is executable python code.  Instead of dashes, use
       backticks.  Again, the number of backticks must match::

           ```
           python = ['goes', 'here']
           ```

    YAML is easy enough - it gets merged in with the node config.  The python
    code is run using ``eval()`` passing the config object in as the local and
    global arguments, so changes to the local scope (adding, changing, removing
    variables) will result in changes to the config object.  You do not access
    the config object within this block.

    This is the last time that the 'type' is checked.  It is often set in the
    front matter to use categories, pagination or other extensions.
    """
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

                yaml_config = yaml.load(front_matter, Loader=yaml.FullLoader)
                if yaml_config:
                    config.update(yaml_config)
                    return config
    return config
