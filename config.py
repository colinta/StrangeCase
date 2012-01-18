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


from processor import Processor
from node import JinjaNode


def my_page_processor(config, source_path, target_path, public_path):
    hidden_config = {}
    hidden_config.update(config)
    hidden_config['name'] = "_%s_hidden" % config['name']
    return (
        JinjaNode(config, public_path, source_path, target_path),
        JinjaNode(hidden_config, "%s.hidden" % public_path, source_path, "%s.hidden" % target_path),
        )


Processor.register('hidden_page', my_page_processor)
