from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, ProjectItem, PaginationItem
import logging
import copy

logger = logging.getLogger('tableau.endpoint.projects')


class Projects(Endpoint):
    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.baseurl = "{0}/sites/{1}/projects"
        self.parent_srv = parent_srv

    def _construct_url(self):
        return self.baseurl.format(self.parent_srv.baseurl, self.parent_srv.site_id)

    def get(self, req_options=None):
        logger.info('Querying all projects on site')
        url = self._construct_url()
        server_response = self.get_request(url, req_options)
        all_project_items = ProjectItem.from_response(server_response.text)
        return all_project_items

    def delete(self, project_id):
        if not project_id:
            error = "Project ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self._construct_url(), project_id)
        self.delete_request(url)
        logger.info('Deleted single project (ID: {0})'.format(project_id))

    def update(self, project_item):
        if not project_item.id:
            error = "Project item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self._construct_url(), project_item.id)
        update_req = RequestFactory.Project.update_req(project_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated project item (ID: {0})'.format(project_item.id))
        updated_project = copy.copy(project_item)
        return updated_project._parse_common_tags(server_response.text)

    def create(self, project_item):
        url = self._construct_url()
        create_req = RequestFactory.Project.create_req(project_item)
        server_response = self.post_request(url, create_req)
        new_project = ProjectItem.from_response(server_response.text)[0]
        logger.info('Created new project (ID: {0})'.format(new_project.id))
        return new_project


