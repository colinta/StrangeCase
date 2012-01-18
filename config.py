from strange_case_jinja import StrangeCaseEnvironment
from extensions.markdown2_extension import Markdown2Extension, markdown2
from extensions.date_extension import date
from time import time
from datetime import datetime

ENVIRONMENT = StrangeCaseEnvironment(extensions=[Markdown2Extension])
ENVIRONMENT.filters['date'] = date
ENVIRONMENT.filters['markdown2'] = markdown2


CONFIG = {
    'time': int(time()),
    'now': datetime.today()
}


from processor import Processor, PageProcessor
from node import JinjaNode


class MyPageProcessor(PageProcessor):
    def process(self, config, source, target):
        hidden_config = {}.update(config)
        hidden_config['name'] = "_%s_hidden" % config['name']
        return (JinjaNode(config, source, target), JinjaNode(hidden_config, source, ".%s.hidden" % target))


Processor.register('hidden_page', MyPageProcessor)
