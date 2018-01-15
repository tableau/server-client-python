from .namespace import NEW_NAMESPACE as DEFAULT_NAMESPACE
from .models import ConnectionCredentials, ConnectionItem, DatasourceItem,\
    GroupItem, JobItem, PaginationItem, ProjectItem, ScheduleItem, \
    SiteItem, TableauAuth, UserItem, ViewItem, WorkbookItem, UnpopulatedPropertyError, \
    HourlyInterval, DailyInterval, WeeklyInterval, MonthlyInterval, IntervalItem, TaskItem, \
    SubscriptionItem
from .server import RequestOptions, ImageRequestOptions, PDFRequestOptions, Filter, Sort, \
    Server, ServerResponseError, MissingRequiredFieldError, NotSignedInError, Pager
from ._version import get_versions
__version__ = get_versions()['version']
__VERSION__ = __version__
del get_versions
