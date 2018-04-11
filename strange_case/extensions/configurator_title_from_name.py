import re

from strange_case.configurators import provides


def titlecase(s):
    s = s.replace('_', ' ')
    s = s.lower()
    s = re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() +
                             mo.group(0)[1:].lower(),
                  s)
    s = re.sub(r'\b(A|The)\b', lambda mo: mo.group(1).lower(), s)
    if len(s) > 1:
        s = s[0].upper() + s[1:]
    return s


@provides('title')
def title_from_name(source_file, config):
    """
    Title-cases the name and stores it in config['title']
    """
    if config['is_index'] and hasattr(config, 'parent'):
        title = config.parent['name']
    else:
        title = config['name']
    title = titlecase(title)
    config['title'] = title
    return config


title_from_name.dont_inherit = [
    'title'
]
