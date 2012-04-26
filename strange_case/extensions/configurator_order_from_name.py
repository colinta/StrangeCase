import re

from strange_case.configurators import provides


INDEX_RE = re.compile(r'(?P<order>[0]\d+)[-_](?P<name>.*)')


@provides('order')
def order_from_name(source_file, config):
    """
    Adds ordering to a file name (when dates aren't quite enough).  The first digit
    *must* be a "0", to distinguish it from a date.
    """
    matches = INDEX_RE.match(config['name'])
    if matches:
        config['order'] = int(matches.group('order'))
        config['name'] = matches.group('name')
    else:
        matches = INDEX_RE.match(config['target_name'])
        if matches:
            config['order'] = matches.group('order')
    return config
