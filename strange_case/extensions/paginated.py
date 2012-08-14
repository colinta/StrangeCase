# -*- encoding: utf-8 -*-
"""
Creates pages that browse through a folder of items.

Let's say you've got 100s of blogs in your blogs/ folder:

    site/
    + blogs/
      | index.html
      | blog_001.html
      | blog_002.html
      | ...
      + blog_999.html

You probably don't want all of these on one page.  If
you assign `type: paginated` to the index.html page,
you will have a `Page` object available that you can
use to link up many pages of content.

In your template, you should iterate thourgh the page object and
output links to the next and previous pages:

    <ul>
    {% for page in my.page %}
        <li><a href="{{ page.url }}">{{ page.title }}</a></li>
    {% endfor %}
    </ul>

    {% if my.page.prev %}<a href="{{ my.page.prev.url }}">&lsaquo; {{ my.page.prev.title }} |</a>
    {% else %}&lsaquo;
    {% endif %}
    {{ my.page }}
    {% if my.page.next %}| <a href="{{ my.page.next.url }}">{{ my.page.next.title }} &rsaquo;</a>
    {% else %}&rsaquo;
    {% endif %}

The `Page` object has a few properties you might want
to use in your template:

    first: the first Page object
    is_first: True if this is the first page, otherwise False
    last: the last Page object
    is_last: True if this is the last page, otherwise False
    next: the next Page object
    prev: the previous Page object
    page: the 1-based index of the page object
    index: the 0-based index of the page object
    length/len: number of items on this page
    limit: number of items *per page* (not necessarily the number on *this* page)
    from/from_index: 1-based index of the first *item* in page
    to/to_index: 1-based index of the last *item* in page

You can output a str representation of a page object and it will
look something like this:

    n of N, item(s) a to b

If you need to configure the page nodes that get created,
you can add a `pages` dictionary to the first page.  For every
page that gets created, that entry will be searched using the
page number as the key.  So if you have this config:

    ----
    type: paginated
    pages:
        3: { title: 'The Third Page' }
    ---

The third page will use that title instead of the default ("Page 3")

You can use different names than "page" and "Page" using the `paginated`
option in config. You can also (and should) reverse the page ordering.  The
default is *sensible* (ascending) but if you are writing a blog, you probably
want the newer posts **FIRST**.

Here are the options it supports:

    ----
    type: paginated
    paginated:
        limit: 5  # default: 10
        name: 'pagina'  # default: page
        title: 'Página'  # default: Page
        reverse: true  # default: false
    pages:
        3: { title: 'The Third Page' }
    ---
"""

import math
from strange_case.nodes.jinja import JinjaNode
from strange_case.nodes import Processor
from strange_case.registry import Registry
from strange_case.configurators import configurate
import types


def bind(bind_to, name=None):
    def descriptor(function):
        my_name = name or function.__name__
        setattr(bind_to, my_name, types.MethodType(function, bind_to))
    return descriptor


class Page(object):
    """
    Pretty much acts like a list (a "page") of StrangeCase nodes,
    but adds these properties:
    """
    def __init__(self, index, limit, total):
        self.items = []
        self.limit = limit
        self.index = index
        self.total = total

    @property
    def page(self):
        return self.index + 1

    @property
    def pages(self):
        return int(math.ceil((self.total - 1) / self.limit)) + 1

    @property
    def length(self):
        return len(self)

    @property
    def len(self):
        return self.length

    @property
    def from_index(self):
        return self.index * self.limit + 1

    @property
    def to_index(self):
        return self.index * self.limit + len(self.items)

    def __getitem__(self, key):
        """
        In templates, 'page.from' and 'page.to' look much better than 'page.from_index'
        """
        if key == 'from':
            return self.from_index()

        if key == 'to':
            return self.to_index()
        return self.items.__getitem__(self, key)

    def __getattr__(self, key):
        return getattr(self.items, key)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return self.items.__len__()

    def __str__(self):
        ret = "Page %i of %i, " % (self.page, self.pages)
        if self.from_index < self.to_index:
            ret += 'items %i to %i' % (self.from_index, self.to_index)
        else:
            ret += 'item %i' % self.from_index
        return ret


def paginate(all_items, limit):
    """
    Takes a list of items and breaks them up into pages,
    which is a list of `Page` objects.  Each `Page` will have
    at most `limit` items.
    """
    pages = []
    current_page = None
    for page in all_items:
        if not current_page:
            current_page = Page(len(pages), limit, len(all_items))
            current_page.is_first = False
            current_page.is_last = False
            pages.append(current_page)

        current_page.append(page)
        if len(current_page) == limit:
            current_page = None
    if pages:
        pages[0].is_first = True
        pages[-1].is_last = True

    return pages


def paginated_processor(config, source_path, target_path):
    config['dont_inherit'].append('pages')
    paginated_processor = Processor(config)
    paginated_config = config.get('paginated', {})
    page_limit = int(paginated_config.get('limit', 10))
    page_name = paginated_config.get('name', 'page')
    page_title = paginated_config.get('title', 'Page')
    page_reverse = paginated_config.get('reverse', False)
    page_order = paginated_config.get('order')
    if page_order:
        import sys
        page_reverse = True if page_order.upper() == 'DESC' else False
        sys.stderr.write("Warning: `paginated.order` is deprecated.  Use `paginated.reverse = {0!r}` instead\n".format(page_reverse))

    @bind(paginated_processor)
    def populate(self, site):
        ret = []
        nodes = [node for node in self.siblings if node.is_page]
        if page_reverse:
            nodes.reverse()
        pages = paginate(nodes, page_limit)

        first_page = None
        last_page = None

        for page in pages:
            if not len(ret):  # is this the first page?
                page_config = self.config_copy(True)  # copy *all* config, even name and title.
            else:
                name = "%s%i" % (page_name, 1 + len(ret))
                target_name = name + config['html_extension']
                page_config = self.config_copy(
                    name=name,
                    target_name=target_name,
                    )
            # page configuration can be further customized by creating a
            # pages: {} dictionary.  The key names should be the page index
            page_index = 1 + len(ret)
            page_config.setdefault('title', "%s %i" % (page_title, page_index))
            page_config.setdefault('page', page)
            page_config.setdefault('iterable', False)
            configurate(source_path, page_config)
            more_page_config = self.config.get('pages', {}).get(page_index)
            if more_page_config:
                page_config.update(more_page_config)
            node = JinjaNode(page_config, source_path, target_path)

            # now that we have node objects we can assign prev and next properties onto
            # the page object.
            page.prev = last_page
            page.next = None
            if last_page:
                last_page.page.next = node
            ret.append(node)
            last_page = node

        for node in ret:
            node.page.first = first_page
            node.page.last = last_page
        return ret

    return (paginated_processor, )


Registry.register('paginated', paginated_processor)
