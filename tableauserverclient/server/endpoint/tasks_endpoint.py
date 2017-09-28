from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError
from .. import TaskItem, PaginationItem, RequestFactory
import logging

logger = logging.getLogger('tableau.endpoint.tasks')


class Tasks(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/tasks/extractRefreshes".format(self.parent_srv.baseurl,
                                                             self.parent_srv.site_id)

    @api(version='2.6')
    def get(self, req_options=None):
        logger.info('Querying all tasks for the site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)

        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_extract_tasks = TaskItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_extract_tasks, pagination_item

    @api(version='2.6')
    def get_by_id(self, task_id):
        if not task_id:
            error = "No Task ID provided"
            raise ValueError(error)
        logger.info("Querying a single task by id ({})".format(task_id))
        url = "{}/{}".format(self.baseurl, task_id)
        server_response = self.get_request(url)
        return TaskItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version='2.6')
    def run(self, task_item):
        if not task_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}/runNow".format(self.baseurl, task_item.id)
        run_req = RequestFactory.Task.run_req(task_item)
        server_response = self.post_request(url, run_req)
        return server_response.content
