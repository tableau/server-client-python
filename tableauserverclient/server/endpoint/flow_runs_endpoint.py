from .endpoint import Endpoint, QuerysetEndpoint, api
from .. import FlowRunItem, PaginationItem
from .exceptions import FlowRunFailedException, FlowRunCanceledException
import time

import logging

logger = logging.getLogger("tableau.endpoint.flowruns")

# Polling for job completion uses exponential backoff for the sleep intervals between polls
ASYNC_JOB_POLL_MIN_INTERVAL=0.5
ASYNC_JOB_POLL_MAX_INTERVAL=30
ASYNC_JOB_POLL_BACKOFF_FACTOR=1.4

class FlowRuns(QuerysetEndpoint):
    def __init__(self, parent_srv):
        super(FlowRuns, self).__init__(parent_srv)

    @property
    def baseurl(self):
        return "{0}/sites/{1}/flows/runs".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Get all flows
    @api(version="3.10")
    def get(self, req_options=None):
        logger.info("Querying all flow runs on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_flow_run_items = FlowRunItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_flow_run_items, pagination_item

    # Get 1 flow by id
    @api(version="3.10")
    def get_by_id(self, flow_run_id):
        if not flow_run_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        logger.info("Querying single flow (ID: {0})".format(flow_run_id))
        url = "{0}/{1}".format(self.baseurl, flow_run_id)
        server_response = self.get_request(url)
        return FlowRunItem.from_response(server_response.content, self.parent_srv.namespace)[0]


    # Cancel 1 flow run by id
    @api(version="3.10")
    def cancel(self, flow_run_id):
        if not flow_run_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        id_ = getattr(flow_run_id, 'id', flow_run_id)
        url = "{0}/{1}".format(self.baseurl, id_)
        self.put_request(url)
        logger.info("Deleted single flow (ID: {0})".format(id_))


    @api(version="3.10")
    def wait_for_job(self, flow_run_id, *, timeout=None):
        id_ = getattr(flow_run_id, "id", flow_run_id)
        wait_start_time = time.time()
        logger.debug(f"Waiting for job {id_}")

        current_sleep_interval = ASYNC_JOB_POLL_MIN_INTERVAL
        flow_run = self.get_by_id(id_)
        while flow_run.completed_at is None:
            max_sleep_time = ASYNC_JOB_POLL_MAX_INTERVAL

            if timeout is not None:
                elapsed = (time.time() - wait_start_time)
                if elapsed >= timeout:
                    raise TimeoutError(f"Timeout after {elapsed} seconds waiting for asynchronous flow run: {id_}")
                max_sleep_time = max(ASYNC_JOB_POLL_MIN_INTERVAL, timeout - elapsed)

            time.sleep(min(current_sleep_interval, max_sleep_time))
            job = self.get_by_id(id_)
            current_sleep_interval *= ASYNC_JOB_POLL_BACKOFF_FACTOR
            logger.debug(f"\tFlowRun {id_} progress={flow_run.progress}")

        logger.info("FlowRun {} Completed: Status: {}".format(id_, flow_run.status))

        if flow_run.status == "Success":
            return flow_run
        elif flow_run.status == "Failed":
            raise FlowRunFailedException(flow_run)
        elif flow_run.finish_code in ["Canceled", "Cancelled"]:
            raise FlowRunCanceledException(flow_run)
        else:
            raise AssertionError("Unexpected status in flow_run", flow_run)