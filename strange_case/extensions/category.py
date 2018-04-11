"""
How to write category & categories pages using processors.

In the end, we will be creating:

* category index (view all categories)
* category folder
*   - category 1
*   - category 2
*   ....
*   - category n

1)  Build your category_index and category_detail pages.  The location of
    category_index will determine what pages it looks in.  It will search all
    pages and folders that are in the same folder (e.g.
    self.parent.pages(recursive=True) ).  The category_detail page should be in
    the same folder.

2)  The category_index should register its processor as 'category_index'
    and the category page registers as 'category_detail'.  The 'category_detail'
    processor returns no children during the build phase (they are not known),
    and the category_index node returns a plain-old PageNode along with an
    instance of CategoryFolderNode.

3)  The CategoryFolderNode generates a page for each category found in the site
    *using* the category_index page.

4)  If you want to customize category pages on a per-category, specify a
    'category' or 'categories' config in the category_detail page front matter.
"""
import os
import re

from strange_case.nodes import JinjaNode, Processor
from strange_case.registry import Registry
from strange_case.configurators import configurate
from strange_case.processors import build_node


class CategoryDetail(JinjaNode):
    """
    Gets created by the CategoryFolderProcesser during populate.
    CategoryDetail.source_paths is assigned during initial build by the
    category_detail_processor.  If the page specifies a 'category', that page
    will only bu used for that category.  If it specifies 'categories', it will
    be used for that list of categories.  So each category can have its own
    page!  StrangeCase is all about customization :-)

    The special key ``None`` refers to the default CategoryDetail template.
    """
    source_paths = {}
    index_node = None

    def __init__(self, config, source_path, target_path):
        super(CategoryDetail, self).__init__(config, source_path, target_path)
        self.count = 0
        self.pages = []


class CategoryFolderProcesser(Processor):
    def populate(self, site):
        if not CategoryDetail.source_paths:
            raise NotImplementedError('No CategoryDetail.source_paths were not assigned. '
                            'Create a node of type "category_detail"')

        pages = site.pages(recursive=True)
        categories = {}
        for page in pages:
            try:
                category = page.category
            except AttributeError:
                continue

            if category not in categories:
                config = self.config_copy()
                target_name = re.sub(r'[\W -]+', '_', category, re.UNICODE)
                config['name'] = target_name
                config['target_name'] = target_name + config['html_extension']
                config['title'] = category

                source_path = CategoryDetail.source_paths.get(category, CategoryDetail.source_paths.get(None))
                if not source_path:
                    raise NotImplementedError('No CategoryDetail page has been '
                        'registered for the "%s" category, and there is no '
                        'default page either' % category)
                configurate(source_path, config)
                categories[category] = CategoryDetail(config, source_path, self.target_folder)

            categories[category].count += 1
            categories[category].pages.append(page)

        categories_values = list(categories.values())
        # assign categories list to the category index page
        if CategoryDetail.index_node:
            CategoryDetail.index_node.config.setdefault('categories', categories_values)
        self.replace_with(categories_values)


def index_processor(config, source_path, target_path):
    config = configurate(source_path, config)
    categories_name = config['name']

    folder_config = config.copy()
    folder_config['target_name'] = categories_name
    folder_config['name'] = categories_name
    folder_config['type'] = config['default_folder_type']
    folder = build_node(folder_config, os.path.dirname(source_path), target_path, categories_name)[0]
    categories_folder_target_path = os.path.join(target_path, categories_name)

    config['dont_inherit'] = [key for key in config['dont_inherit'] if key != 'title']
    index_config = config.copy()
    index_config['target_name'] = config['index.html']
    index_config['name'] = 'index'
    configurate(os.path.join(source_path, config['index.html']), index_config)
    index_node = JinjaNode(index_config, source_path, categories_folder_target_path)
    folder.append(index_node)
    CategoryDetail.index_node = index_node

    # attach Processor node - this is the class that will scan the pages for
    # the `category` property:
    folder.append(CategoryFolderProcesser(config, categories_folder_target_path))
    return (folder, )


def register_category_page(category, source_path):
    if category in CategoryDetail.source_paths:
        raise TypeError('Duplicate CategoryDetail page registered for "%s"' % (category or '(default category page)'))
    CategoryDetail.source_paths[category] = source_path


def detail_processor(config, source_path, target_path):
    # just store the source path - when the detail pages get created, they
    # will use this path.
    config = configurate(source_path, config)

    if 'category' in config:
        register_category_page(config['category'], source_path)
    elif 'categories' in config:
        for category in config['categories']:
            register_category_page(category, source_path)
    else:
        register_category_page(None, source_path)
    return ()


def reset_category_detail(config):
    CategoryDetail.source_paths = {}


Registry.listen('on_start', reset_category_detail)
Registry.register('category_index', index_processor)
Registry.register('category_detail', detail_processor)
