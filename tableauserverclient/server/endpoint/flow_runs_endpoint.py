from .endpoint import Endpoint, QuerysetEndpoint, api
from .. import FlowRunItem, PaginationItem

import logging

logger = logging.getLogger("tableau.endpoint.flowruns")


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
        all_flow_items = FlowRunItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_flow_items, pagination_item

    # Get 1 flow by id
    @api(version="3.10")
    def get_by_id(self, flowrun_id):
        if not flowrun_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        logger.info("Querying single flow (ID: {0})".format(flowrun_id))
        url = "{0}/{1}".format(self.baseurl, flowrun_id)
        server_response = self.get_request(url)
        return FlowRunItem.from_response(server_response.content, self.parent_srv.namespace)[0]


    # Cancel 1 flow run by id
    @api(version="3.10")
    def cancel(self, flowrun_id):
        if not flowrun_id:
            error = "Flow ID undefined."
            raise ValueError(error)
        id_ = getattr(flowrun_id, 'id', flowrun_id)
        url = "{0}/{1}".format(self.baseurl, id_)
        self.put_request(url)
        logger.info("Deleted single flow (ID: {0})".format(id_))
