import os
import re


ORDER_RE = re.compile(r'''
    ^0+(?P<order>[1-9]\d*)
    [-_]
    (?P<name>.*)
''', re.VERBOSE)


def strip_order_from(order, name):
    strip_order_re = re.compile(r'^0+{order}[-_]'.format(**locals()))
    match = strip_order_re.search(name)
    if match:
        return name[:match.start()] + name[match.end():]
    return name


def order_from_name(source_file, config):
    """
    Adds ordering to a file name (when dates aren't quite enough).  The first digit
    *must* be a "0", to distinguish it from a date.
    """
    file_name = os.path.basename(source_file)
    matches = ORDER_RE.search(file_name)
    if matches:
        order = int(matches.group('order'))
        if 'order' not in config:
            config['order'] = order

        if config['strip_metadata_from_name']:
            config['name'] = strip_order_from(order, config['name'])

        if config['strip_metadata_from_target_name']:
            config['target_name'] = strip_order_from(order, config['target_name'])
    return config

order_from_name.defaults = {
    'strip_metadata_from_name': True,
    'strip_metadata_from_target_name': False,
}

order_from_name.dont_inherit = [
    'order'
]
