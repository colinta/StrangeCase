import os
import re
import datetime


CREATED_AT_RE = re.compile(r'''
    (?P<created_at>
        (?P<year>[1-9]\d{3})
        (?:
            [-_](?P<month>\d{2})
            (?:
                [-_](?P<day>\d{2})
            )?
        )?
    )[-_]
    (?P<name>.*)''', re.VERBOSE)


def strip_created_at_from(created_at, name):
    created_at = re.sub(r'[-_]', '[-_]', created_at)
    strip_created_at_re = re.compile(r'{created_at}[-_]'.format(**locals()))
    match = strip_created_at_re.search(name)
    if match:
        return name[:match.start()] + name[match.end():]
    return name


def created_at_from_name(source_file, config):
    """
    Matches a date in the name or target_name.  Makes it easy to sort a blog
    and you don't have to add `date: ...` using YAML, plus you get a
    python date object.
    """
    file_name = os.path.basename(source_file)
    matches = CREATED_AT_RE.search(file_name)

    if matches:
        created_at = matches.group('created_at')
        if 'created_at' not in config:
            year = int(matches.group('year'))
            if matches.group('month') is not None:
                month = int(matches.group('month'))
            else:
                month = 1

            if matches.group('day') is not None:
                day = int(matches.group('day'))
            else:
                day = 1

            date = datetime.date(
                year=year,
                month=month,
                day=day,
                )
            config['created_at'] = date

        if config['strip_metadata_from_name']:
            config['name'] = strip_created_at_from(created_at, config['name'])

        if config['strip_metadata_from_target_name']:
            config['target_name'] = strip_created_at_from(created_at, config['target_name'])
    return config

created_at_from_name.defaults = {
    'strip_metadata_from_name': True,
    'strip_metadata_from_target_name': False,
}

created_at_from_name.dont_inherit = [
    'created_at'
]
