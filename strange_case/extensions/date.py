"""
Provides ``date`` and ``timestamp`` filters.  Each accepts a ``format`` that
uses datetime.strftime to output a human readable date, and both can accept the
string "now".  But where ``date`` is meant to any date object, ``timestamp``
is meant to output a UTC time.

So use ``{{ value|date }}`` on your date properties (like ``page.created_at``),
and use `{{ "now"|timestamp }}` to output timestamps for RSS feeds and such.

The default date format is outputs something like "11 May 2011".  Here are, for
my own reference, other formatters::

    # as of datetime.datetime(2012, 4, 11, 22, 40, 50, 362334)
    %a:  Locale's abbreviated weekday name.                     "Fri"
    %A:  Locale's full weekday name.                            "Friday"
    %b:  Locale's abbreviated month name.                       "Apr"
    %B:  Locale's full month name.                              "April"
    %c:  Locale's appropriate date and time representation.     "Fri April 11 22:40:50 2012"
    %C:  ???                                                    "20"
    %d:  Day of the month as a decimal number [01,31].          "11"
    %D:  ???                                                    "04/11/12"
    %e:  ???                                                    "11"
    %f:  ???                                                    "362334"
    %F:  ???                                                    "2012-04-11"
    %g:  ???                                                    "12"
    %G:  ???                                                    "2012"
    %h:  ???                                                    "Apr"
    %H:  Hour (24-hour clock) as a decimal number [00,23].      "22"
    %I:  Hour (12-hour clock) as a decimal number [01,12].      "10"
    %j:  Day of the year as a decimal number [001,366]          "102"
    %k:  ???                                                    "22"
    %l:  ???                                                    "10"
    %m:  Month as a decimal number [01,12].                     "05"
    %M:  Minute as a decimal number [00,59].                    "40"
    %n:  ???                                                    "\n"
    %p:  Locale's equivalent of either AM or PM.                "PM"
    %r:  ???                                                    "10:40:50 PM"
    %R:  ???                                                    "22:40"
    %s:  unix timestamp                                         "1334205650"
    %S:  Second as a decimal number [00,61].                    "50"
    %T:  22:40:50
    %x:  Locale's appropriate date representation.              "05/11/12"
    %X:  Locale's appropriate time representation.              "22:40:50"
    %y:  Year without century as a decimal number [00,99].      "12"
    %Y:  Year with century as a decimal number.                 "2012"
    %Z:  Time zone name (no characters if no time zone exists). ""
    %%:  A literal '%' character.                               "%"

    %Y-%m-%d or %F:  SQL date
    %H:%M:%S or %T:  SQL time
    %B %d, %Y:       April 11, 2012

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
    if isinstance(value, basestring):
        try:
            import dateutil
        except ImportError:
            from strange_case import require_package
            require_package('python-dateutil')
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
