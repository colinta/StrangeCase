"""
Provides a pluralization filter, using the inflect library.
"""
from __future__ import absolute_import
try:
    import inflect
except ImportError:
    from strange_case import require_package
    require_package('inflect')


__engine = inflect.engine()

pluralize = __engine.plural
