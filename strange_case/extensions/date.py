import dateutil
import datetime


def to_datetime(value):
    if isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
        return value
    if isinstance(value, int) or isinstance(value, float):
        return datetime.datetime.utcfromtimestamp(value)
    if isinstance(value, basestring):
        return dateutil.parser.parse(value)
    raise TypeError('Invalid argument {!r} passed to `to_datetime`'.format(value))


def date(value, format='%d %b %Y'):
    """
    Default format: 13 May 2012
    """
    if not value:
        return ''

    if value is "now":
        value = datetime.datetime.now()
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
