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
        BackgroundJobItem,
        ConnectionItem,
        DataAccelerationReportItem,
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
        PaginationItem,
        Permission.Mode,
        Permission.Capability,
        DailyInterval,
        WeeklyInterval,
        MonthlyInterval,
        HourlyInterval,
        TableItem,
        Target,
    ]


def get_unimplemented_models():
    return [
        FavoriteItem,  # no repr because there is no state
        Resource,  # list of type names
        TableauItem,  # should be an interface
    ]
