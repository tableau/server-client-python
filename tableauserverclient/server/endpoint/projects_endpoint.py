import logging

from tableauserverclient.server.endpoint.default_permissions_endpoint import _DefaultPermissionsEndpoint
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api, XML_CONTENT_TYPE
from tableauserverclient.server.endpoint.exceptions import MissingRequiredFieldError
from tableauserverclient.server.endpoint.permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.server import RequestFactory, RequestOptions
from tableauserverclient.models.permissions_item import PermissionsRule
from tableauserverclient.models import ProjectItem, PaginationItem, Resource

from typing import Optional, TYPE_CHECKING

from tableauserverclient.server.query import QuerySet

if TYPE_CHECKING:
    from tableauserverclient.server.server import Server
    from tableauserverclient.server.request_options import RequestOptions

from tableauserverclient.helpers.logging import logger


class Projects(QuerysetEndpoint[ProjectItem]):
    def __init__(self, parent_srv: "Server") -> None:
        super().__init__(parent_srv)

        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._default_permissions = _DefaultPermissionsEndpoint(parent_srv, lambda: self.baseurl)

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/projects"

    @api(version="2.0")
    def get(self, req_options: Optional["RequestOptions"] = None) -> tuple[list[ProjectItem], PaginationItem]:
        logger.info("Querying all projects on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_project_items = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_project_items, pagination_item

    @api(version="2.0")
    def delete(self, project_id: str) -> None:
        if not project_id:
            error = "Project ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{project_id}"
        self.delete_request(url)
        logger.info(f"Deleted single project (ID: {project_id})")

    @api(version="2.0")
    def update(self, project_item: ProjectItem, samples: bool = False) -> ProjectItem:
        if not project_item.id:
            error = "Project item missing ID."
            raise MissingRequiredFieldError(error)

        params = {"params": {RequestOptions.Field.PublishSamples: samples}}
        url = f"{self.baseurl}/{project_item.id}"
        update_req = RequestFactory.Project.update_req(project_item)
        server_response = self.put_request(url, update_req, XML_CONTENT_TYPE, params)
        logger.info(f"Updated project item (ID: {project_item.id})")
        updated_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_project

    @api(version="2.0")
    def create(self, project_item: ProjectItem, samples: bool = False) -> ProjectItem:
        params = {"params": {RequestOptions.Field.PublishSamples: samples}}
        url = self.baseurl
        if project_item._samples:
            url = f"{self.baseurl}?publishSamples={project_item._samples}"
        create_req = RequestFactory.Project.create_req(project_item)
        server_response = self.post_request(url, create_req, XML_CONTENT_TYPE, params)
        new_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        logger.info(f"Created new project (ID: {new_project.id})")
        return new_project

    @api(version="2.0")
    def populate_permissions(self, item: ProjectItem) -> None:
        self._permissions.populate(item)

    @api(version="2.0")
    def update_permissions(self, item: ProjectItem, rules: list[PermissionsRule]) -> list[PermissionsRule]:
        return self._permissions.update(item, rules)

    @api(version="2.0")
    def delete_permission(self, item: ProjectItem, rules: list[PermissionsRule]) -> None:
        self._permissions.delete(item, rules)

    @api(version="2.1")
    def populate_workbook_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Workbook)

    @api(version="2.1")
    def populate_datasource_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Datasource)

    @api(version="3.2")
    def populate_metric_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Metric)

    @api(version="3.4")
    def populate_datarole_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Datarole)

    @api(version="3.4")
    def populate_flow_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Flow)

    @api(version="3.4")
    def populate_lens_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Lens)

    @api(version="3.23")
    def populate_virtualconnection_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.VirtualConnection)

    @api(version="3.23")
    def populate_database_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Database)

    @api(version="3.23")
    def populate_table_default_permissions(self, item: ProjectItem) -> None:
        self._default_permissions.populate_default_permissions(item, Resource.Table)

    @api(version="2.1")
    def update_workbook_default_permissions(
        self, item: ProjectItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Workbook)

    @api(version="2.1")
    def update_datasource_default_permissions(
        self, item: ProjectItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Datasource)

    @api(version="3.2")
    def update_metric_default_permissions(
        self, item: ProjectItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Metric)

    @api(version="3.4")
    def update_datarole_default_permissions(
        self, item: ProjectItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Datarole)

    @api(version="3.4")
    def update_flow_default_permissions(self, item: ProjectItem, rules: list[PermissionsRule]) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Flow)

    @api(version="3.4")
    def update_lens_default_permissions(self, item: ProjectItem, rules: list[PermissionsRule]) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Lens)

    @api(version="3.23")
    def update_virtualconnection_default_permissions(
        self, item: ProjectItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.VirtualConnection)

    @api(version="3.23")
    def update_database_default_permissions(
        self, item: ProjectItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Database)

    @api(version="3.23")
    def update_table_default_permissions(
        self, item: ProjectItem, rules: list[PermissionsRule]
    ) -> list[PermissionsRule]:
        return self._default_permissions.update_default_permissions(item, rules, Resource.Table)

    @api(version="2.1")
    def delete_workbook_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Workbook)

    @api(version="2.1")
    def delete_datasource_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Datasource)

    @api(version="3.2")
    def delete_metric_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Metric)

    @api(version="3.4")
    def delete_datarole_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Datarole)

    @api(version="3.4")
    def delete_flow_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Flow)

    @api(version="3.4")
    def delete_lens_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Lens)

    @api(version="3.23")
    def delete_virtualconnection_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.VirtualConnection)

    @api(version="3.23")
    def delete_database_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Database)

    @api(version="3.23")
    def delete_table_default_permissions(self, item: ProjectItem, rule: PermissionsRule) -> None:
        self._default_permissions.delete_default_permission(item, rule, Resource.Table)

    def filter(self, *invalid, page_size: Optional[int] = None, **kwargs) -> QuerySet[ProjectItem]:
        """
        Queries the Tableau Server for items using the specified filters. Page
        size can be specified to limit the number of items returned in a single
        request. If not specified, the default page size is 100. Page size can
        be an integer between 1 and 1000.

        No positional arguments are allowed. All filters must be specified as
        keyword arguments. If you use the equality operator, you can specify it
        through <field_name>=<value>. If you want to use a different operator,
        you can specify it through <field_name>__<operator>=<value>. Field
        names can either be in snake_case or camelCase.

        This endpoint supports the following fields and operators:


        created_at=...
        created_at__gt=...
        created_at__gte=...
        created_at__lt=...
        created_at__lte=...
        name=...
        name__in=...
        owner_domain=...
        owner_domain__in=...
        owner_email=...
        owner_email__in=...
        owner_name=...
        owner_name__in=...
        parent_project_id=...
        parent_project_id__in=...
        top_level_project=...
        updated_at=...
        updated_at__gt=...
        updated_at__gte=...
        updated_at__lt=...
        updated_at__lte=...
        """

        return super().filter(*invalid, page_size=page_size, **kwargs)
