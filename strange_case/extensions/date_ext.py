import datetime


def date(value, format='%d %b %Y'):
    if not value:
        return ''

    if value is "now":
        value = datetime.date.today()
    elif isinstance(value, basestring):
        value = datetime.datetime.strptime(value, "%Y-%m-%d")
    elif isinstance(value, int) or isinstance(value, float):
        value = datetime.date.fromtimestamp(value)

    if isinstance(value, datetime.date):
        return value.strftime(format)
