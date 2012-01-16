The Strange Case...
===================

It's yet another static site generator.  Have you seen jekyll?  hyde?  Yup.  Like those.

But this one is:

1. Written in python, unlike `jekyll`
2. **NOT** complicated, unlike `hyde`.  and I mean *really* **NOT** complicated.


OK, SO
-------

* `config.yaml` stores context variables.
* `site/` stores site content - templates and assets.  These are processed or copied or ignored, as the case may be.
* `config.yaml` files in a folder within `site/` override settings in the parent folder.  config is merged with the default config (see below - it's simple, too!).
* `./` is the "root" afa template includes go:
  * layouts can go in `layouts/` and are extended using `{% extends 'layouts/file.j2' %}`
  * includes can go in `anywhere/` and are included using `{% include 'anywhere/file.j2' %}`
  * see? only `site/` is special.  everything else is up to you.


DEFAULT CONFIG
--------------

'host': hostname (http://localhost:8000)
'ignore': which files to ignore altogether (['config.yaml', '.*'])
'dont_process': do not run these files through jinja (['*.js', '*.css', *images])
'rename_extensions': which extensions to rename ({'j2': 'html'})


EXECUTING
---------

`$ python strange_case.py`

Goes through all the files and directories in site/

* Folders become "FolderNode" objects (site/ is such a node).  folders have children
* Templates (jinja2 templates - or any text file) become TemplatePageNode(PageNode) objects
* Assets (css, js, images - anything that isn't a template) become AssetPageNode(PageNode) objects


Files can have metadata either as front matter, or in that folder's config.yaml in the parent folder, in a "files" entry (this is so that static assets can have metadata).  because of this, "files:" in the yaml files are not copied as context variables.


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

### In your templates, you have access anything in the top-level config and in per-page metadata:

`/config.yaml`:

``` yaml
meta:
  author:
    name: Colin
```

`/site/index.html`:

``` jinja
---
# front matter
title: test
---

{{ meta.author.name }}
{{ title }}
```

=>

    Colin
    test


### You can iterate over folders:

``` jinja
{% for blog in site.blogs %}
{{ loop.index }}. {{ blog.title }}
{% endfor %}
```

### Or access a page by name (filename w/o ext):

``` jinja
{{ site.blogs.test1.url }}
```

### Iterate over static assets:

``` jinja
{% for image in site.static.image %}
<img src="{{ image.url }}" />
{% endfor %}
```

AND THAT'S IT
-------------

jinja2 makes it easy to put logic in these templates, which is really the only place for them...

...or is it !?  I’m wondering what kind of spaghetti nonsense these templates could end up with (it's like PHP all over again!), and how that could be fixed.


TODO
----

* Add page processors, so that you could build a categories index page based on pages' category metadata.
* Placing entries in .../config.yaml override parent configs, but i'd like to add a merging syntax similar to what we have in fbmvc (`key ?:`, `key !:`, `key -:` ...)
