import os
import re

from strange_case.configurators import provides


@provides('name')
def setdefault_name(source_file, config):
    ##|  ASSIGN DEFAULT NAME
    file_name = os.path.basename(source_file)
    base_name, ext = os.path.splitext(file_name)

    if 'rename_extensions' in config and ext in config['rename_extensions']:
        ext = config['rename_extensions'][ext]

    name = base_name

    ##|  FIX NAME
    # add the extension if it exists and isn't ".html"
    if ext and ext != config.get('html_extension'):
        name += '_' + ext[1:]  # pluck off the "." in front

    # replace non-word, hyphens, and spaces characters with _
    name = re.sub(r'[\W -]', '_', name, re.UNICODE)
    config['name'] = name.encode('ascii')
    return config
