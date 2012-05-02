import datetime


def date(value, format='%d %b %Y'):
    if not value:
        return ''

    if value is "now":
        value = datetime.date.today()
    elif isinstance(value, basestring):
        value = datetime.datetime.strptime(value, "%Y-%m-%d")
    elif isinstance(value, int) or isinstance(value, float):
        value = datetime.datetime.fromtimestamp(value)

    if isinstance(value, datetime.date):
        return value.strftime(format)


def timestamp(value, format=None):
    if not value:
        return ''

    if value is 'now':
        value = datetime.datetime.utcnow()
    elif isinstance(value, int) or isinstance(value, float):
        value = datetime.datetime.fromtimestamp(value)
    else:
        value = datetime.datetime.strptime(value, "%Y-%m-%d:%H:%M")

    if format is None:
        return '%sZ' % value.isoformat()
    else:
        return value.strftime(format)
