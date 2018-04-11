"""
Provides ``date`` and ``timestamp`` filters.  Each accepts a ``format`` that
uses datetime.strftime to output a human readable date, and both can accept the
string "now".  But where ``date`` is meant to any date object, ``timestamp``
is meant to output a UTC time.

So use ``{{ value|date }}`` on your date properties (like ``page.created_at``),
and use `{{ "now"|timestamp }}` to output timestamps for RSS feeds and such.

The default date format is outputs something like "11 May 2011".  Here are, for
my own reference, other formatters::

    # as of datetime.datetime(2011, 4, 7, 9, 1, 2, 362334)
    %a:  Locale's abbreviated weekday name.                     "Thu"
    %A:  Locale's full weekday name.                            "Thursday"
    %b:  Locale's abbreviated month name.                       "Apr"
    %B:  Locale's full month name.                              "April"
    %c:  Locale's appropriate date and time representation.     "Thu April  7 09:01:02 2012"
    %C:  ??? (century?)                                         "20"
    %d:  Day of the month as a decimal number [01,31].          "07"
    %D:  ???                                                    "04/07/12"
    %e:  Day of the month without "0" in front                  " 7"
    %f:  ???                                                    "000003"
    %F:  ???                                                    "2012-04-07"
    %g:  ???                                                    "11"
    %G:  ???                                                    "2011"
    %h:  ???                                                    "Apr"
    %H:  Hour (24-hour clock) as a decimal number [00,23].      "09"
    %I:  Hour (12-hour clock) as a decimal number [01,12].      "09"
    %j:  Day of the year as a decimal number [001,366]          "097"
    %k:  ???                                                    " 9"
    %l:  ???                                                    " 9"
    %m:  Month as a decimal number [01,12].                     "04"
    %M:  Minute as a decimal number [00,59].                    "01"
    %n:  newline                                                "\n"
    %p:  Locale's equivalent of either AM or PM.                "AM"
    %r:  time with seconds and am/pm                            "09:01:02 AM"
    %R:  military time in HH:MM in 24-h                         "09:01"
    %s:  unix timestamp                                         "1302188462"
    %S:  Second as a decimal number [00,61].                    "02"
    %T:  Military time, with seconds                            "09:01:02"
    %x:  Locale's appropriate date representation.              "04/07/12"
    %X:  Locale's appropriate time representation.              "09:01:02"
    %y:  Year without century as a decimal number [00,99].      "11"
    %Y:  Year with century as a decimal number.                 "2011"
    %z:  UTC Offset                                             "-0600"
    %Z:  Time zone name (no characters if no time zone exists). ""
    %%:  A literal '%' character.                               "%"

    %Y-%m-%d or %F:  SQL date
    %H:%M:%S or %T:  SQL time
    %B %d, %Y:       April 11, 2012
    %a, %e %b %Y %X %z:  RSS pubDate format

``timestamp`` on the other hand defaults to a UTC timestamp in ISO 8601 format::

    2012-05-12T04:42:47.362334Z

Usage::

    {{ page.created_at|date }}
    {{ page.created_at|date('%Y-%m-%d') }}
    {{ "now"|date }}
    {{ "now"|timestamp }}

If any other string is passed to ``date`` or ``timestamp``, it will be parsed
using ``python-dateutil``.  Since this is less commond, it is imported lazily.
"""
import datetime


def to_datetime(value):
    if isinstance(value, datetime.date) or isinstance(value, datetime.datetime):
        return value
    if isinstance(value, int) or isinstance(value, float):
        return datetime.datetime.utcfromtimestamp(value)
    if isinstance(value, str):
        try:
            import dateutil.parser
        except ImportError:
            from strange_case import require_package
            require_package('python-dateutil')
        return dateutil.parser.parse(value)
    raise TypeError('Invalid argument {!r} passed to `to_datetime`'.format(value))


def date(value, format='%d %b %Y'):
    """
    Default format: 01 May 2012
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
