from .endpoint import Endpoint, api, item_must_be_of_type
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, PaginationItem, ScheduleItem, WorkbookItem, DatasourceItem
from ...type_helpers import item_type
import logging
import copy

logger = logging.getLogger('tableau.endpoint.schedules')


class Schedules(Endpoint):
    @property
    def baseurl(self):
        return "{0}/schedules".format(self.parent_srv.baseurl)

    @property
    def siteurl(self):
        return "{0}/sites/{1}/schedules".format(self.parent_srv.baseurl, self.parent_srv.site_id)


    @api(version="2.3")
    def get(self, req_options=None):
        logger.info("Querying all schedules")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_schedule_items = ScheduleItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_schedule_items, pagination_item


    @api(version="2.3")
    def delete(self, schedule_id):
        if not schedule_id:
            error = "Schedule ID undefined"
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, schedule_id)
        self.delete_request(url)
        logger.info("Deleted single schedule (ID: {0})".format(schedule_id))


    @api(version="2.3")
    def update(self, schedule_item):
        if not schedule_item.id:
            error = "Schedule item missing ID."
            raise MissingRequiredFieldError(error)
        if schedule_item.interval_item is None:
            error = "Interval item must be defined."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, schedule_item.id)
        update_req = RequestFactory.Schedule.update_req(schedule_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated schedule item (ID: {})".format(schedule_item.id))
        updated_schedule = copy.copy(schedule_item)
        return updated_schedule._parse_common_tags(server_response.content, self.parent_srv.namespace)


    @api(version="2.3")
    def create(self, schedule_item):
        if schedule_item.interval_item is None:
            error = "Interval item must be defined."
            raise MissingRequiredFieldError(error)

        url = self.baseurl
        create_req = RequestFactory.Schedule.create_req(schedule_item)
        server_response = self.post_request(url, create_req)
        new_schedule = ScheduleItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        logger.info("Created new schedule (ID: {})".format(new_schedule.id))
        return new_schedule


    @api(version="2.8")
    @item_must_be_of_type(workbook_or_datasource=[WorkbookItem, DatasourceItem])
    def add_to_schedule(self, schedule_id, workbook_or_datasource):
        type_ = item_type(workbook_or_datasource)

        # id will exist because item_must_be_of_type ensures this
        id_ = workbook_or_datasource.id
        req_factory = getattr(RequestFactory.Schedule, 'add_{}_req'.format(type_), None)
        if req_factory is None:
            raise RuntimeError("Unable to find request factory for {}".format(type_))

        url = "{0}/{1}/{2}s".format(self.siteurl, schedule_id, type_)

        add_req = req_factory(id_)
        server_response = self.put_request(url, add_req)
        # TOOD: Assert that server_response is 2xx, otherwise, throw an error
        logger.info("Added {0} {1} to schedule {2}".format(type_, id_, schedule_id))
        return True
