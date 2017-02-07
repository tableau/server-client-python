from .endpoint import Endpoint
from .. import TaskItem, PaginationItem
import logging

logger = logging.getLogger('tableau.endpoint.tasks')


class Tasks(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/tasks/extract-refreshes".format(self.parent_srv.baseurl,
                                                              self.parent_srv.site_id)

    def get(self, req_options=None):
        logger.info('Querying all tasks for the site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)

        pagination_item = PaginationItem.from_response(server_response.content)
        all_extract_tasks = TaskItem.from_response(server_response.content)
        return all_extract_tasks, pagination_item

    def get_by_id(self, task_id):
        if not task_id:
            error = "No Task ID provided"
            raise ValueError(error)
        logger.info("Querying a single task by id ({})".format(task_id))
        url = "{}/{}".format(self.baseurl, task_id)
        server_response = self.get_request(url)
        return TaskItem.from_response(server_response.content)[0]
