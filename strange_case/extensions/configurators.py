"""
Users are encouraged to add their own configurators and import them here.
"""
from .configurator_created_at_from_name import created_at_from_name
from .configurator_order_from_name import order_from_name
from .configurator_title_from_name import title_from_name
from .configurator_file_stats import file_ctime, file_mtime
from .configurator_strip_extensions import strip_extensions
