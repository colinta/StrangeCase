TODO
====

* create a generic Extension mechanism, something that brings `filters` and
  `processors` and `configurators` all under one roof.

* add scaffolding, especially to help create a useful config.yaml file (which
  is, at this point, pretty much a necessity)

* add CSS/JS compressor/minification/combinator support, probably as a tag.

* **CANCELED** merge YAML/config using a DSL that allows arrays to be extended
  instead of replaced

* **TABLED** table of contents

2012_05_09 - v4.2.0
===================

* added `scase --serve` command

2012_05_06 - v4.1.6
===================

* Lots more tests, including entire site building tests.
* Lots of fixes - thanks, tests!
* configurator methods can now offer some special properties that are picked up
  in the `strange_case` function, `meta_before` and `meta_after`:
  1. defaults - a dictionary of configuration key/values
  2. require_before - a list of config keys that must be present when
     configuration starts
  3. require_after - a list of config keys that must be present when
     configuration ends
  4. on_start - a function that is called before the root node is created, it is
     passed the config dict
  5. on_finish - a function that is called after the site is generater, also
     handed the config dict

2012_04_27 - v4.0.10
====================

* The configurators have been totally broken up into components, with some of
  them being relegated to "extension" status (`setdefault_title`,
  `order_from_name`, `created_at_from_name`) and added some new ones
  (`file_mtime`, `file_ctime`, `strip_extensions`).
* Opened up the #strangecase chat room on irc.freenode.com.  Join us! :-)
* Moved `url` and `iterable` "detection" into configuration.  *However*, there
  **is** still a `url` method on `Node`, which attaches the parent's url.
* Tests!  Finally added a test framework, using py.test.

2012_03_13 - v3.0.3
===================

* refactored the extensions folder *again*.  removed all the imports from `__init__.py`.
  you **WILL** need to update your imports:

      strange_case.extensions.Markdown2Extension => strange_case.extensions.markdown.MarkdownExtension
      strange_case.extensions.markdown => strange_case.extensions.markdown.markdown
      strange_case.extensions.date => strange_case.extensions.date.date
      strange_case.extensions.sha => strange_case.extensions.sha.sha
      strange_case.extensions.image_processor => strange_case.extensions.image
      strange_case.extensions.paginated_processor => strange_case.extensions.paginated
      strange_case.extensions.category_processor => strange_case.extensions.category
      strange_case.extensions.clevercss_processor => strange_case.extensions.clevercss_ext
      strange_case.extensions.scss_processor => strange_case.extensions.scss_ext

* Thanks to this refactor, CleverCSS, PIL, markdown2, and PySCSS are now
  optional, not installed as part of `pip install StrangeCase`

* Added `require_package` helper to output error message when a package is not
  installed.  Usage: `require_package("PIL")`.

2012_03_13 - v3.0.3
===================

* refactored the extensions folder, but that shouldn't affect anyone

* added 'default_type' config, used when `type` isn't set and no `file_types` match the file

2012_03_13 - v3.0.0
===================

* added scss_processor and clevercss_processor.  They compile and save SCSS/CleverCSS into CSS.

* moved all extensions into the strange_case.extensions module.  processors, extensions, and filters
  are all imported from there.

* refactored configurator to use the 'file_types' config, which is modified during startup by
  processors to associate file types with a default processor.  this replaces the `dont_process`
  configuration.

* updated README to reflect these changes

2012_03_11 - v2.4.0
===================

* added a `paginated` processor.  it will iterate through all the pages in the folder and
  create a `Page` object that holds `paginated.limit` items (default: 10).  the first page
  will be named after the page that you assign `type: paginated`.  every page after that
  will be named "pageN.html", where N is one-indexed (and therefore starts at "2", since
  the first page is probably "index.html").  see the README or `processors/paginated.py`
  file for more info

* added favicon.ico to list of dont_process defaults

* command-line options (`-x`, `--exclude`) to exclude folders from the `--watch` command.

* date configurator matches Y, Y-M, or Y-M-D.  month and day default to 1.

2012_03_01 - v2.3.0
===================

* you can now specify the following configurations as command-line options:
  + `-p`, `--project`:   project_path
  + `-s`, `--site`:      site_path
  + `-d`, `--deploy`:    deploy_path
  + `-r`, `--remove`:    remove_stale_files
  + `-n`, `--no-remove`: remove_stale_files
  + `-c`, `--config`:    config_file
  + `key:value`:         any key/value
  + `key: value`:        these don't have to be "touching"

  These override any defaults, and any settings in config.py and config.yaml

* You can now have python configuration front matter.  Instead of dashes, use "\`\`\`"s
  python configuration front matter is eval'd with the current `config` as `locals()`,
  so any assignments you make in you front matter will be available in your template.

  See README for more information

* Added `config_hook`, so that you can assign configuration *at the end* of configuration.
  It is a callable that is passed one argument: the `CONFIG` variable.

  You can use this to process configurations that are expected from the command line.

* Fixed the file removal to use absolute paths when matching against `dont_remove`, but
  outputs using `os.path.relpath`

* Terminal-formatted output, and writes messages to `sys.stderr`

* Support error messages using `assert` in config.py.


2012_03_01 - v2.2.0
===================

"Stale" files are now automatically removed during generation!  This can be controlled
and disabled.

* Added `remove_stale_files` boolean and `dont_remove` list to config.

* if `remove_stale_files` is true, all files that don't match patterns in `dont_remove`
  and were not generated are removed.

  Defaults:
  `remove_stale_files`: true
  `dont_remove`: ['.*']  # dotfiles

2012_02_29 - v2.1.4
===================
* First submission to PyPi.
* Supports --watch using watchdog
* see README for all features
