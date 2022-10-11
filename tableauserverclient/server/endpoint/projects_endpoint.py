import logging

from .default_permissions_endpoint import _DefaultPermissionsEndpoint
from .endpoint import QuerysetEndpoint, api, XML_CONTENT_TYPE
from .exceptions import MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .. import RequestFactory, RequestOptions, ProjectItem, PaginationItem, Resource

from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..server import Server
    from ..request_options import RequestOptions

logger = logging.getLogger("tableau.endpoint.projects")


class Projects(QuerysetEndpoint):
    def __init__(self, parent_srv: "Server") -> None:
        super(Projects, self).__init__(parent_srv)

        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._default_permissions = _DefaultPermissionsEndpoint(parent_srv, lambda: self.baseurl)

    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/projects".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="2.0")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[ProjectItem], PaginationItem]:
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
        url = "{0}/{1}".format(self.baseurl, project_id)
        self.delete_request(url)
        logger.info("Deleted single project (ID: {0})".format(project_id))

    @api(version="2.0")
    def update(self, project_item: ProjectItem, samples: bool = False) -> ProjectItem:
        if not project_item.id:
            error = "Project item missing ID."
            raise MissingRequiredFieldError(error)

        params = {"params": {RequestOptions.Field.PublishSamples: samples}}
        url = "{0}/{1}".format(self.baseurl, project_item.id)
        update_req = RequestFactory.Project.update_req(project_item)
        server_response = self.put_request(url, update_req, XML_CONTENT_TYPE, params)
        logger.info("Updated project item (ID: {0})".format(project_item.id))
        updated_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_project

    @api(version="2.0")
    def create(self, project_item: ProjectItem, samples: bool = False) -> ProjectItem:
        params = {"params": {RequestOptions.Field.PublishSamples: samples}}
        url = self.baseurl
        create_req = RequestFactory.Project.create_req(project_item)
        server_response = self.post_request(url, create_req, XML_CONTENT_TYPE, params)
        new_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        logger.info("Created new project (ID: {0})".format(new_project.id))
        return new_project

    @api(version="2.0")
    def populate_permissions(self, item: ProjectItem) -> None:
        self._permissions.populate(item)

    @api(version="2.0")
    def update_permission(self, item, rules):
        import warnings

        warnings.warn(
            "Server.projects.update_permission is deprecated, "
            "please use Server.projects.update_permissions instead.",
            DeprecationWarning,
        )
        return self._permissions.update(item, rules)

    @api(version="2.0")
    def update_permissions(self, item, rules):
        return self._permissions.update(item, rules)

    @api(version="2.0")
    def delete_permission(self, item, rules):
        self._permissions.delete(item, rules)

    @api(version="2.1")
    def populate_workbook_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, Resource.Workbook)

    @api(version="2.1")
    def populate_datasource_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, Resource.Datasource)

    @api(version="3.2")
    def populate_metric_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, Resource.Metric)

    @api(version="3.4")
    def populate_datarole_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, Resource.Datarole)

    @api(version="3.4")
    def populate_flow_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, Resource.Flow)

    @api(version="3.4")
    def populate_lens_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, Resource.Lens)

    @api(version="2.1")
    def update_workbook_default_permissions(self, item, rules):
        return self._default_permissions.update_default_permissions(item, rules, Resource.Workbook)

    @api(version="2.1")
    def update_datasource_default_permissions(self, item, rules):
        return self._default_permissions.update_default_permissions(item, rules, Resource.Datasource)

    @api(version="3.2")
    def update_metric_default_permissions(self, item, rules):
        return self._default_permissions.update_default_permissions(item, rules, Resource.Metric)

    @api(version="3.4")
    def update_datarole_default_permissions(self, item, rules):
        return self._default_permissions.update_default_permissions(item, rules, Resource.Datarole)

    @api(version="3.4")
    def update_flow_default_permissions(self, item, rules):
        return self._default_permissions.update_default_permissions(item, rules, Resource.Flow)

    @api(version="3.4")
    def update_lens_default_permissions(self, item, rules):
        return self._default_permissions.update_default_permissions(item, rules, Resource.Lens)

    @api(version="2.1")
    def delete_workbook_default_permissions(self, item, rule):
        self._default_permissions.delete_default_permission(item, rule, Resource.Workbook)

    @api(version="2.1")
    def delete_datasource_default_permissions(self, item, rule):
        self._default_permissions.delete_default_permission(item, rule, Resource.Datasource)

    @api(version="3.2")
    def delete_metric_default_permissions(self, item, rule):
        self._default_permissions.delete_default_permission(item, rule, Resource.Metric)

    @api(version="3.4")
    def delete_datarole_default_permissions(self, item, rule):
        self._default_permissions.delete_default_permission(item, rule, Resource.Datarole)

    @api(version="3.4")
    def delete_flow_default_permissions(self, item, rule):
        self._default_permissions.delete_default_permission(item, rule, Resource.Flow)

    @api(version="3.4")
    def delete_lens_default_permissions(self, item, rule):
        self._default_permissions.delete_default_permission(item, rule, Resource.Lens)
