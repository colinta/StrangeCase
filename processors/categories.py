"""
How to write category & categories pages using processors.

In the end, we will be creating:

* category index (view all categories)
* category folder
*   - category 1
*   - category 2
*   ....
*   - category n

1)  Build your category_index and category_detail pages.  The location of category_index
    will determine what pages it looks in.  It will search all pages and folders that
    are in the same folder (e.g. self.parent.all(pages=True) ).  The category_detail
    page should be in the same folder.

2)  The category_index should register its processor as 'category_index'
    and the category page registers as 'category_detail'.  The 'category_detail'
    processor returns no children during the build phase (they are not known), and the
    category_index node returns a plain-old PageNode along with an instance of
    CategoryFolderNode.

3)  The CategoryFolderNode generates a page for each category found in
    the site *using* the category_index page.
"""

import os
import re
from registry import Registry
from nodes import JinjaNode, FolderNode, Processor
from copy import deepcopy


class CategoryDetail(JinjaNode):
    """
    Gets created by the CategoryFolderProcesser during populate.
    CategoryDetail.source_path is assigned during initial build
    by the category_detail_processer.
    """
    source_path = None

    def __init__(self, config, target_path, category):
        super(CategoryDetail, self).__init__(config, CategoryDetail.source_path, target_path)
        self.title = category
        self.count = 0
        self.pages = []


def category_index_processor(config, source_path, target_path):
    categories_name = 'categories'

    folder_config = deepcopy(config)
    folder_config['target_name'] = categories_name
    folder_config['name'] = categories_name
    folder = FolderNode(folder_config, None, target_path)

    index_config = deepcopy(config)
    index_config['target_name'] = config['index']
    index_config['name'] = 'index'
    categories_target_path = os.path.join(target_path, categories_name)
    index = JinjaNode(index_config, source_path, categories_target_path)

    folder.append(index)
    folder.append(CategoryFolderProcesser(config, categories_target_path))
    return (folder, )


def category_detail_processer(config, source_path, target_path):
    CategoryDetail.source_path = source_path
    return ()


class CategoryFolderProcesser(Processor):
    def populate(self, site):
        pages = site.all(pages=True, recursive=True)
        categories = {}
        for page in pages:
            if not page.category:
                continue

            if page.category not in categories:
                config = self.config_copy()
                target_name = re.sub(r'[\W -]+', '_', page.category, re.UNICODE)
                config['name'] = target_name
                config['target_name'] = target_name + config['html_extension']
                categories[page.category] = CategoryDetail(config, self.target_folder, page.category)

            categories[page.category].count += 1
            categories[page.category].pages.append(page)
        self.replace_with(categories.values())


Registry.register('category_index', category_index_processor)
Registry.register('category_detail', category_detail_processer)
