import logging
from typing import List, Optional, Tuple, TYPE_CHECKING

from tableauserverclient.server.endpoint.endpoint import Endpoint, api
from tableauserverclient.server.endpoint.exceptions import MissingRequiredFieldError
from tableauserverclient.models import TaskItem, PaginationItem
from tableauserverclient.server import RequestFactory

from tableauserverclient.helpers.logging import logger

if TYPE_CHECKING:
    from tableauserverclient.server.request_options import RequestOptions


class FlowTasks(Endpoint):
    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/tasks/flows".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="3.22")
    def create(self, flow_item: TaskItem) -> TaskItem:
        if not flow_item:
            error = "No flow provided"
            raise ValueError(error)
        logger.info("Creating an flow task %s", flow_item)
        url = self.baseurl
        create_req = RequestFactory.FlowTask.create_flow_task_req(flow_item)
        server_response = self.post_request(url, create_req)
        return server_response.content
