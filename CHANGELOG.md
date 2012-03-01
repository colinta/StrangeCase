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