from .namespace import NAMESPACE
from .models import ConnectionCredentials, ConnectionItem, DatasourceItem,\
    GroupItem, PaginationItem, ProjectItem, ScheduleItem, \
    SiteItem, TableauAuth, UserItem, ViewItem, WorkbookItem, UnpopulatedPropertyError, \
    HourlyInterval, DailyInterval, WeeklyInterval, MonthlyInterval, IntervalItem
from .server import RequestOptions, Filter, Sort, Server, ServerResponseError,\
    MissingRequiredFieldError, NotSignedInError, Pager

__version__ = '0.0.1'
__VERSION__ = __version__

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
