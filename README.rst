.. image:: https://travis-ci.org/colinta/StrangeCase.png?branch=master :target: https://travis-ci.org/colinta/StrangeCase

======================
The Strange Case of...
======================

It's yet another static site generator.  Have you seen `jekyll`_?
`hyde`_?  Yup.  Like those.

But this one is:

1. Written in python, unlike ``jekyll``
2. **NOT** complicated, unlike ``hyde``.  And I mean *really* **NOT** complicated.

I just read about `nanoc`_, and realized that it is the Ruby equivalent to
StrangeCase.  I commend them!  I had considered porting StrangeCase to Ruby
(and maybe I will some day, just for kicks), but for now, I would say to
Rubyists: use `nanoc`_.


------------
INSTALLATION
------------

::

    $ pip install StrangeCase
    $ scase  # generates the site
    $ scase --watch  # generates the site and watches
                     # for changes to source files


-----
HELP!
-----

Already!?  Geez::

    #strangecase @ irc.freenode.net

    (i'm colinta)


-----------
QUICK START
-----------

1. In your project folder, make a ``site/`` and ``public/`` folder.
2. Put ``index.j2`` in ``site/``, and put some html in there.
3. Add YAML front matter to that file.  It looks like this::

    ---
    title: My first StrangeCase site
    ---
    <!doctype html>
    ...

4. Use that YAML in your page using `Jinja2`_'s template language syntax::

    ---
    title: My first StrangeCase site
    ---
    <!doctype html>
    <h1>{{ title }}</h1>

5. Run strange case:
   ``$ scase``

6. Open ``public/index.html``.  You might want to hold onto your jaw, lest it
   drop to the floor.  Yeah, it's not gonna say ``{{ title }}``, it's gonna say
   ``My First Page`` in big letters.


------------
SLOWER START
------------

Whoopity freakin' do, right?  Let's add a layout and create a site.

At this point this demo site looks like this::

    project
    ├── public
    │   └── index.html
    └── site
        └── index.j2

Add a layouts folder, and put a layout in there::

    project
    ├── layouts
    │   └── base.j2
    ├── public
    │   └── index.html
    └── site
        └── index.j2

``layouts/base.j2`` looks like this::

    <!doctype html>
    <head>
      <title>{{ title or "Nifty Wow!" }}</title>
    </head>
    <body>
    {% block content %}
    {% endblock %}
    </body>

And update ``index.j2`` to use this layout::

    ---
    title: My first StrangeCase site
    ---
    {% extends "layouts/base.j2" %}
    {% block content %}
    <h1>{{ title }}</h1>
    {% endblock %}

You can run StrangeCase again.  ``public/index.html`` will now have ``<head>``
and ``<body>`` tags surrounding it.

If you're lost at this point, you should read up on Jinja.  We haven't really
done anything more than run ``index.j2`` through jinja and wrote the output to
``index.html``.

Now let's add a projects folder and a couple projects.  When you add *content*
to your site, put it in the ``site/`` folder.  Most simple projects will pretty
much only use the ``site/`` folder and a ``layouts/`` folder wth one or two
layouts in there.

I'm going to throw a curveball into the project file names.  StrangeCase orders
files by sorting them by file name.  This is important when you go to display
images or blogs in order by date.  If you want to have them ordered by anything
other than filename, you can use a couple different naming schemes at the
beginning of the file name.  jekyll does a similar thing, btw.

I'm going to add *two* prefixes so we can see what happens when we process
files this way.

::

    project
    ├── layouts
    │   └── base.j2
    ├── public
    │   └── ...
    └── site
        ├── index.j2
        └── projects
            ├── 001_2012_02_27_first_project.j2   #
            ├── 002_2012_02_28_second_project.j2  # look over here!
            └── 003_2012_02_27_third_project.j2   #

And here is what each project template looks like::

    {% extends "layouts/base.j2" %}

    {% block content %}
    <h1>{{ title }}</h1>
    <p>Project number #{{ order }} started on {{ created_at | date }}</p>
    {% endblock %}

A little shorter than our original ``index.j2``.  Notice I've left out the YAML
front matter, and yet I am using the variables `title`, `order`, and
`created_at`.  Where do they get their value from?

The file name, and configurators.

::

    001_2012_02_27_first_project
    \+/ \---+----/ \-----+-----/
     |      |            |
     |      |            +-title
     |      |
     |      +-created_at
     |
     +-order

In this way, you get some variables for free just by naming your files with a
date and/or order prefix.  We are looking at the by-product of “configurators”.
They are passed the source file name and the config dictionary.  There are some
that *have* to run, and some that are optional but enabled by default.

Anyway, if you tried to run StrangeCase right now, you would get the following
error::

    $ scase
    ...
    jinja2.exceptions.TemplateAssertionError: no filter named 'date'

No worries, there is a `date` filter built into StrangeCase.  It's just not
enabled. So add a config.yaml file to the project root::

    project
    ├── config.yaml
    ├── layouts
    │   └── base.j2
    ├── public
    │   └── ...
    └── site
        ├── index.j2
        └── projects
            ├── 001_2012_02_27_first_project.j2
            ├── 002_2012_02_28_second_project.j2
            └── 003_2012_02_27_third_project.j2

and add the date filter::

    filters:
      date: strange_case.extensions.date.date

*Now* you can run StrangeCase with no errors, which will generate::

    <!doctype html>
    <head>
      <title>Nifty Wow!</title>
    </head>
    <body>

    <h1></h1>
    <p>Project number #1 started on 27 Feb 2012</p>

    </body>

Moving along.  Now let's create a project listing at ``projects/index.j2``.  We
need a way to "fetch" the project pages.  This is going to be very easy,
because really all that StrangeCase *does* is build a resource tree.  And we
can walk that tree using the node names.  So if we just iterate over the
``projects/`` folder, we'll have our project nodes.

Add ``index.j2`` to ``site/projects/`` ::

    project
    ├── config.yaml
    ├── layouts
    │   └── base.j2
    ├── public
    │   └── ...
    └── site
        ├── index.j2
        └── projects
            ├── index.j2    # <===
            ├── 001_2012_02_27_first_project.j2
            ├── 002_2012_02_28_second_project.j2
            └── 003_2012_02_27_third_project.j2

``index.j2``::

    {% extends "layouts/base.j2" %}

    {% block content %}
    {% for project in site.projects %}
    <p><a href="{{ project.url }}">{{ project.title }}</a></p>
    {% endfor %}
    {% endblock %}

Iterating over folders is a very easy thing to do in StrangeCase.  It's how you
do things like create an index page, as we saw here, or create a photo blog
(``for photo in site.images.my_fun_trip``).  It is the thing that I wanted to be
*really* easy, because I couldn't figure out, at a glance, how to do it in
jekyll or hyde (it is possible in hyde, I think).

Notice that when we iterate over the ``site.projects`` folder, it doesn't
include the ``index.html`` file.  Makes sense, though, right?  The index page
is considered to be the same "page" as the folder.  Even though they are
seperate nodes, they have the same URL.

To wrap things up, let's make a link to the project page from the home page.
Every node has a ``url`` property, and you can access pages by their name.
"name" is whatever is "leftover" after the created_at date, order and extension
have been pulled out.  I'll add a link to the second project to demonstrate
this::

    ---
    title: My first StrangeCase site
    ---
    {% extends "layouts/base.j2" %}
    {% block content %}
    <h1>{{ title }}</h1>
    <p><a href="{{ site.projects.url }}">Projects</a></p>
    <p>My favorite project: <a href="{{ site.projects.second_project.url }}">My second project</a></p>
    {% endblock %}


This wraps up the tutorial!  Now, I'll explain the inner workings.

---------------
TIPS AND TRICKS
---------------

Here are some quick little neat things.

1. You'll need a good, solid config.yaml.  Just copy and paste this when you
   start a new site::

       extensions:
         - strange_case.extensions.misaka.MarkdownExtension
       filters:
         date: strange_case.extensions.date.date
         markdown: strange_case.extensions.misaka.markdown
         json: json.dumps
         sha: strange_case.extensions.hashlib.sha
       processors:
         - strange_case.extensions.image
         - strange_case.extensions.category
         - strange_case.extensions.paginated
         - strange_case.extensions.scss

2. Iterate over a folder of pages, or a folder of assets, using
   ``{% for page in site.folder.subfolder %}``.  There is no "easy" way to
   iterate over a folder that contains folders - what you really want there is
   to get the index file of the folder, it will contain the meta data (title,
   created_at, etc) that you probably want to display in the listing.  I will
   try and fix this, but probably won't until someone asks for it.

3. Do not mix pages and assets.  You *can* do it, but things get goofy when you
   try and iterate over the folder.  If you ``{% for page in site.folder %}``,
   you will end up with *both* types of file.  If you *really* want to mix them,
   you can iterate over just the pages (and exclude index.html files) using
   ``iter_pages``, introduced in v4.3.0.

4. You can assign "pointers" in your YAML front matter.  They look like this::

       page ->: site.other.page

   If your asset folders are getting unwieldy
   (``site.static.images.posts.pics_of.kittens``), use this trick to shorten it
   down in your template.  In this case you *must* prefix the pointer with
   ``my.``, because jinja will not know how to lookup "page ->" when you say
   only "page", and I have not devised a workaround yet::

       ---
       pics ->: site.static.images.posts.pics_of.kittens
       ---
       {% for pic in my.pics %}
         <img src="{{ pic.url }}">
       {% endfor %}

5. Page content is simply not available during template generation.  For that, I
   can't help you.  That would introduce page dependencies, which would suck.

   If you want a "blurb" or "summary" of a page's content, you'll just have to
   add it to the page front matter::

       ---
       title: my post
       summary: |
         I think this post is great.  It's all about code:

             print "like this"
       ---

   Back in your listing, you can run that summary through markdown using a
   filter::

       {% for post in site.posts %}
       <h3>{{ post.title }}</h3>
       {% if post.summary -%}
       <div class="summary">
         Summary:<br />
         {{ post.summary|markdown }}
       </div>
       {% endif %}

6. As of v4.5.0, you do not have to have a ``CONFIG`` dict in your config.py
   file.  Instead, you can create or import functions into that file, and then
   reference them from your project's config.yaml.  For instance, to add a
   ``pluralize`` filter to your project::

       # config.py
       import inflect ; inflect = inflect.engine()

       pluralize = inflect.plural

       # config.yaml
       filters:
         pluralize: config.pluralize

   Interestingly, this was a complete accident.  But I've added a test for it,
   so it's here to stay! :-)

7. Sometimes you will want to override values, but ``dont_inherit`` gets in the
   way.  In those instances, you can add values to ``override``, usually in a
   folder ``config.yaml``.  One common case is to set a folder of images'
   ``title`` to ``""``.  The default configurators would set the title based
   on the name of the file (``title_from_name`` configurator), but it will *not*
   if the title is set to anything, even ``""``.

8. ??? I'll add to this list as needed.

--------------------
STRANGECASE OVERVIEW
--------------------

StrangeCase parses all the files and directories in ``site/`` and builds a tree
of nodes.  At its big, squishy heart, that's what StrangeCase does.  Then it
runs ``generate`` on every node.

* Files/Folders that match ``ignore`` are not processed at all.
* Folders become ``FolderNode`` objects (``site/``, though, is a ``RootNode``)
  and scanned recursively.
* Pages (html and jinja files) become ``JinjaNode(FileNode)`` objects.
* Assets (javascript, css, images) become ``AssetNode(FileNode)`` objects.
* These can be overridden using the ``type`` config.
* Additional nodes can be created by including the appropriate processor and
  setting the node's ``type`` to use that processor.  These are things like
  pagination, tags, images, and categories.

The nodes are placed in a tree::

    (root, aka site)                    # RootNode
    | static/                           # FolderNode
    | | css/                            # FolderNode
    | | + style.css                     # AssetNode
    | \ image/                          # FolderNode
    |   | img1.png                      # AssetNode (or possibly ImageNode)
    |   | img2.png                      # AssetNode
    |   + img3.png                      # AssetNode
    | robots.txt                        # PageNode
    | index (index.j2 => index.html)    # PageNode
    \ blogs/                            # FolderNode
      | test1 (test1.j2 => test1.html)  # PageNode
      + test2 (test2.j2 => test2.html)  # PageNode

-------------------
SOO? WHA' HAPPENED?
-------------------

1 - Build stage
~~~~~~~~~~~~~~~

In the build stage, StrangeCase is looking at the files and folders in site/.
First a root node is created::

    root_node = build_node(config, site_path, deploy_path, '')[0]

The ``build_node`` method **configures** and **processes** the node.
**configures** means that it passes the ``source_path`` and ``config`` to each
of the ``configurators`` (we saw these working in the tutorial above:
``created_at_from_name``, ``order_from_name``, and ``title_from_name`` in
particular).  **processes** means that one or more nodes are instantiated and
added to the node tree.  The ``root_node`` sits at the top, and in your
templates you access it using ``{{ site }}``.

This process continues recursively for every file and folder in site (except
``ignore``-d files).

1.a - Configuration
~~~~~~~~~~~~~~~~~~~

When you run StrangeCase, it starts building a config object, a dictionary
(actually an instance of ``ConfigDict``, which extends ``dict``). This object
(and clones of it) will be used throughout the generation of your site, so it is
important to understand what it does, and how you control it.

First, ``strange_case_config.py`` establishes the initial defaults.  Look at
that file, or read about the defaults below.  Next, the project config file is
merged in.  This is the ``config.yaml`` file that sits at the top of your
project.  Then command-line arguments are processed.  **Finally**, if a function
is assigned to ``config_hook``, it will be passed the configuration, and it is
expected to throw errors or make changes to that object as needed.  This is how
"scaffolding" is accomplished, which is actually just a StrangeCase extension
and a few handy ``site/`` folders.

When a new node is being built, it is given a copy of the config dictionary and
passed through the configurators.  These add properties to the config dict that
are specific to the node that is going to be built, including specifying *what
type* of node will be built.  The default list of configurators is in
``strange_case_config.py``.

Nodes inherit all the configuration of the parent node except for the keys that
are in ``dont_inherit`` (``name``, ``target_name``, ``type``, and most of the
properties that are assigned by configurators).

If the node is a folder, the special file config.yaml will be merged into that
node if it exists.  If it is a file node, the parent folder's config is checked
for a ``files`` entry, and if the current file is in there, that config is
merged in.

``page`` types can have YAML front matter, which we've read all about already.

See the section below that outlines the default config, and how those options
affect processing.  Know this: everything is controlled using config.  If you're
trying to do something complicated and having trouble, please create an issue.
I'd like to compile a list of HOWTOs/FAQs.

1.b - Processors
~~~~~~~~~~~~~~~~

During the build stage, page, folder, and asset nodes are created using
**processors**.  There are four built-in processors, and more available as
extensions.  One important thing to note here is that assets and pages are
differentiated only by the fact that one of them is passed through Jinja2.  If
you want to process a JavaScript file through Jinja2, you should associate
``*.js`` with the ``page`` type, or set ``type: page`` in the parent folder
config.yaml file (using the ``files:`` dictionary)::

    file_types:
        - [page, '*.js']
    # or, if you want to only process a couple files:
        - [page, ['special.js', 'special-2.js']]

    # or assign the 'page' processor
    files:
      special.js: { type: page }

``type`` is not inherited, but ``file_types`` is, so you can set a whole folder
of assets to become page nodes using this config.

Processors are kind of tricky to build, because they need to have a firm
understanding of the build process.  If you're feeling industrious, there are
plenty of existing extensions (category and pagination) that can push you in the
right direction.

2 - Populating
~~~~~~~~~~~~~~

If you are using the category processor this stage is important.  If you're not,
it won't matter so much.

Some nodes can't know what content they will generate until the entire site is
scanned.  Like categories!  We need to know *all* the pages in the site before
we know what all the categories are, and how many pages have that category.

These nodes are stored as ``Processor``s, and they are nodes that say "hold
on, I'm not ready yet...".  They must implement a ``populate`` method, which
when called *removes* the processor node from the tree and replaces itself with
nodes (or it can insert nodes elsewhere in the tree, or do nothing I suppose).

If you are writing your own processor, and need to access a node's config, you
might want to use the item-index operators, ``[]``.  If the configuration is not
set, you'll get ``None`` instead of an ``AttributeError``. ::

    node.thingy     # => AttributeError
    node['thingy']  # => None

After the tree is populated, the site is ready to generate.  You will have a
tree of nodes, with the root node at the top, and it is always named ``"site"``.

3 - Generating
~~~~~~~~~~~~~~

The ``generate`` method is called on the root node, and recursively on all the
children.  This is where folders are created, pages are generated, and assets
are copied over.  If you are using the image processor, you might also have
thumbnails created using `PIL`_.

---------
TEMPLATES
---------

In your templates, you have access to anything in the inherited config and in
per-page metadata:

``/config.yaml``::

    meta:
      author:
        name: "Colin"

``/site/index.j2``::

    ---
    title: test
    ---

    <h1>{{ meta.author.name }}</h1>
    <h2>{{ title }}</h2>
    <h2>{{ my.title }}</h2>

Generates::

    <h1>Colin</h1>
    <h2>test</h2>
    <h2>test</h2>

Node properties
~~~~~~~~~~~~~~~

Nodes have a number of useful properties, roughly grouped into:

* config/metadata like name, title, created_at.  This is the big one.
* website-specific - ``url``, ``index``, ``is_{page,asset,folder}``
* traversal - parents, children, siblings, iterable

**Config**

Hopefully by now the importance of the config object has been bored into your
head.  StrangeCase is all about the config object.  That, and the node tree.
And that's it.  Nothing else.  Oh, and templating.  Templating, config, and the
node tree.  That's all it needs.  That's it, that's... and this lamp.  That's
all.

In your templates, the configuration is simply "there".  The properties of the
current node and all the configuration it has inherited is given to jinja2 as
the context.  There is, however, *one* exception to this, which are "pointer"
configurations::

    ---
    images ->: site.static.images
    ---
    {{ images|length }}     # wrong
    {{ my.images|length }}  # right

I have not bothered to fix this, since I *prefer* the second syntax.  I use the
``my`` prefix anytime I'm referring to the YAML front matter - kind of keeps
things sane for me.  If people clamor for the pointer thing to get fixed it
wouldn't be too difficult.

**Website**

The most used is, of course, ``node.url``.  URLs are created by appending the
current node's URL to the parent URL.  The URL of the site node is assigned
by the ``set_url`` configurator, and defaults to ``/``.  If you want your static
site to be in a subfolder, assign something else to the ``root_url`` config.

There are other configs used internally, like ``is_page`` and ``index``.  These
are worth looking at.  ``is_page`` returns True when the node was processed
using Jinja - it does not mean that the page is an HTML page, so ``robots.txt``
and ``sitemap.xml`` will be included in there, too.  BUT hey!  You can fix that!
Add::

    ---
    is_page: false
    ---

And that node will be excluded, it will considered to be an asset instead.  An
asset is any file that is not a page.  If you want to set ``is_asset: true``
above, that is supported, and an infinite loop is avoided, but the "official"
stance is that ``is_asset := ! is_page``.

Accessing any node by name
~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a common thing to do in StrangeCase.  The ``name``, if it is not
explicitly declared, is detemined by the file name.  The default configurators
will remove ordering (``order_from_name``) and created_at
(``created_at_from_name``) from the front of the file name, and then the default
name (``setdefault_name``) will be the file name with non-alphanumerics replaced
with underscores, lowercased, and the html extension is removed.  All other
extensions will remain.  Examples:

``This is a file name - DUH.j2`` becomes ``this_is_a_file_name___duh``

``WHAT, a great image?.jpg`` becomes ``what__a_great_image_jpg``

Example of accessing the "Best blog ever" page's URL::

    <a href="{{ site.blogs.best_blog_ever.url }}">Best blog ever</a>.

All nodes except the root node (``site`` is the root node, if you haven't
noticed) have ``siblings`` nodes, a ``next`` node, and a ``prev`` node.  If this
is the first / last node, ``prev`` / ``next`` returns None.  ``siblings`` always
returns a list, and at the minimum the current node will be in there (even the
root node, but why you would call ``site.siblings`` is beyond me).

There is also an ``ancestors`` property, which returns all the parent pages of
the node.  BUT, in order to be the most useful, this method looks for a node
called ``index`` on the parents, so instead of getting a list of folder nodes,
you will get list of index pages.  If you're building a breadcrumb trail,
``ancestors`` is your friend, and you'll be glad that the index pages are
returned instead of folder nodes.

Iterating over folders
~~~~~~~~~~~~~~~~~~~~~~

We've already seen this, but I'll include it again for completeness::

    {% for blog in site.blogs %}
    <p>{{ loop.index }}. {{ blog.title }}</p>
    {% endfor %}

=> ::

    <p>1. Blog Title</p>
    <p>2. Blog Title</p>

**Note:** Files named ``index.html`` will not be included in this list.  This is
a very reasonable design decision, but I can imagine a situation where you have
a file (think ``robots.txt``) that *also* doesn't belong in the iterable pages
list.  So ``iterable: false`` is available as a config setting.

Iterate over a folder of images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    {% for image in site.static.image %}
    <img src="{{ image.url }}" />
    {% endfor %}

**BAM**, how's that for an image listing!  This might be my favorite thing in
StrangeCase: that folders are iterable.  It makes things that were weird in
jekyll (``site.categories.blablabla``) very easy, and intuitive, I think, since
you only have to know the folder name of your images/blogs/projects/*whatever*.

You might want to check out the image processor, explained below.  It uses
`PIL`_ to make thumbnail images.

You can check what kind of node you're working with using the ``type`` property
("page", "folder", "asset") or the ``is_page``, ``is_folder``, ``is_asset``
methods.  Internally ``is_page`` is used a lot, and if you mix your page and
asset files in the same folders, these are useful for filtering those out in a
for loop.

Lastly, the ``.all()`` method, and its more specific variants, are very useful
if you need to make a sitemap, or to grab the entire node tree at some point.
The ``all()`` method definition says it all I think::

    def all(self, recursive=False, folders=None, pages=None, assets=None, processors=None):
        """
        Returns descendants, ignoring iterability. Folders, assets, and
        pages can all be included or excluded as the case demands.

        If you specify any of folders, pages, assets or processors, only those objects
        will be returned.
        Otherwise all node types will be returned.

        recursive, though, defaults to False.  calling all(True) is the same as all(recursive=True)
        """

The variants are all subsets of ``all()``::

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

------
OK, SO
------

Mostly random thoughts here.  Most of what you might want to know about StrangeCase *should* be here, so expect some repetition.

* In your project folder (where you execute StrangeCase), you can have
  ``config.yaml`` and/or ``config.py``, and you *definitely* have a ``site/``
  folder, where your site content is stored.  There are probably Jinja2 layouts,
  includes, and who knows what else in the root folder, too.

* ``site/`` stores site content: templates, assets, folders, and maybe some
  "special" files like category pages. These are processed, rendered, copied, or
  ignored, as the case may be (dot-files are ignored, btw!).

* When StrangeCase is done it places your static site in ``public/``.

* There are only two special folders: site and public. They can be changed in
  config (``site_path`` and ``dest_path``).

* ``config.yaml`` stores context variables.  It is merged with the default
  config.  Child folders and pages inherit all the config settings of their
  parent except the variables in ``dont_inherit``:

  + ``type``
  + ``name``
  + ``target_name``
  + ``title``
  + ``created_at``
  + ``order``

* Template files (.html, .txt, .md) can contain YAML front matter.  If the first
  line is a bunch of dashes (``^[-]{3,}$``), all lines up to the matching dashes
  will be treated as YAML and added to that files context variables.

* Binary files can have front matter, too, but since you can't place it *in* the
  file, it is stored in a special ``files:`` setting in the parent folder's
  config.yaml file.  It should be a dictionary with the key corresponding to the
  name of the file, and the value is the front matter for that file.  ``files:``
  entries in ``config.yaml`` are not inherited.

* Everything in ``config.yaml`` and YAML front matter is available as a context
  variable in your templates.

* Templates are rendered using Jinja2_.

* StrangeCase points Jinja to your project folder, so you can use any
  directories you want in there to store layouts, macros, and partials.

  * layouts that are in ``layouts/`` are extended using ``{% extends 'layouts/file.j2' %}``
  * includes in ``anywhere/`` are included using ``{% include 'anywhere/file.j2' %}``
  * I suppose the convention is to have layouts/ and includes/ folders.

* In the project root, ``config.py`` is where you can place runtime things,
  like...

  * if you need to calculate a value (e.g. ``datetime.time``)
  * fetch some data from a database (*ewww!*)
  * import jinja extensions (or use 'extensions' in config.yaml)
  * import jinja filters (or use 'filters' in config.yaml)
  * register StrangeCase processors (or use 'processors' in config.yaml)

* If you need a page to be processed differently, set ``type`` to the desired
  file type in the config for that file/folder. For instance, the category index
  page should be ``type: categories``.

* You can prefix variables on a page with ``my.`` (e.g. ``my.title`` or
  ``my.parent``). I think it looks better in some places because it makes it
  clear where the content comes from (e.g. ``{{ my.title }}`` as opposed to just
  ``{{ title }}``).  Totally optional.

* Based on the file name, config.yaml, and YAML front matter, some config
  settings get changed during the build stage. See ``configurators.py`` for
  these methods.  See ``strange_case_config.py`` for the order.

--------------
DEFAULT CONFIG
--------------

You should study this to learn a lot about how StrangeCase works.  The reason I
boast that StrangeCase is simple is because *everything it does* can be
controlled using the config.

If you go looking in ``strange_case_config`` for these settings, you won't find
them.  They have been broken up into ``configurators``.  In the early life of
StrangeCase, all configuration was done in one file.   Now they are broken up
into a list of configurator functions, and each function can add defaults.  More
complicated, but more extensible.

::

    config_file: 'config.yaml'                # name of file that contains config
    ignore: ['config.yaml', '.*']             # which files to ignore altogether while building the site
    dont_inherit:                             # nodes will not inherit these properties
      - type
      - name
      - target_name
      - title
      - created_at
      - order
      - iterable
      - is_index
      - url
      - skip
    file_types:                                 # how files should be processed.  some processors add to this list, like to associate images
        - [page, ['*.j2', '*.jinja2', '*.jinja', '*.html', '*.txt', '*.xml']],   # with the image processor
    default_type: asset                       # if this is falsey, unassociated nodes will be ignored.
    default_root_type: root                   # you probably shouldn't change this!
    default_folder_type: folter               # you probably shouldn't change this!
    rename_extensions:                        # which extensions to rename, and to what
      '.j2': '.html',
      '.jinja2': '.html'
      '.jinja': '.html',
      '.md': '.html',
    index.html: index.html                    # determines which file is the index file, which in turn determines "iterability" (index pages are not iterable)
    html_extension: '.html'                   # files with this extension are html files (`page.is_page` => `True`)

    # PROTECTED
    # these can only be assigned in the root config file, otherwise they will
    # be treated as plain ol' file data
    site_path: 'site/'                        # where to find site content
    deploy_path: 'public/'                    # where to put the generated site
    remove_stale_files: true                  # removes files that were not generated.
    dont_remove: ['.*']                       # list of glob patterns to ignore when removing stale files
    extensions: []                            # list of Jinja2 extension classes as a dot-separated import path
    filters: {}                               # dictionary of `filter_name: filter.method`.
    processors: []                            # additional processors.  Processors register themselves as a certain type.
    configurators: [                          # list of configurators.  The built-ins do very important things, so overriding this does *bad things*
      meta_before,              # assigns defaults from the configurators ``.defaults`` property
      file_types,               # checks 'file_types' for a pattern that matches the file name
      page_types,               # if you want to use your own template engine, you'll need to add it to this list
      merge_files_config,       # merges files[filename] with filename
      folder_config_file,       # processes folder/config.yaml.  If the folder config contains `ignore: true`, the folder is skipped
      front_matter_config,      # processes YAML front matter.  Again, the file can be ignored using `ignore: true`
      setdefault_name,          # if 'name' isn't assigned explicitly, this assigns it based on the file name and extension
      setdefault_target_name,   # similarly for target_name
      is_index,                 # compares the file name with the 'index.html' config.  if they are the same, it is an index page.
      setdefault_iterable,      # index files are not iterable
      ignore,                   # ignores files based on the 'ignore' setting
      created_at_from_name,     # Gets the date from the file name, and strips it from name.
      order_from_name,          # Gets the order from the file name, and strips it from name.
      title_from_name,          # Assigns the "title" property based on the name.
      set_url,                  # Assigns the "local" part of the URL.  The entire URL is a property of the node object
    ]

--------------------
COMMAND LINE OPTIONS
--------------------

You can override configuration - or add to it - via the command-line.
Here are all the command line arguments:

    -p, --project:   project_path
    -s, --site:      site_path
    -d, --deploy:    deploy_path
    -r, --remove:    remove_stale_files = true (default, but this can override -n)
    -n, --no-remove: remove_stale_files = false
    -c, --config:    config_file

(and of course)

    -w, --watch:     watch files for changes

You can set/add arbitrary configuration using any number of ``key:value``
arguments::

    key:value         any key/value pair

I use this to implement a simple code generator for my Sublime Text 2 plugins.
I run::

    scase --deploy ../NewProject project:new_project desc:'A great new package'

See `My PackageTemplate <https://github.com/colinta/_SublimePackageTemplate_>`_
for an example of how this can be used.

---------------------------
AND THAT'S (pretty much) IT
---------------------------

Jinja2 makes it easy to put pretty complicated logic in templates, which is
really the only place for them in this static generator context...

\...or is it !?  I’m wondering what kind of spaghetti nonsense these templates
could end up with (it's like PHP all over again!), and how that could be fixed.

Which leads right into...

------------------------
REALLY COMPLICATED STUFF
------------------------

This relates to the ``config.py`` and ``config.yaml`` files mentioned above.

Take a glance at the colinta.com repository.  It does most things that can be
done.

You can define ``extensions``, ``filters``, "configurators", and ``processors``.

``filters`` is a dictionary of ``filter_name: package.path``.

``extensions`` is a list of ``package.paths``.

If you specify these in config.py, you can import the extension/filter and
assign it to the list.  Otherwise, in config.yaml, use a dot-separated path,
similar to how you would write an ``import`` statement, but include the class
name.

There are a couple built-in processors that are not imported & registered by
default: categories and image.

In config.py, you can add context variables that need the **POWER OF PYTHON**.
Things like ``time.time(), datetime.datetime.now()``.

Example of all this nonsense using ``config.py``::

    # import the processors you want to use.  you don't have to do anything with them,
    # it is enough just to import them.
    from strange_case.extensions import image, categories

    # import the extensions and filters.  we still need to add these to CONFIG
    from strange_case.extensions.markdown import MarkdownExtension, markdown
    from time import time

    CONFIG.update({
        'extensions': [MarkdownExtension],
        'filters': {
            'markdown': markdown,
        },
        'time': int(time()),
    })

Equivalent in the root ``config.yaml``::

    extensions:
      - strange_case.extensions.misaka.MarkdownExtension
    filters:
      markdown: strange_case.extensions.markdown
    processors:
      - strange_case.extensions.image
      - strange_case.extensions.categories
    # cannot assign time to datetime.time.  DANG.

``extensions/category.py`` has an explanation of how processors work, and how it
was written. I made it up as I went along, and ended up adding a ``Processor``
class that extends ``Node``, and a concept of "populating" the tree after the
initial build.  Read more in that file.  I think it's a good system, but I'm
open to friendly suggestions.

Last but not least: configurators.  These are really the work horses of
StrangeCase.  They look at YAML front matter, ignore files, set default
processors, and so on.  If you need to do the equivalent of a context processor
in django, this is where you would do that.

Every configurator in ``config['configurators']`` is given the node config.  If
it returns nothing, the node is ignored.  Otherwise, you can modify the config,
or create a whole new one, and return it.

See ``created_at_from_name`` for a good example of modifying the config based on
the file name.

-------------
JINJA FILTERS
-------------

StrangeCase includes several Jinja filters that you can use in your templates.
Remember that in order to use a filter you must first enable it in your
configuration. For example to enable the date filter you must add::

    filters:
      date: strange_case.extensions.date.date

This will register a filter named *date* which is implemented by the function
`date` in the module ``strange_case.extensions.date``.

strange_case.extensions.date.date
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This filter formats a date. The input can be any string readble by the
`dateutil`_ ``parse()`` method, or the string ``"now"`` for the current date. If
no format is specified it is printed as '01 Jan 2000'.

::

   <p>The date is {{ 'now'|date }}.</p>
   <p>The date is 06 May 2012.</p>

strange_case.extensions.inflect.pluralize
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pluralizes a variable::

    <p>Category - {{ title|pluralize }}

::

    filters:
      pluralize: strange_case.extensions.inflect.pluralize

strange_case.extensions.uuid.uuid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This filter generates a UUID based on the provided input. The UUID is
generated by taking a SHA1 hash of the input combined with a namespace
identifier. The available namespaces are:

* ``dns`` for fully-qualified domain names as input
* ``url`` for URLs (default)
* ``oid`` for ISO OID input
* ``X500`` for X.500 DNs in either DER or text format

::

   <id>{{ 'http://myhost.com/articles'|uuid('url') }}</id>


strange_case.extensions.uuid.urn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This filter generates a UUID URN based on the provided input. This is often
useful when needing to generate unique identifies that must be URIs, for
example when generating an Atom feed.

The UUID is generated by taking a SHA1 hash of the input combined with a
namespace identifier. The available namespaces are:

* ``dns`` for fully-qualified domain names as input
* ``url`` for URLs (default)
* ``oid`` for ISO OID input
* ``X500`` for X.500 DNs in either DER or text format

::

   <id>{{ 'http://myhost.com/articles'|uuid('url') }}</id>

---------------
IMAGE PROCESSOR
---------------

The image processor uses PIL to create thumbnails.  The usual way to do this is
to specify the thumbnail size in a parent folder config, and then set `type:
image` on all the image files.  This is done in the image folder's config.yaml
file::

    thumbnails:
        thumb: '480x480'
    file_types:
        - [image, '*.jpg']
    files:
        img_0001.jpg:
            alt: a great picture
        img_0002.jpg:
        ...

It registers all images to be processed by the image processor, so you don't
have to write an entry for every file in the folder.

And of course, enable the image processor in your ``config.yaml``::

    processors:
        - strange_case.extensions.image

------------------
CATEGORY PROCESSOR
------------------

This processor scans your site pages, looking for pages that have a "category"
property in their config.  For every category, it builds a ``category_detail``
page that can list the pages, and a ``category_index`` page to list the
categories.

Enable the category processor in your ``config.yaml``::

    processors:
        - strange_case.extensions.category

And build ``categories.j2`` and ``category_detail.j2``.  The ``category_detail``
page can be named anything (it will get renamed based on the category), but the
``categories`` page will keep its name/title/etc, so give it a sensible name.

In categories.j2 you can use the ``categories`` property to iterate over the
category_detail pages::

    ---
    type: category_index
    ---
    {% extends 'layouts/base.j2' %}

    {% for category in my.categories %}
      <li><a href="{{ category.url }}">{{ category.title }}</a> (<span>{{ category.count }}</span>)</li>
    {% endfor %}

In category_detail.j2 you'll have a ``pages`` property::

    ---
    type: category_detail
    ---
    {% extends 'layouts/header.j2' %}

    {% block content %}
    <ul class="posts">
    {%- for page in my.pages %}
      <li><a href="{{ page.url }}">{{ page.title }}</a></li>
    {%- endfor %}
    </ul>
    {% endblock %}

-------------------
PAGINATED PROCESSOR
-------------------

This processor can break up a large folder of pages.  It is designed so that
converting from an index.j2 file to a paginated file is easy.  Let's say your
existing blogs/index.j2 lookes like this::

    {% extends 'layouts/base.j2' %}

    {% block content %}
    <ul>
    {% for page in site.blogs %}
        <li><a href="{{ page.url }}">{{ page.title }}</a></li>
    {% endfor %}
    </ul>
    {% endblock content %}

We'll change this to use pagination.

Enable the paginated processor in your ``config.yaml``::

    processors:
        - strange_case.extensions.paginated

And change the ``type`` to ``paginated``, and update the HTML to use pagination::

    ----
    type: paginated
    ----
    {% extends 'layouts/base.j2' %}

    {% block content %}
    <ul>
    {% for page in my.page %}
        <li><a href="{{ page.url }}">{{ page.title }}</a></li>
    {% endfor %}
    </ul>

    <div class="pagination">
    {% if my.page.prev %}<a href="{{ my.page.prev.url }}">&lsaquo; {{ my.page.prev.title }} |</a>
    {% else %}&lsaquo;
    {% endif %}
    {{ my.page }}
    {% if my.page.next %}| <a href="{{ my.page.next.url }}">{{ my.page.next.title }} &rsaquo;</a>
    {% else %}&rsaquo;
    {% endif %}
    </div>
    {% endblock content %}

-----------------------------
SCSS AND CLEVERCSS PROCESSORS
-----------------------------

These two get associated with ``.scss`` and ``.clevercss`` files and compile them to CSS files.

::

    processors:
        - strange_case.extensions.scss
        - strange_case.extensions.clevercss

-------
TESTING
-------

I am currently (as of version 4.0.2) including tests::

    > pip install pytest
    > py.test

-------
LICENSE
-------

:Author: Colin T.A. Gray
:Copyright: 2012 Colin T.A. Gray <http://colinta.com/>

Copyright (c) 2012, Colin T.A. Gray
All rights reserved.

See LICENSE_ for more details (it's a simplified BSD license).

.. _jekyll:       https://github.com/mojombo/jekyll
.. _hyde:         http://ringce.com/hyde
.. _Jinja2:       http://jinja.pocoo.org/
.. _LICENSE:      https://github.com/colinta/StrangeCase/blob/master/LICENSE
.. _PIL:          http://www.pythonware.com/products/pil/
.. _nanoc:        http://nanoc.stoneship.org/
.. _dateutil:     http://labix.org/python-dateutil
