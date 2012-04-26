import re

from strange_case.configurators import provides


def titlecase(s):
    s = s.replace('_', ' ')
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() +
                             mo.group(0)[1:].lower(),
                  s)


@provides('title')
def title_from_name(source_file, config):
    """
    Title-cases the name and stores it in config['title']
    """
    if config['is_index'] and hasattr(config, 'parent'):
        title = config.parent.name
    else:
        title = config['name']
    title = titlecase(title)
    config['title'] = title
    return config
