import math
from strange_case.registry import Registry
from strange_case.nodes.jinja import JinjaNode
from strange_case.nodes import Processor
import types


def bind(object, name=None):
    def dec(function):
        my_name = name or function.__name__

        setattr(object, my_name, types.MethodType(function, object))
    return dec


class Page(object):
    """
    Pretty much acts like a list (a "page") of StrangeCase nodes,
    but adds these properties:
        `index`: 0-based index
        `page`: 1-based index
        `limit`: number of items *per page* (not necessarily the number on *this* page)
        `from`: 1-based item index of first item in page
        `to`: 1-based item index of last item in page
        `length`/`len`: number of items on this page
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
        return "Page %i of %i, item%s %i to %i" % (self.page, self.pages, (self.from_index < self.to_index and 's' or ''), self.from_index, self.to_index)


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
    paginated = Processor(config)
    page_limit = int(config.get('paginated', {}).get('limit', 10))
    page_name = config.get('paginated', {}).get('name', 'page')
    page_title = config.get('paginated', {}).get('title', 'Page')

    @bind(paginated)
    def populate(self, site):
        ret = []
        pages = paginate([node for node in self.parent if node.is_page], page_limit)

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
            more_page_config = self.config.get('pages', {}).get(1 + len(ret), None)
            if more_page_config:
                page_config.update(more_page_config)
            page_config.setdefault('title', "%s %i" % (page_title, 1 + len(ret)))
            page_config.setdefault('page', page)
            page_config.setdefault('iterable', False)
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

    return (paginated, )


Registry.register('paginated', paginated_processor)
