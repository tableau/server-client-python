import logging
from typing import List, Optional, Tuple, TYPE_CHECKING

from tableauserverclient.server.endpoint.endpoint import Endpoint, api
from tableauserverclient.server.endpoint.exceptions import MissingRequiredFieldError
from tableauserverclient.models import TaskItem, PaginationItem
from tableauserverclient.server import RequestFactory

from tableauserverclient.helpers.logging import logger

if TYPE_CHECKING:
    from tableauserverclient.server.request_options import RequestOptions


class Tasks(Endpoint):
    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/tasks".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    def __normalize_task_type(self, task_type: str) -> str:
        """
        The word for extract refresh used in API URL is "extractRefreshes".
        It is different than the tag "extractRefresh" used in the request body.
        """
        if task_type == TaskItem.Type.ExtractRefresh:
            return "{}es".format(task_type)
        else:
            return task_type

    @api(version="2.6")
    def get(
        self, req_options: Optional["RequestOptions"] = None, task_type: str = TaskItem.Type.ExtractRefresh
    ) -> Tuple[List[TaskItem], PaginationItem]:
        if task_type == TaskItem.Type.DataAcceleration:
            self.parent_srv.assert_at_least_version("3.8", "Data Acceleration Tasks")

        logger.info("Querying all %s tasks for the site", task_type)

        url = "{0}/{1}".format(self.baseurl, self.__normalize_task_type(task_type))
        server_response = self.get_request(url, req_options)

        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_tasks = TaskItem.from_response(server_response.content, self.parent_srv.namespace, task_type)
        return all_tasks, pagination_item

    @api(version="2.6")
    def get_by_id(self, task_id: str) -> TaskItem:
        if not task_id:
            error = "No Task ID provided"
            raise ValueError(error)
        logger.info("Querying a single task by id %s", task_id)
        url = "{}/{}/{}".format(
            self.baseurl,
            self.__normalize_task_type(TaskItem.Type.ExtractRefresh),
            task_id,
        )
        server_response = self.get_request(url)
        return TaskItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.19")
    def create(self, extract_item: TaskItem) -> TaskItem:
        if not extract_item:
            error = "No extract refresh provided"
            raise ValueError(error)
        logger.info("Creating an extract refresh %s", extract_item)
        url = "{0}/{1}".format(self.baseurl, self.__normalize_task_type(TaskItem.Type.ExtractRefresh))
        create_req = RequestFactory.Task.create_extract_req(extract_item)
        server_response = self.post_request(url, create_req)
        return server_response.content

    @api(version="2.6")
    def run(self, task_item: TaskItem) -> bytes:
        if not task_item.id:
            error = "Task item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}/{2}/runNow".format(
            self.baseurl,
            self.__normalize_task_type(TaskItem.Type.ExtractRefresh),
            task_item.id,
        )
        run_req = RequestFactory.Task.run_req(task_item)
        server_response = self.post_request(url, run_req)
        return server_response.content  # Todo add typing

    # Delete 1 task by id
    @api(version="3.6")
    def delete(self, task_id: str, task_type: str = TaskItem.Type.ExtractRefresh) -> None:
        if task_type == TaskItem.Type.DataAcceleration:
            self.parent_srv.assert_at_least_version("3.8", "Data Acceleration Tasks")

        if not task_id:
            error = "No Task ID provided"
            raise ValueError(error)
        url = "{0}/{1}/{2}".format(self.baseurl, self.__normalize_task_type(task_type), task_id)
        self.delete_request(url)
        logger.info("Deleted single task (ID: %s)", task_id)
