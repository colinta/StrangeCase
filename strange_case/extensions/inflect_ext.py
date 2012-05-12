"""
Provides a pluralization filter, using the inflect library.
"""
try:
    import inflect
except ImportError:
    from strange_case import require_package
    require_package('inflect')


__inflect = inflect.engine()

pluralize = __inflect.plural
