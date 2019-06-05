from .endpoint import api, Endpoint
from .exceptions import MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .default_permissions_endpoint import _DefaultPermissionsEndpoint
from .. import RequestFactory, ProjectItem, PaginationItem
import logging

logger = logging.getLogger('tableau.endpoint.projects')


class Projects(Endpoint):
    def __init__(self, parent_srv):
        super(Projects, self).__init__(parent_srv)

        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._default_permissions = _DefaultPermissionsEndpoint(parent_srv, lambda: self.baseurl)

    @property
    def baseurl(self):
        return "{0}/sites/{1}/projects".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="2.0")
    def get(self, req_options=None):
        logger.info('Querying all projects on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_project_items = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_project_items, pagination_item

    @api(version="2.0")
    def delete(self, project_id):
        if not project_id:
            error = "Project ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, project_id)
        self.delete_request(url)
        logger.info('Deleted single project (ID: {0})'.format(project_id))

    @api(version="2.0")
    def update(self, project_item):
        if not project_item.id:
            error = "Project item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, project_item.id)
        update_req = RequestFactory.Project.update_req(project_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated project item (ID: {0})'.format(project_item.id))
        updated_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_project

    @api(version="2.0")
    def create(self, project_item):
        url = self.baseurl
        create_req = RequestFactory.Project.create_req(project_item)
        server_response = self.post_request(url, create_req)
        new_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        logger.info('Created new project (ID: {0})'.format(new_project.id))
        return new_project

    @api(version='2.0')
    def populate_permissions(self, item):
        self._permissions.populate(item)

    @api(version='2.0')
    def update_permission(self, item, rules):
        return self._permissions.update(item, rules)

    @api(version='2.0')
    def delete_permission(self, item, rule):
        return self._permissions.delete(item, rule)

    @api(version='2.1')
    def populate_workbook_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, 'workbooks')

    @api(version='2.1')
    def populate_datasource_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, 'datasources')

    @api(version='3.4')
    def populate_flow_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, 'flows')

    @api(version='2.1')
    def update_default_permission(self, item, permissions, content_type):
        self._default_permissions.update_default_permissions(item, permissions, content_type)

    @api(version='2.1')
    def delete_default_permission(self, item, rule, content_type):
        self._default_permissions.delete_default_permission(item, rule, content_type)
