import datetime


def date(value, format='%d %b %Y'):
    if isinstance(value, basestring):
        value = datetime.strptime(value)

    if isinstance(value, datetime.date):
        return value.strftime(format)
