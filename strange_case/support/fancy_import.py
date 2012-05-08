

def fancy_import(import_name):
    """
    This takes a fully qualified object name, like
    'strange_case.extensions.markdown', and returns the last
    object.  equivalent to `from strange_case.extensions import markdown`.
    """

    import_path, import_me = import_name.rsplit('.', 1)
    imported = __import__(import_path, globals(), locals(), [import_me], -1)
    return getattr(imported, import_me)
