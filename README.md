The Strange Case of...
======================

It's yet another static site generator.  Have you seen [jekyll](https://github.com/mojombo/jekyll)?
[hyde](http://ringce.com/hyde)?  Yup.  Like those.

But this one is:

1. Written in python, unlike `jekyll`
2. **NOT** complicated, unlike `hyde`.  And I mean *really* **NOT** complicated.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

QUICK START
-----------

1. In your project folder, make a `site` and `public` folder.
2. Put index.j2 in site, and put some html in there.
3. Add YAML front matter to that file.  It looks like this:

```jinja
---
title: My first StrangeCase site
---
<!doctype html>
...
```

4. Use that YAML in your page using [jinja2](http://jinja.pocoo.org/)'s template language syntax:

```jinja
---
title: My first StrangeCase site
---
<!doctype html>
<h1>{{ title }}</h1>
```

5. Run strange case:
   `$ python /path/to/strange_case.py`

6. Open `public/index.html`.  You might want to hold onto your jaw, lest it drop to the floor.  Yeah, it's not gonna say `{{ title }}`,
   it's gonna say `My First Page` in big letters.


 SLOWER START
--------------

Whoopity freakin' do, right?  Let's add a layout and create a site.

At this point this demo site looks like this:

```
project
├── public
│   └── index.html
└── site
    └── index.j2
```

Add a layouts folder, and put a layout in there:

```
project
├── layouts
│   └── base.j2
├── public
│   └── index.html
└── site
    └── index.j2
```

layouts/base.j2 looks like this:

```jinja
<!doctype html>
<head>
  <title>{{ title or "Nifty Wow!" }}</title>
</head>
<body>
{% block content %}
{% endblock %}
</body>
```

And update index.j2 to use this layout:

```jinja
---
title: My first StrangeCase site
---
{% extends "layouts/base.j2" %}
{% block content %}
<h1>{{ title }}</h1>
{% endblock %}
```

You can run StrangeCase again.  public/index.html will now have <head> and <body> tags surrounding it.

If you're lost at this point, you should read up on Jinja.  We haven't really done anything more than run
index.j2 through jinja and wrote the output to index.html.

Now let's add a projects folder and a couple projects.  When you add *content* to your site, put it in
the site/ folder.  Most simple projects will pretty much only use the site/ folder.

I'm going to throw a curveball into the project file names.  StrangeCase orders files by sorting them by file
name.  This is important when you go to display images or blogs in order by date.  If you want to have them
ordered by anything other than filename, you can use a couple different naming schemes at
the beginning of the file name.  jekyll does a similar thing, btw.

I'm going to add *two* prefixes so we can see what happens when we process files this way.

```
project
├── layouts
│   └── base.j2
├── public
│   └── index.html
└── site
    ├── index.j2
    └── projects
        ├── 001_2012_02_27_first_project.j2   #
        ├── 002_2012_02_28_second_project.j2  # look over here!
        └── 003_2012_02_27_third_project.j2   #
```

And here is what each project template looks like:

```jinja
{% extends "layouts/base.j2" %}

{% block content %}
<h1>{{ title }}</h1>
<p>Project number #{{ order }} started on {{ created_at | date }}</p>
{% endblock %}
```

A little shorter than our original index.j2.  Notice I've left out the YAML front matter, and yet I
am using the variables `title`, `order`, and `created_at`.  Where do they get their value from?  The file name!

```
001_2012_02_27_first_project
\+/ \---+----/ \-----+-----/
 |      |            |
 |      |            +-title
 |      |
 |      +-created_at
 |
 +-order
```

You get a few variables for free just by naming your files with a date or order prefix.
Later, you'll be able to write your a function that does this and more!  We are looking
at the by-product of “configurators”, and they can access and modify the entire config.

BUT, if you tried to run StrangeCase right now, you would get the following error:

```shell
$ python /path/to/strange_case.py
...
jinja2.exceptions.TemplateAssertionError: no filter named 'date'
```

No worries, there is a `date` filter built into StrangeCase.  It's just not enabled. So
add a config.yaml file to the project root

```
project
├── config.yaml
├── layouts
│   └── base.j2
├── public
│   └── index.html
└── site
    ├── index.j2
    └── projects
        ├── 001_2012_02_27_first_project.j2
        ├── 002_2012_02_28_second_project.j2
        └── 003_2012_02_27_third_project.j2
```

and add the date filter:

```yaml
filters:
  date: extensions.date_extension.date
```

```shell
$ python /path/to/strange_case.py
$  # success!
```

```html
<!doctype html>
<head>
  <title>Nifty Wow!</title>
</head>
<body>

<h1></h1>
<p>Project number #1 started on 27 Feb 2012</p>

</body>
```

Moving along.  Now let's create a project listing at projects/index.j2.  We need a way
to "fetch" the project pages.  This is going to be very easy, because really all that
StrangeCase *does* is build a resource tree.  And we can walk that tree using the node
names.  So if we just iterate over the projects folder, we'll have our project nodes.

Add index.j2 to site/projects/

```
project
├── config.yaml
├── layouts
│   └── base.j2
├── public
│   └── index.html
└── site
    ├── index.j2
    └── projects
        ├── index.j2    # <===
        ├── 001_2012_02_27_first_project.j2
        ├── 002_2012_02_28_second_project.j2
        └── 003_2012_02_27_third_project.j2
```

```jinja
{% extends "layouts/base.j2" %}

{% block content %}
{% for project in site.projects %}
<p><a href="{{ project.url }}">{{ project.title }}</a></p>
{% endfor %}
{% endblock %}
```

Iterating over folders is a very important thing in StrangeCase.  It's how
you do things like create an index page, as we saw here,
or create a photo blog (`for photo in site.images.my_fun_trip`).  It is what I
found very frustrating in `jekyll` and `hyde` (especially `jekyll`), and so
it's what is *very easy* in StrangeCase.

Notice that when we iterate over the `site.projects` folder, it does *not*
include the index file.  Makes sense, though, right?  The index page is considered
to be the same "page" as the folder.  Even though they are seperate nodes, they have
the same URL.

To wrap things up, let's make a link to the project page from the home page.  Every node
has a `url` property, and you can access pages by their name.  "name" is whatever is "leftover"
after the created_at date and order have been pulled out.  I'll add a link to the second project
to demonstrate this.

```jinja
---
title: My first StrangeCase site
---
{% extends "layouts/base.j2" %}
{% block content %}
<h1>{{ title }}</h1>
<p><a href="{{ site.projects.url }}">Projects</a></p>
<p>My favorite project: <a href="{{ site.projects.second_project.url }}">My second project</a></p>
{% endblock %}
```


This wraps up the tutorial!  Next, I'll explain the inner workings.


 BUT FIRST
-----------

`python /path/to/strange_case --watch` is very useful. :-)


 WHA' HAPPENED?
----------------

Here is the basic 1-2-3 of what StrangeCase does when you run it.

### 1 - Build stage

In the build stage, StrangeCase is looking at the files and folders in site/.  First a root node is created:

```python
root_node = build_node(config, site_path, deploy_path, '')[0]
```

The `build_node` method **configures** and **processes** the node.  **configures** means that it passes the `source_path`
and `config` to each of the `configurators` (we saw these working in the tutorial above: `date_from_name`,
`order_from_name`, and `title_from_name` in particular).  **processes** means that one or more nodes are instantiated.

This process continues recursively for every file and folder in site (except `ignore`-d files).

### 2 - Populating

If you are using the category processor (or tags, archive, etc), this stage is important.  If you're not, it won't matter.

Some nodes can't know what content they will generate until the entire site is scanned.  These nodes are called `ProcessorNode`s,
and they are nodes that say "hold on, I'm not ready yet...".  They must implement a `populate` method, which when called *removes*
the processor node from the tree and replaces itself with nodes (or it can insert nodes elsewhere in the tree, or do nothing I suppose).

### 3 - Generating

At this point all the nodes are instantiated and are arranged in a tree structure, with the root node at the top.  The `generate`
method is called on the root node, and recursively on all the children.  This is where folders are created, pages are generated, and
assets are copied over.  If you are using the image processor, you might also have thumbnails created.


 OK, SO
--------

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

* Based on the file name, config.yaml, and YAML front matter, a few config settings get changed.  This part
  happens during the configuration stage, by `configurator` methods.


DEFAULT/SPECIAL CONFIG
----------------------

```yaml
  config_file: 'config.yaml'  # name of file that contains config
  host: "http://localhost:8000"  # hostname.  I'm not using this for anything, but it might be import for plugin authors one day
  index: index.html  # any file whose target_name matches this name will not be iterable
  ignore: ['config.yaml', '.*']  # which files to ignore altogether while building the site
  dont_process: ['*.js', '*.css', *images]  # do not run these files through jinja
  dont_inherit: [  # nodes should not inherit these properties
    # these are all assigned during the build/configure stage
    'type',
    'name',
    'target_name',
    'title',
    'created_at',
    'order',
  ]
  rename_extensions: {  # which extensions to rename, and how
    '.j2': '.html',
    '.jinja2': '.html'
  }
  html_extension: '.html'  # files with this extension are html files (`page.is_page` => `True`)

  # PROTECTED
  # these can only be assigned in the root config file, otherwise they will
  # be treated as plain ol' file data
  site_path: 'site/'  # where to find site content
  deploy_path: 'public/'  # where to put the generated site
  extensions: []  # list of jinja2 extension classes as a dot-separated import path
  filters: {}  # dictionary of `filter_name: filter.method`.
  processors: []  # additional processors.  Processors register themselves as a certain type.
  configurators: [  # list of configurators.  The built-ins do very importan things, so overriding this does *bad things*
    configurators.ignore,                  # ignores files based on the 'ignore' setting
    configurators.merge_files_config,      # merges files[filename] with filename
    configurators.setdefault_name,         # if 'name' isn't assigned explicitly, this assigns it based on the file name and extension
    configurators.setdefault_target_name,  # similarly for target_name
    configurators.folder_pre,              # processes folder/config.yaml.  If the folder config contains `ignore: true`, the folder is skipped
    configurators.file_pre,                # processes YAML front matter.  Again, the file can be ignored using `ignore: true`
    configurators.date_from_name,          # Gets the date from the file name, and strips it from name.
  ]
  configurators +: []  # to solve the problem of not changing 'configurators', you can put additional configurators in here.
```

RUNNING StrangeCase
-------------------

`$ python /path/to/strange_case.py`


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

```yaml
meta:
  author:
    name: "Colin"
```

`/site/index.html`:

```jinja
---
# YAML front matter
title: test
---

<h1>{{ meta.author.name }}</h1>
<h2>{{ title }}</h2>
<h2>{{ my.title }}</h2>
```

=>

```html
<h1>Colin</h1>
<h2>test</h2>
<h2>test</h2>
```

### Access any page by name:

(This is a common thing to do in StrangeCase)

```jinja
<a href="{{ site.blogs.best_blog_ever.url }}">Best blog ever</a>.
```

In order to access pages this way, non-word characters are replaced by "_".  e.g. `-my.goofy-$-filename.txt` => `my_goofy___filename_txt`.

** * Note: * ** The .html extension is removed from html files, but all other extensions are preserved.  So `file.txt` => `file_txt` (since
"." is a special character).


THIS IS COOL AND SO WORTH POINTING OUT
--------------------------------------

### You can iterate over folders:

```jinja
{% for blog in site.blogs %}
<p>{{ loop.index }}. {{ blog.title }}</p>
{% endfor %}
```

=>

```html
<p>1. Blog Title</p>
<p>2. Blog Title</p>
```

** * Note: * ** Files named `index.html` will not be included in this list.  This is a
very reasonable design decision, but I can imagin a situation where you have a file (think
`robots.txt`) that *also* doesn't belong in the iterable pages list.  So `iterable: false` is
available as a config setting.


### Iterate over a folder of images

```jinja
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

```python
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

```python
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

You can define `extensions`, `filters`, "configurators", and `processors`.

`filters` is a dictionary of `filter_name: package.path`.

`extensions` is a list of `- package.paths`.

If you specify these in config.py, you can import the extension/filter and assign it to the list.  Otherwise, in config.yaml,
use a dot-separated path, similar to how you would write an `import` statement, but include the class name.

There are a couple built-in processors that are not imported & registered by default: categories and image.

In config.py, you can add context variables that need the **POWER OF PYTHON**.  Things like datetime.time().
I might add a way to do this in the YAML, but *probably not* (unless the community argues for its inclusion).


Example of all this nonsense using `config.py`:

```python
from strange_case_config import CONFIG
from processors import image, categories
from extensions.Markdown2 import Markdown2Extension, markdown_filter
from datetime.datetime import time

CONFIG.update({
    'extensions': [Markdown2Extension],
    'filters': {
        'markdown': markdown_filter,
    },
    'processors': [image, categories]
    'time': int(time()),
})
```

Equivalent in the root `config.yaml`:

```yaml
extensions:
  - extensions.Markdown2.Markdown2Extension
filters:
  markdown: extensions.Markdown2.markdown_filter
processors:
  - processors.image
  - processors.categories
# cannot assign time to datetime.time.  DANG.
```

`processors/categories.py` has an explanation of how processors work, and how it was written.
I made it up as I went along, and ended up adding a `Processor` class that extends `Node`,
and a concept of "populating" the tree after the initial build.  Read more in that file.  I
think it's a good system, but I'm open to friendly suggestions.

Last but not least: configurators.  These are really the work horses of StrangeCase.  They
look at YAML front matter, ignore files, set default processors, and so on.  If you need to
do the equivalent of a context processor in django, this is where you would do that.

Every configurator in `config['configurators']` is given the node config.  If it returns nothing,
the node is skipped.  Otherwise, you can modify the config, or create a new one, and return it.

See `date_from_name` for a good example of modifying the config based on the file name.


TODO
----

* Placing entries in `**/config.yaml` override parent configs, but i'd like to add a merging syntax to the YAML, as a little DSL.

LICENSE
-------

Copyright (c) 2012, Colin Thomas-Arnold
All rights reserved.

See [LICENSE](https://github.com/colinta/StrangeCase/blob/master/LICENSE) for more details (it's a simplified BSD license).
