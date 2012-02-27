import os
import re
import yaml
import datetime
from fnmatch import fnmatch


def ignore(source_file, config):
    file_name = os.path.basename(source_file)
    if config['ignore'] is True or any(pattern for pattern in config['ignore'] if fnmatch(file_name, pattern)):
        return
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


def setdefault_name(source_file, config):
    ##|  ASSIGN DEFAULT NAME
    if 'name' not in config:
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


def setdefault_target_name(source_file, config):
    ##|  ASSIGN TARGET_NAME
    # allow target_name override, otherwise it is
    # `name + ext`
    if not 'target_name' in config:
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


def folder_pre(source_file, config):
    if os.path.isdir(source_file):
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
        elif 'type' not in config:
            config['type'] = 'folder'
    return config


def _check_for_front_matter(source_file):
    with open(source_file, 'r') as f:
        contents = f.read()
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
                return yaml_config
    return {}


def file_pre(source_file, config):
    if os.path.isfile(source_file):
        # an entire folder of static assets can be marked 'dont_process' using 'dont_process': true
        # or it can contain a list of glob patterns
        # note, this doesn't apply to *folders*, they are ignored using 'ignore: true'
        # or 'ignore: [glob patterns]'
        file_name = os.path.basename(source_file)
        should_process = True
        if isinstance(config['dont_process'], bool):
            should_process = not config['dont_process']
        elif any(pattern for pattern in config['dont_process'] if fnmatch(file_name, pattern)):
            should_process = False

        if should_process:
            yaml_config = _check_for_front_matter(source_file)
            if 'dont_process' in yaml_config:
                raise KeyError('"dont_process" is not allowed in yaml front matter.')
            config.update(yaml_config)

        if config['ignore'] is True:
            return
        elif 'type' not in config:
            if should_process:
                config['type'] = 'page'
            else:
                config['type'] = 'asset'
    return config


DATE_RE = re.compile(r'(?P<year>[1-9]\d{3})([-_])(?P<month>\d{2})\2(?P<day>\d{2})\2(?P<name>.*)')


def date_from_name(source_file, config):
    """
    Matches a date in the name or target_name.  Makes it easy to sort a blog
    and you don't have to add `date: ...` using YAML, plus you get a
    python date object.
    """
    if 'created_at' not in config:
        matches = DATE_RE.match(config['name'])
        if matches:
            date = datetime.date(
                year=int(matches.group('year')),
                month=int(matches.group('month')),
                day=int(matches.group('day')),
                )
            config['created_at'] = date
            config['name'] = matches.group('name')
        else:
            matches = DATE_RE.match(config['target_name'])
            if matches:
                date = datetime.date(
                    year=int(matches.group('year')),
                    month=int(matches.group('month')),
                    day=int(matches.group('day')),
                    )
                config['created_at'] = date
    return config


INDEX_RE = re.compile(r'(?P<order>[0]\d+)[-_](?P<name>.*)')


def order_from_name(source_file, config):
    """
    Adds ordering to a file name (when dates aren't quite enough).  The first digit
    *must* be a "0", to distinguish it from a date.
    """
    if 'order' not in config:
        matches = INDEX_RE.match(config['name'])
        if matches:
            config['order'] = int(matches.group('order'))
            config['name'] = matches.group('name')
        else:
            matches = INDEX_RE.match(config['target_name'])
            if matches:
                config['order'] = matches.group('order')
    return config


def _titlecase(s):
        return re.sub(r"[A-Za-z]+('[A-Za-z]+)?",
                      lambda mo: mo.group(0)[0].upper() +
                                 mo.group(0)[1:].lower(),
                      s)


def title_from_name(source_file, config):
    """
    Title-cases the name and stores it in config['title']
    """
    if os.path.isfile(source_file) and 'title' not in config:
        title = config['name']
        title = title.replace('_', ' ')
        title = _titlecase(title)
        config['title'] = title
    return config
