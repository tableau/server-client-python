from tableauserverclient import *

# TODO why aren't these available in the tsc namespace? Probably a bug.
from tableauserverclient.models import (
    DataAccelerationReportItem,
    Credentials,
    ServerInfoItem,
    Resource,
    TableauItem,
)


def get_defined_models():
    # nothing clever here: list was manually copied from tsc/models/__init__.py
    return [
        ConnectionItem,
        DataAlertItem,
        DatasourceItem,
        FlowItem,
        GroupItem,
        JobItem,
        MetricItem,
        PermissionsRule,
        ProjectItem,
        RevisionItem,
        ScheduleItem,
        SubscriptionItem,
        Credentials,
        JWTAuth,
        TableauAuth,
        PersonalAccessTokenAuth,
        ServerInfoItem,
        SiteItem,
        TaskItem,
        UserItem,
        ViewItem,
        WebhookItem,
        WorkbookItem,
    ]


# manually identified. As these are implemented, they should move to the other list.
def get_unimplemented_models():
    return [
        BackgroundJobItem,
        DataAccelerationReportItem,
        FavoriteItem,
        IntervalItem,
        DailyInterval,
        WeeklyInterval,
        MonthlyInterval,
        HourlyInterval,
        PaginationItem,
        Permission,
        Resource,
        TableItem,
        TableauItem,
        Target
    ]
