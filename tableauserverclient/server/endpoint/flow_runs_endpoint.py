import logging
from typing import List, Optional, Tuple, TYPE_CHECKING

from .endpoint import QuerysetEndpoint, api
from .exceptions import FlowRunFailedException, FlowRunCancelledException
from .. import FlowRunItem, PaginationItem
from ...exponential_backoff import ExponentialBackoffTimer

logger = logging.getLogger("tableau.endpoint.flowruns")

if TYPE_CHECKING:
    from ..server import Server
    from ..request_options import RequestOptions


class FlowRuns(QuerysetEndpoint):
    def __init__(self, parent_srv: "Server") -> None:
        super(FlowRuns, self).__init__(parent_srv)
        return None

    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/flows/runs".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Get all flows
    @api(version="3.10")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[FlowRunItem], PaginationItem]:
        logger.info("Querying all flow runs on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_flow_run_items = FlowRunItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_flow_run_items, pagination_item

    # Get 1 flow by id
    @api(version="3.10")
    def get_by_id(self, flow_run_id: str) -> FlowRunItem:
        if not flow_run_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        logger.info("Querying single flow (ID: {0})".format(flow_run_id))
        url = "{0}/{1}".format(self.baseurl, flow_run_id)
        server_response = self.get_request(url)
        return FlowRunItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Cancel 1 flow run by id
    @api(version="3.10")
    def cancel(self, flow_run_id: str) -> None:
        if not flow_run_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        id_ = getattr(flow_run_id, "id", flow_run_id)
        url = "{0}/{1}".format(self.baseurl, id_)
        self.put_request(url)
        logger.info("Deleted single flow (ID: {0})".format(id_))

    @api(version="3.10")
    def wait_for_job(self, flow_run_id: str, *, timeout: Optional[int] = None) -> FlowRunItem:
        if isinstance(flow_run_id, FlowRunItem):
            flow_run_id = flow_run_id.id
        assert isinstance(flow_run_id, str)
        logger.debug(f"Waiting for flow run {flow_run_id}")

        backoffTimer = ExponentialBackoffTimer(timeout=timeout)
        flow_run = self.get_by_id(flow_run_id)
        while flow_run.completed_at is None:
            backoffTimer.sleep()
            flow_run = self.get_by_id(flow_run_id)
            logger.debug(f"\tFlowRun {flow_run_id} progress={flow_run.progress}")

        logger.info("FlowRun {} Completed: Status: {}".format(flow_run_id, flow_run.status))

        if flow_run.status == "Success":
            return flow_run
        elif flow_run.status == "Failed":
            raise FlowRunFailedException(flow_run)
        elif flow_run.status == "Cancelled":
            raise FlowRunCancelledException(flow_run)
        else:
            raise AssertionError("Unexpected status in flow_run", flow_run)
