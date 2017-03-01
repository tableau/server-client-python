from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, ProjectItem, PaginationItem, PermissionItem
import logging
import copy

logger = logging.getLogger('tableau.endpoint.projects')


class Projects(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/projects".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    def get(self, req_options=None):
        logger.info('Querying all projects on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        all_project_items = ProjectItem.from_response(server_response.content)
        return all_project_items, pagination_item

    def get_permissions(self, project_id, req_options=None):
        logger.info('Querying project permissions on site')
        url = "{0}/{1}/permissions".format(self.baseurl, project_id)
        server_response = self.get_request(url, req_options)
        all_project_items = PermissionItem.from_response(server_response.content)
        return all_project_items

    def delete(self, project_id):
        if not project_id:
            error = "Project ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, project_id)
        self.delete_request(url)
        logger.info('Deleted single project (ID: {0})'.format(project_id))

    def update(self, project_item):
        if not project_item.id:
            error = "Project item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, project_item.id)
        update_req = RequestFactory.Project.update_req(project_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated project item (ID: {0})'.format(project_item.id))
        updated_project = copy.copy(project_item)
        return updated_project._parse_common_tags(server_response.content)

    def create(self, project_item):
        url = self.baseurl
        create_req = RequestFactory.Project.create_req(project_item)
        server_response = self.post_request(url, create_req)
        new_project = ProjectItem.from_response(server_response.content)[0]
        logger.info('Created new project (ID: {0})'.format(new_project.id))
        return new_project

    def add_permissions(self, project_item, permission_item):
        if not project_item.id:
            error = "Project item missing ID."
            raise MissingRequiredFieldError(error)
        if not permission_item:
            error = "Permission item missing."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/permissions".format(self.baseurl, project_item.id)
        add_req = RequestFactory.Permission.add_req(permission_item)
        server_response = self.put_request(url, add_req)
        new_permissions = PermissionItem.from_response(server_response.content)[0]
        logger.info('Added new permissions for project (ID: {0})'.format(
            new_permissions.grantee_id))
        return new_permissions
