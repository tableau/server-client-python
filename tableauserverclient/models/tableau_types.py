from tableauserverclient.models.base_item import TableauItem


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
    VirtualConnection = "virtualConnection"
    Workbook = "workbook"


# TableauItem is now a structural Protocol (base_item.py) rather than a Union type.
# Any class with id and name satisfies it implicitly -- no inheritance required.


def plural_type(content_type: Resource | str) -> str:
    if content_type == Resource.Lens:
        return "lenses"
    else:
        return f"{content_type}s"
