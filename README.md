The Strange Case of...
======================

It's yet another static site generator.  Have you seen [jekyll](https://github.com/mojombo/jekyll)?
[hyde](http://ringce.com/hyde)?  Yup.  Like those.

But this one is:

1. Written in python, unlike `jekyll`
2. **NOT** complicated, unlike `hyde`.  And I mean *really* **NOT** complicated.

----------------------------------------------------------------------------------------------------------------

First, the complicated stuff.  This will hopefully make sense at the end.  I mention them
first so that you get an idea for the *most* complicated parts (which aren't really that
complicated)

* `config.yaml` files can contain a `files:` dictionary where the keys refer to a file in that folder, and
  the values are treated as yaml front matter.  This makes it possible to add meta data to binary files.

* Index pages are not included when iterating over a folder.

* Index pages' URLs do not include the filename.  This means they have the same name
  as the folder they index.  That's good, right?

* To add filters and extensions to jinja add `extensions` and `filters` to your base config.yaml file.  You
  can also do this using config.py if you need to do some special importing or other runtime configuration.


Now for the easy stuff!

----------------------------------------------------------------------------------------------------------------

QUICK START
-----------

1. In your project folder, make a `site` and `public` folder.
2. Put index.j2 in site, and put some html in there.
3. Add YAML front matter to that file.  It looks like this:

```
---
title: My first page
---
<!doctype html>
...
```

4. Use that YAML in your page using [jinja2](http://jinja.pocoo.org/)'s template language syntax:

```
---
title: My first page
---
<!doctype html>
<h1>{{ title }}</h1>
```

5. Run strange case:
   `$ python strange_case.py`

6. Open `public/index.html`.  You might want to hold onto your jaw, lest it drop to the floor.  Yeah, it's not gonna say `{{ title }}`,
   it's gonna say `My First Page` in big letters.

7. Add more templates, add layouts, add include files, add static assets, and learn more about [jinja2](http://jinja.pocoo.org/).

8. Because that is just about all that StrangeCase is gonna do for you!†

† *this is not true, StrangeCase is capable of generating category pages, tag clouds, image listings, and it's all very straightforward.*


OK, SO
-------

* In your project folder (where you execute StrangeCase), you can have `config.yaml` and/or `config.py`, and you *definitely* have a
  `site/` folder, where your site content is stored.  Why isn't this stuff in the "root" folder?  Because there are jinja2 layouts, includes,
  and who knows what else in there.

* `site/` stores site content: templates, assets, folders, and maybe some "special" files like category pages.
  These are processed, rendered, copied, or ignored, as the case may be.

* When StrangeCase is done it places your static site in `public/`.

* These are the only two special folders: site, and public. They can be changed in config (`site_path` and `dest_path`).

* `config.yaml` stores context variables.  It is merged with the default config.  Child folders and pages inherit all the
  config settings of their parent except name, target_name, source_path, and type.

* Template files (.html, .txt, .md) can contain YAML front matter.  If the first line is a bunch of dashes (`^[-]{3,}$`),
  all lines up to the matching dashes will be treated as YAML and added to that files context variables.

* Binary files can have front matter, too, but since you can't place it *in* the file, it is stored in a special `files:`
  setting in the parent folder's config.yaml file.  It should be a dictionary with the key corresponding to the name
  of the file, and the value is the front matter for that file.  `files:` entries in `config.yaml` are not inherited.

* Everything in `config.yaml` and YAML front matter is available as a context variable in your templates.

* Templates are rendered using [jinja2](http://jinja.pocoo.org/).

* StrangeCase points Jinja to your project folder, so you can use any directories you want in there
  to store layouts, macros, and partials.
  * layouts that are in `layouts/` are extended using `{% extends 'layouts/file.j2' %}`
  * includes in `anywhere/` are included using `{% include 'anywhere/file.j2' %}`
  * I guess the convention is to have layouts/ and includes/ folders.

* In the project root, config.py is where you can place runtime things, like...
  * if you need to calculate a value (e.g. datetime.time)
  * fetch some data from a database (ewww!)
  * import jinja extensions (or use 'extensions' in config.yaml)
  * import jinja filters (or use 'filters' in config.yaml)
  * register StrangeCase processors (or use 'processors' in config.yaml)

* If you need a page to be processed differently, set `type` to another file type in the config for that file/folder.
  For instance, the category page should have `type: category_index`.

* You can prefix variables on a page with `my.` (e.g. `my.title` or `my.parent`). I think it looks
  better in some places because it makes it clear where the content comes from (e.g. `{{ my.title }}` as
  opposed to just `{{ title }}`).  Totally optional.


DEFAULT/SPECIAL CONFIG
----------------------

``` yaml
  config_file: 'config.yaml'  # name of file that contains config
  host: "http://localhost:8000"  # hostname.  I'm not using this for anything, but it might be import for plugin authors one day
  index: index.html  # any file whose target_name matches this name will not be iterable
  ignore: ['config.yaml', '.*']  # which files to ignore altogether while building the site
  dont_process: ['*.js', '*.css', images]  # do not run these files through jinja
  rename_extensions: { '.j2': '.html', '.jinja2': '.html' }  # which extensions to rename
  html_extension: '.html'  # files with this extension are html files (`page.is_page` => `True`)

  # PROTECTED
  # these can only be assigned in the root config file, otherwise they will
  # be treated as plain ol' file data
  site_path: 'site/'  # where to find site content
  deploy_path: 'public/'  # where to put the generated site
  extensions: []  # list of jinja2 extension classes as a dot-separated import path
  filters: {}  # dictionary of `filter_name: filter.method`.
  processors: []  # additional processors.  Processors register themselves as a certain type.
```

RUNNING StrangeCase
-------------------

`$ python strange_case.py`


RUNNING StrangeCase, PART 2
---------------------------

StrangeCase parses all the files and directories in `site/`.

* Files/Folders that match `ignore` are not processed at all.
* Folders become `FolderNode` objects (`site/` is such a node) and scanned recursively.
* Templates (any file that doesn't match `dont_process`) become `JinjaNode(FileNode)` objects.
* Assets (anything that isn't a template) become `AssetNode(FileNode)` objects.
* These can be overridden using the `type` config.


These nodes are placed in a tree:

    (root, aka site)
    | static/
    | | css/
    | | + style.css
    | \ image/
    |   | img1.png
    |   | img2.png
    |   + img3.png
    | robots.txt
    | index (index.j2 => index.html)
    \ blogs/
      | test1 (test1.j2 => test1.html)
      + test2 (test2.j2 => test2.html)


TEMPLATES
---------

### In your templates, you have access to anything in the top-level config and in per-page metadata:

`/config.yaml`:

``` yaml
meta:
  author:
    name: "Colin"
```

`/site/index.html`:

``` jinja
---
# YAML front matter
title: test
---

<h1>{{ meta.author.name }}</h1>
<h2>{{ title }}</h2>
<h2>{{ my.title }}</h2>
```

=>

``` html
<h1>Colin</h1>
<h2>test</h2>
<h2>test</h2>
```

### Access any page by name:

(This is a common thing to do in StrangeCase)

``` jinja
<a href="{{ site.blogs.best_blog_ever.url }}">Best blog ever</a>.
```

In order to access pages this way, non-word characters are replaced by "_".  e.g. `-my.goofy-$-filename.txt` => `my_goofy___filename_txt`.

** * Note: * ** The .html extension is removed from html files, but all other extensions are preserved.  So `file.txt` => `file_txt` (since
"." is a special character).


THIS IS COOL AND SO WORTH POINTING OUT
--------------------------------------

### You can iterate over folders:

``` jinja
{% for blog in site.blogs %}
<p>{{ loop.index }}. {{ blog.title }}</p>
{% endfor %}
```

=>

``` html
<p>1. Blog Title</p>
<p>2. Blog Title</p>
```

** * Note: * ** Files named `index.html` will not be included in this list.  This is a
very reasonable design decision, but I can imagin a situation where you have a file (think
`robots.txt`) that *also* doesn't belong in the iterable pages list.  So `iterable: false` is
available as a config setting.


### Iterate over a folder of images

``` jinja
{% for image in site.static.image %}
<img src="{{ image.url }}" />
{% endfor %}
```

** * BAM * **, how's that for an image listing!  This might be my favorite thing in StrangeCase,
that folders are iterable.  It makes things that were weird in jekyll very easy and intuitive in StrangeCase.

Also, you might want to check out the image processor, explained below.  It uses PIL to make thumbnail images.

You can check what kind of node you're working with using the `type` property ("page", "folder", "asset") or
the `is_page`, `is_folder`, `is_asset` methods.  Internally this is done a lot, I can't think of a reason
you would need to do this in a template... but there it is!


Lastly, the `.all()` method, and its more specific variants, are useful.  The `all()` method definition says it all I think:

``` python
def all(self, recursive=False, folders=None, pages=None, assets=None, processors=None):
    """
    Returns descendants, ignoring iterability. Folders, assets, and
    pages can all be included or excluded as the case demands.

    If you specify any of folders, pages, assets or processors, only those objects
    will be returned.
    Otherwise all node types will be returned.

    recursive, though, defaults to False.  calling all(True) is the same as all(recursive=True)
    """
```

The variants are all subsets of `all()`:

``` python
  def pages(self, recursive=False):
      return self.all(recursive=recursive, pages=True)

  def folders(self, recursive=False):
      return self.all(recursive=recursive, folders=True)

  def assets(self, recursive=False):
      return self.all(recursive=recursive, assets=True)

  def files(self, recursive=False):
      return self.all(recursive=recursive, pages=True, assets=True)

  def processors(self, recursive=False):
      return self.all(recursive=recursive, processors=True)
```


AND THAT'S (pretty much) IT
---------------------------

jinja2 makes it easy to put complicated logic in templates, which is really the only place for them in this static generator context...

...or is it !?  I’m wondering what kind of spaghetti nonsense these templates could end up with (it's like PHP all over again!), and how that could be fixed.

Which leads right into...


*REALLY COMPLICATED STUFF*
--------------------------

This relates to the `config.py` and `config.yaml` files mentioned above.

You should glance at the colinta.github.com repository on the build branch.  It does most things that can be done (and look in
`extensions/` for the markdown and date extension, I copied it from somewhere).

You can define `extensions`, `filters`, and `processors`.  Filters are a dictionary of `filter: package`.  Extensions is a list of packages.

If you specify these in config.py, you can import the extension/filter and assign it to the list.  Otherwise, in config.yaml,
use a dot-separated path, similar to how you would write an `import` statement, but include the class name.

There are a couple built-in processors that are not imported & registered by default: categories and image.  You can add these using similar tricks.

Like I mentioned earlier, you can add context variables that need the **POWER OF PYTHON** to be determined. Like datetime.time().
I might add a way to do this in the YAML, but *probably not* (unless the community argues for its inclusion).


Example of all this nonsense using `config.py`:

``` python
from strange_case_config import CONFIG
from processors import image, categories
from extensions.Markdown2 import Markdown2Extension, markdown2_filter
from datetime.datetime import time

CONFIG.update({
    'extensions': [Markdown2Extension],
    'filters': {
        'markdown': markdown2_filter,
    },
    'processors': [image, categories]
    'time': int(time()),
})
```

Equivalent in the root `config.yaml`:

``` yaml
extensions:
  - extensions.Markdown2.Markdown2Extension
filters:
  markdown2: extensions.Markdown2.markdown2_filter
processors:
  - processors.image
  - processors.categories
# cannot assign time to datetime.time.  DANG.
```

`processors/categories.py` has an explanation of how processors work, and how it was written.  I made it up as I went along, and ended up adding
a `Processor` class that extends `Node`, and a concept of "populating" the tree after the initial build.  Read more in that file.  I think
it's a good system, but I'm open to friendly suggestions.


TODO
----

* Placing entries in `**/config.yaml` override parent configs, but i'd like to add a merging syntax to the YAML, as a little DSL.
* I like to add date prefixes to my file names so that they get sorted in the order I want.  But I have to manually set the date
  and name in the front matter, which is annoying.  Add a "filename parser" that is optional and configurable?
* And if I'm gonna do that, isn't that just a subset of including front matter and config.yaml?  Maybe all these tasks can be converted
  into a nifty new whizbang system.

LICENSE
-------

Copyright (c) 2012, Colin Thomas-Arnold
All rights reserved.

See [LICENSE](https://github.com/colinta/StrangeCase/blob/master/LICENSE) for more details (it's a simplified BSD license).
