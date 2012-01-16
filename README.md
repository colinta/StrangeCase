The Strange Case...
===================

It's yet another static site generator.  Have you seen jekyll?  hyde?  Yup.  Like those.

But this one is:

1. Written in python, unlike `jekyll`
2. **NOT** complicated, unlike `hyde`.  and I mean *really* **NOT** complicated.


First, the complicated stuff:

* Index pages are not iterable, except by using `page.all()`
* Index pages' URLs do not include the filename.  This means they have the same name
  as the folder they index.  That's good, right?
* For fun, you can prefix variables on a page with `my.`
  I think it looks better, and `self` was taken.


Now for the easy stuff!


OK, SO
-------

* `config.yaml` stores context variables.
* `site/` stores site content - templates and assets.  These are processed or copied or ignored, as the case may be.
* `config.yaml` files in a folder within `site/` override settings in the parent folder.  config is merged with the default config (see below - it's simple, too!).
* `./` is the "root" afa template includes go:
  * layouts can go in `layouts/` and are extended using `{% extends 'layouts/file.j2' %}`
  * includes can go in `anywhere/` and are included using `{% include 'anywhere/file.j2' %}`
  * see? only `site/` is special.  everything else is up to you.


DEFAULT/SPECIAL CONFIG
----------------------

``` yaml
  host: "http://localhost:8000"  # hostname
  index: index.html  # any file whose target_name matches this name will not be iterable (by default)
  ignore: ['config.yaml', '.*']  # which files to ignore altogether
  dont_process: ['*.js', '*.css', *images]  # do not run these files through jinja
  rename_extensions: { '.j2': '.html', '.jinja2': '.html' }  # which extensions to rename
  html_extension: '.html'  # files with this extension are html files (`page.is_page` => `True`)
```


EXECUTING
---------

`$ python strange_case.py`

Goes through all the files and directories in `site/`

* Folders become `FolderNode` objects (`site/` is such a node).  Folders have children.
* Templates (jinja2 templates - or any text file) become `TemplatePageNode(PageNode)` objects
* Assets (css, js, images - anything that isn't a template) become `StaticPageNode(PageNode)` objects

Files can have metadata either as front matter, or in that folder's `config.yaml` in the parent folder, in a `files` entry.
The `files` is so that static assets can have metadata.  Because of this, `files:` in the `config.yaml` files are not
copied or merged with child or parent settings.  That's the only special config other than those above.


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
```

=>

``` html
<h1>Colin</h1>
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

** * Note: * ** Files named `index.html` will not be iterable by default.  This is a
*good thing* when making index.html files.  If you don't like it, set `iterable: true`
in your front matter.


### Access any page by name:

``` jinja
{{ site.blogs.test1.url }}
```

** * Note: * ** The .html extension is removed, but in order to have unique names, all other
file types have their extension added.

Also, in order to access pages this way, non-word characters are replaced by "_".  e.g. `-my.goofy-$-filename.txt` => `my_goofy___filename_txt`.

### Even iterate over static assets, everything is a node!

``` jinja
{% for image in site.static.image %}
<img src="{{ image.url }}" />
{% endfor %}
```

You can check what kind of node you're working with using the `type` property ("page", "folder", "asset") or the `is_page`, `is_folder`, `is_asset` methods.


AND THAT'S IT
-------------

jinja2 makes it easy to put complicated logic in templates, which is really the only place for them in this static generator context...

...or is it !?  I’m wondering what kind of spaghetti nonsense these templates could end up with (it's like PHP all over again!), and how that could be fixed.


TODO
----

* Add page processors, so that you could build a categories index page based on pages' category metadata.
* Placing entries in `**/config.yaml` override parent configs, but i'd like to add a merging syntax to the YAML, as a little DSL.
