import os
import re
import yaml
import datetime
from fnmatch import fnmatch
from functools import wraps


def provides(*confs):
    def decorator(function):
        @wraps(function)
        def wrapper(source_file, config):
            if all(conf not in config for conf in confs):
                return function(source_file, config)
            return config
        return wrapper
    return decorator


@provides('type')
def file_types(source_file, config):
    if os.path.isdir(source_file):
        config['type'] = 'folder'
        return config
    else:
        file_name = os.path.basename(source_file)
        for node_type, globs in config.get('file_types', []):
            if isinstance(globs, basestring):
                globs = [globs]
            for pattern in globs:
                if fnmatch(file_name, pattern):
                    config['type'] = node_type
                    return config
        if not config.get('default_type', None):
            return None
        config['type'] = config['default_type']
        return config


def merge_files_config(source_file, config):
    ##|  MERGE FILES CONFIG
    # these use the physical file_name
    file_name = os.path.basename(source_file)
    if 'files' in config:
        if file_name in config['files']:
            config.update(config['files'][file_name])
        # the 'files' setting is not passed on to child pages
        del config['files']
    return config


@provides('name')
def setdefault_name(source_file, config):
    ##|  ASSIGN DEFAULT NAME
    file_name = os.path.basename(source_file)
    base_name, ext = os.path.splitext(file_name)

    if 'rename_extensions' in config and ext in config['rename_extensions']:
        ext = config['rename_extensions'][ext]

    name = base_name

    ##|  FIX NAME
    # add the extension if it exists and isn't ".html"
    if ext and ext != config['html_extension']:
        name += '_' + ext[1:]  # pluck off the "." in front

    # replace non-word, hyphens, and spaces characters with _
    name = re.sub(r'[\W -]', '_', name, re.UNICODE)
    config['name'] = name.encode('ascii')
    return config


@provides('target_name')
def setdefault_target_name(source_file, config):
    ##|  ASSIGN TARGET_NAME
    # allow target_name override, otherwise it is
    # `name + ext`
    ##|  FIX EXTENSION
    # .jinja2, .j2, and .md files should be served as .html
    file_name = os.path.basename(source_file)
    base_name, ext = os.path.splitext(file_name)
    if 'rename_extensions' in config and ext in config['rename_extensions']:
        ext = config['rename_extensions'][ext]
        config['target_name'] = base_name + ext

    target_name = base_name + ext

    ### fix_target_name?
    ### this code makes target names "look purty", like their name counterpart
    ##
    # target_name = re.sub(r'/[\W -]/', '_', target_name, re.UNICODE)
    ##
    ### it's commented out because I'm not convinced target_names should get
    ### this treatment.  If you have a strange character in your URL, that's
    ### your business.  Or maybe I'll add something to the upcoming "renamers"
    config['target_name'] = target_name
    return config


@provides('is_index')
def setdefault_is_index(source_file, config):
    ##|  ASSIGN DEFAULT NAME

    config['is_index'] = False
    if os.path.isfile(source_file):
        if config['target_name'] == config['index.html'] and hasattr(config, 'parent'):
            config['is_index'] = True
    return config


def folder_config_file(source_file, config):
    if config['type'] == 'folder':
        # the config is read *before* its processor is invoked (so no matter what processor you
        # use, it is guaranteed that its config is complete)
        config_path = os.path.join(source_file, config['config_file'])
        if os.path.isfile(config_path):
            with open(config_path, 'r') as config_file:
                yaml_config = yaml.load(config_file)

            if yaml_config:
                config.update(yaml_config)
        # if { ignore: true }, the entire directory is ignored
        if config['ignore'] is True:
            return
    return config


def front_matter_config(source_file, config):
    if config['type'] != 'asset' and os.path.isfile(source_file):
        with open(source_file, 'r') as f:
            contents = f.read()
            front_config_match = re.match(r"\A([`]{3,})$", contents, re.MULTILINE)
            if front_config_match:
                offset = len(front_config_match.group(0)) + 1  # +1 for newline
                delim = re.compile("^" + front_config_match.group(1) + "$")
                front_config = ""
                lines = contents.split("\n")[1:]
                for line in lines:
                    offset += len(line) + 1
                    if delim.match(line):
                        break
                    front_config += line + "\n"

                config_code = compile(front_config, 'config.py', 'exec')
                eval(config_code, config, config)
                return config

            front_matter_match = re.match(r"\A([-]{3,})$", contents, re.MULTILINE)
            if front_matter_match:
                offset = len(front_matter_match.group(0)) + 1  # +1 for newline
                delim = re.compile("^" + front_matter_match.group(1) + "$")
                front_matter = ""
                lines = contents.split("\n")[1:]
                for line in lines:
                    offset += len(line) + 1
                    if delim.match(line):
                        break
                    front_matter += line + "\n"

                yaml_config = yaml.load(front_matter)
                if yaml_config:
                    config.update(yaml_config)
                    return config
    return config


def ignore(source_file, config):
    file_name = os.path.basename(source_file)
    if config['ignore'] is True or any(pattern for pattern in config['ignore'] if fnmatch(file_name, pattern)):
        return
    return config


DATE_YMD_RE = re.compile(r'(?P<year>[1-9]\d{3})(?:([-_])(?P<month>\d{2})(?:\2(?P<day>\d{2}))?)?\2(?P<name>.*)')


@provides('created_at')
def date_from_name(source_file, config):
    """
    Matches a date in the name or target_name.  Makes it easy to sort a blog
    and you don't have to add `date: ...` using YAML, plus you get a
    python date object.
    """
    matches = DATE_YMD_RE.match(config['name'])
    if matches:
        year = int(matches.group('year'))
        if matches.group('month') is not None:
            month = int(matches.group('month'))
        else:
            month = int(matches.group('month'))

        if matches.group('day') is not None:
            day = int(matches.group('day'))
        else:
            day = 1
        date = datetime.date(
            year=year,
            month=month,
            day=day,
            )
        config['created_at'] = date
        config['name'] = matches.group('name')
    else:
        matches = DATE_YMD_RE.match(config['target_name'])
        if matches:
            date = datetime.date(
                year=int(matches.group('year')),
                month=int(matches.group('month')),
                day=int(matches.group('day')),
                )
            config['created_at'] = date
    return config


INDEX_RE = re.compile(r'(?P<order>[0]\d+)[-_](?P<name>.*)')


@provides('order')
def order_from_name(source_file, config):
    """
    Adds ordering to a file name (when dates aren't quite enough).  The first digit
    *must* be a "0", to distinguish it from a date.
    """
    matches = INDEX_RE.match(config['name'])
    if matches:
        config['order'] = int(matches.group('order'))
        config['name'] = matches.group('name')
    else:
        matches = INDEX_RE.match(config['target_name'])
        if matches:
            config['order'] = matches.group('order')
    return config


def titlecase(s):
    s = s.replace('_', ' ')
    return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                  lambda mo: mo.group(0)[0].upper() +
                             mo.group(0)[1:].lower(),
                  s)


@provides('title')
def title_from_name(source_file, config):
    """
    Title-cases the name and stores it in config['title']
    """
    if config['is_index'] and hasattr(config, 'parent'):
        title = config.parent.name
    else:
        title = config['name']
    title = title.replace('_', ' ')
    title = titlecase(title)
    config['title'] = title
    return config
