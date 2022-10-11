from tableauserverclient.models.database_item import DatabaseItem
from tableauserverclient.models.datasource_item import DatasourceItem
from tableauserverclient.models.flow_item import FlowItem
from tableauserverclient.models.project_item import ProjectItem
from tableauserverclient.models.table_item import TableItem
from tableauserverclient.models.view_item import ViewItem
from tableauserverclient.models.workbook_item import WorkbookItem

from typing import Union


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
