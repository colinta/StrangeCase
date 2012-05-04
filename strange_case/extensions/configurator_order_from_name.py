import re

from strange_case.configurators import provides


ORDER_RE = re.compile(r'''
    ^(?P<order>[0]\d+)
    [-_]
    (?P<name>.*)
''', re.VERBOSE)


def strip_order_from(order, name):
    strip_order_re = re.compile(r'^0+{order}[-_]'.format(**locals()))
    match = strip_order_re.search(name)
    if match:
        return name[len(match.group(0)):]
    return name


@provides('order')
def order_from_name(source_file, config):
    """
    Adds ordering to a file name (when dates aren't quite enough).  The first digit
    *must* be a "0", to distinguish it from a date.
    """
    matches = ORDER_RE.search(config['name'])
    order = None
    if matches:
        order = int(matches.group('order'))
    else:
        matches = ORDER_RE.search(config['target_name'])
        if matches:
            order = matches.group('order')

    if order is not None:
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
