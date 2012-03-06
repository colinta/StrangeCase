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
