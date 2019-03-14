from .endpoint import Endpoint, api, parameter_added_in
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, ProjectItem, PaginationItem
import logging

logger = logging.getLogger('tableau.endpoint.projects')


class Projects(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/projects".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="2.0")
    def get(self, req_options=None):
        logger.info('Querying all projects on site')
        url = self.baseurl + '?fields=_all_'
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
    @parameter_added_in(publish_samples="2.5")
    def update(self, project_item, publish_samples=False):
        if not project_item.id:
            error = "Project item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, project_item.id)
        if publish_samples:
            url += '?publishSamples=true'
        update_req = RequestFactory.Project.common_req(project_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated project item (ID: {0})'.format(project_item.id))
        updated_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_project

    @api(version="2.0")
    @parameter_added_in(publish_samples="2.5")
    def create(self, project_item, publish_samples=False):
        url = self.baseurl
        if publish_samples:
            url += '?publishSamples=true'
        create_req = RequestFactory.Project.common_req(project_item)
        server_response = self.post_request(url, create_req)
        new_project = ProjectItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        logger.info('Created new project (ID: {0})'.format(new_project.id))
        return new_project
