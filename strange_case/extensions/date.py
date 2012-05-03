import dateutil
import datetime


def to_datetime(value):
    if isinstance(value, int) or isinstance(value, float):
        return datetime.datetime.utcfromtimestamp(value)
    elif isinstance(value, basestring):
        return dateutil.parser.parse(value)


def date(value, format='%d %b %Y'):
    if not value:
        return ''

    if value is "now":
        value = datetime.date.today()
    else:
        value = to_datetime(value)

    return value.strftime(format)


def timestamp(value, format=None):
    if not value:
        return ''

    if value is 'now':
        value = datetime.datetime.utcnow()
    else:
        value = to_datetime(value)

    if format is None:
        return '%sZ' % value.isoformat()
    else:
        return value.strftime(format)
