from typing import Union

from .datasource_item import DatasourceItem
from .flow_item import FlowItem
from .project_item import ProjectItem
from .view_item import ViewItem
from .workbook_item import WorkbookItem


class Resource:
    Database = "database"
    Datarole = "datarole"
    Datasource = "datasource"
    Flow = "flow"
    Lens = "lens"
    Metric = "metric"
    Project = "project"
    Table = "table"
    View = "view"
    Workbook = "workbook"


# resource types that have permissions, can be renamed, etc
TableauItem = Union[DatasourceItem, FlowItem, ProjectItem, ViewItem, WorkbookItem]


def plural_type(content_type: Resource) -> str:
    if content_type == Resource.Lens:
        return "lenses"
    else:
        return "{}s".format(content_type)
