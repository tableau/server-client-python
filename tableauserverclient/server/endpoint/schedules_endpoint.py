from .endpoint import Endpoint
from .. import PaginationItem, ScheduleItem
import logging

logger = logging.getLogger('tableau.endpoint.schedules')


class Schedules(Endpoint):
    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.baseurl = "{0}/schedules"
        self.parent_srv = parent_srv

    def _construct_url(self):
        return self.baseurl.format(self.parent_srv.baseurl)

    def get(self, req_options=None):
        logger.info("Querying all schedules")
        url = self._construct_url()
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        all_schedule_items = ScheduleItem.from_response(server_response.content)
        return all_schedule_items, pagination_item

    def delete(self, schedule_id):
        if not schedule_id:
            error = "Schedule ID undefined"
            raise ValueError(error)
        url = "{0}/{1}".format(self._construct_url(), schedule_id)
        self.delete_request(url)
        logger.info("Deleted single schedule (ID: {0})".format(schedule_id))
