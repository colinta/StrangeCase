import re
from strange_case.nodes import JinjaNode, Processor


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


class CategoryFolderProcesser(Processor):
    def populate(self, site):
        pages = site.pages(recursive=True)
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
