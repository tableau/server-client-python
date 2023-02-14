
from tableauserverclient import *
# mmm. why aren't these available in the tsc namespace?
from tableauserverclient.models import DataAccelerationReportItem, FavoriteItem, Credentials, ServerInfoItem, Resource, \
    TableauItem, plural_type


def get_defined_models():
    # not clever: copied from tsc/models/__init__.py
    return [ColumnItem,
            ConnectionCredentials,
            ConnectionItem,
            DataAccelerationReportItem,
            DataAlertItem,
            DatabaseItem,
            DatasourceItem,
            DQWItem,
            UnpopulatedPropertyError,
            FavoriteItem,
            FlowItem,
            FlowRunItem,
            GroupItem,
            IntervalItem,
            DailyInterval,
            WeeklyInterval,
            MonthlyInterval,
            HourlyInterval,
            JobItem, BackgroundJobItem,
            MetricItem,
            PaginationItem,
            PermissionsRule, Permission,
            ProjectItem,
            RevisionItem,
            ScheduleItem,
            ServerInfoItem,
            SiteItem,
            SubscriptionItem,
            TableItem,
            Credentials, TableauAuth, PersonalAccessTokenAuth,
            Resource, TableauItem, plural_type,
            Target,
            TaskItem,
            UserItem,
            ViewItem,
            WebhookItem,
            WorkbookItem
            ]
