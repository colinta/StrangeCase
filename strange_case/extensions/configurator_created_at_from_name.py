import re
import datetime

from strange_case.configurators import provides


DATE_YMD_RE = re.compile(r'(?P<year>[1-9]\d{3})' + \
                         r'(?:([-_])(?P<month>\d{2})' + \
                         r'(?:([-_])(?P<day>\d{2}))?' + \
                         r')?([-_])(?P<name>.*)')


@provides('created_at')
def created_at_from_name(source_file, config):
    """
    Matches a date in the name or target_name.  Makes it easy to sort a blog
    and you don't have to add `date: ...` using YAML, plus you get a
    python date object.
    """
    matches = DATE_YMD_RE.match(config['name'])
    if matches:
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
        config['name'] = matches.group('name')
    else:
        matches = DATE_YMD_RE.match(config['target_name'])
        if matches:
            date = datetime.date(
                year=int(matches.group('year')),
                month=int(matches.group('month')),
                day=int(matches.group('day')),
                )
            config['created_at'] = date
    return config
