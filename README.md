The Strange Case of...
======================

It's yet another static site generator.  Have you seen (jekyll)[https://github.com/mojombo/jekyll]?
(hyde)[http://ringce.com/hyde]?  Yup.  Like those.

But this one is:

1. Written in python, unlike `jekyll`
2. **NOT** complicated, unlike `hyde`.  And I mean *really* **NOT** complicated.

----------------------------------------------------------------------------------------------------------------

First, the complicated stuff.  This will hopefully make sense at the end.  I mention them
first so that you get an idea for the *most* complicated parts (which aren't really that
complicated)

* `config.yaml` files can contain a `files:` dictionary where the keys refer to a file in that folder, and
  the values are treated as yaml front matter.  This makes it possible to configure binary files.

* Index pages are not included when iterating over a folder.

* Index pages' URLs do not include the filename.  This means they have the same name
  as the folder they index.  That's good, right?


Now for the easy stuff!

----------------------------------------------------------------------------------------------------------------

OK, SO
-------


* `config.yaml` stores context variables.  It is merged with the default config (see below - it's simple, too!).

* Everything in your `config.yaml` files is available as a context variable.  `config.yaml` files in a folder
  are merged with the parent folder.

* `site/` stores site content - templates and assets.  These are processed or copied or ignored, as the case may be.

* `config.yaml` files in a folder within `site/` override settings in the parent folder.

* Template files (.html, .txt, .md) can contain YAML front matter.  If the first line is `^[-]{3,}$`, everything up
  to the matching dashes will be treated as YAML and added to that files context variables.

* Templates are processed using (jinja2)[http://jinja.pocoo.org/]

* Jinja is told only about your project folder, so you can use any directories you want
  to store layouts, macros, and partials.
  * layouts that are in `layouts/` are extended using `{% extends 'layouts/file.j2' %}`
  * includes can go in `anywhere/`, and then they are included using `{% include 'anywhere/file.j2' %}`
  * SO: only `site/` is special.

* For fun, you can prefix variables on a page with `my.` (e.g. `my.title` or `my.parent`). I think it looks
  better in some places because it makes it clear where the content comes from (e.g. `{{ my.title }}` as
  opposed to just `{{ title }}`).


DEFAULT/SPECIAL CONFIG
----------------------

``` yaml
  config_file: 'config.yaml'  # name of file that contains config
  host: "http://localhost:8000"  # hostname.  I'm not using this for anything, but I imagine it will be importand for pligin authors
  index: index.html  # any file whose target_name matches this name will not be iterable
  ignore: ['config.yaml', '.*']  # which files to ignore altogether
  dont_process: ['*.js', '*.css', *images]  # do not run these files through jinja
  rename_extensions: { '.j2': '.html', '.jinja2': '.html' }  # which extensions to rename
  html_extension: '.html'  # files with this extension are html files (`page.is_page` => `True`)
  # PROTECTED
  # these can only be assigned in the root config file
  site_path: 'site/'  # where to find site content
  deploy_path: 'public/'  # where to put the generated site
```


EXECUTING
---------

`$ python strange_case.py`

Goes through all the files and directories in `site/`

* Files/Folders that match `ignore` are skipped.
* Folders become `FolderNode` objects (`site/` is such a node).  Folders have children.
* Templates (any file that doesn't match `dont_process`) become `TemplatePageNode(PageNode)` objects
* Assets (anything that isn't a template) become `StaticPageNode(PageNode)` objects

Files can have metadata either as front matter, or in that folder's `config.yaml` in a `files:` entry.
The `files:` entry is so that static assets can have metadata.  Because of this, `files:` in the `config.yaml` files are not
copied or merged with child or parent settings.


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


### Access any page by name:

``` jinja
{{ site.blogs.test1.url }}
```

In order to access pages this way, non-word characters are replaced by "_".  e.g. `-my.goofy-$-filename.txt` => `my_goofy___filename_txt`.

** * Note: * ** The .html extension is removed from html files, all other extensions are preserved (but `file.txt` => `file_txt`, as
explained above)


### Even iterate over static assets, since everything is a node!

``` jinja
{% for image in site.static.image %}
<img src="{{ image.url }}" />
{% endfor %}
```

You can check what kind of node you're working with using the `type` property ("page", "folder", "asset") or the `is_page`, `is_folder`, `is_asset` methods.

Lastly, the `.all()` method on folders is useful.  The method definition says it all I think:

``` python
def all(self, folders=False, pages=True, assets=False, recursive=False):
    """ Returns descendants, ignoring iterability. Folders, assets, and
    pages can all be included or excluded as the case demands."""
```


AND THAT'S IT
-------------

jinja2 makes it easy to put complicated logic in templates, which is really the only place for them in this static generator context...

...or is it !?  I’m wondering what kind of spaghetti nonsense these templates could end up with (it's like PHP all over again!), and how that could be fixed.


TODO
----

* Add page processors, so that you could build a categories index page based on pages' category metadata.
* Placing entries in `**/config.yaml` override parent configs, but i'd like to add a merging syntax to the YAML, as a little DSL.
