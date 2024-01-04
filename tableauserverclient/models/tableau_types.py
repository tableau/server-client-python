from typing import Union

from .datasource_item import DatasourceItem
from .flow_item import FlowItem
from .project_item import ProjectItem
from .view_item import ViewItem
from .workbook_item import WorkbookItem
from .metric_item import MetricItem


class Resource:
    Database = "database"
    Datarole = "datarole"
    Table = "table"
    Datasource = "datasource"
    Flow = "flow"
    Lens = "lens"
    Metric = "metric"
    Project = "project"
    View = "view"
    Workbook = "workbook"


# resource types that have permissions, can be renamed, etc
# todo: refactoring: should actually define TableauItem as an interface and let all these implement it
TableauItem = Union[DatasourceItem, FlowItem, MetricItem, ProjectItem, ViewItem, WorkbookItem]


def plural_type(content_type: Resource) -> str:
    if content_type == Resource.Lens:
        return "lenses"
    else:
        return "{}s".format(content_type)
