import copy
import logging
import warnings
from collections import namedtuple
from typing import TYPE_CHECKING, Callable, List, Optional, Tuple, Union

from .endpoint import Endpoint, api, parameter_added_in
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, PaginationItem, ScheduleItem, TaskItem

logger = logging.getLogger("tableau.endpoint.schedules")
AddResponse = namedtuple("AddResponse", ("result", "error", "warnings", "task_created"))
OK = AddResponse(result=True, error=None, warnings=None, task_created=None)

if TYPE_CHECKING:
    from ..request_options import RequestOptions
    from ...models import DatasourceItem, WorkbookItem, FlowItem


class Schedules(Endpoint):
    @property
    def baseurl(self) -> str:
        return "{0}/schedules".format(self.parent_srv.baseurl)

    @property
    def siteurl(self) -> str:
        return "{0}/sites/{1}/schedules".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="2.3")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[ScheduleItem], PaginationItem]:
        logger.info("Querying all schedules")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_schedule_items = ScheduleItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_schedule_items, pagination_item

    @api(version="3.8")
    def get_by_id(self, schedule_id):
        if not schedule_id:
            error = "No Schedule ID provided"
            raise ValueError(error)
        logger.info("Querying a single schedule by id ({})".format(schedule_id))
        url = "{0}/{1}".format(self.baseurl, schedule_id)
        server_response = self.get_request(url)
        return ScheduleItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="2.3")
    def delete(self, schedule_id: str) -> None:
        if not schedule_id:
            error = "Schedule ID undefined"
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, schedule_id)
        self.delete_request(url)
        logger.info("Deleted single schedule (ID: {0})".format(schedule_id))

    @api(version="2.3")
    def update(self, schedule_item: ScheduleItem) -> ScheduleItem:
        if not schedule_item.id:
            error = "Schedule item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, schedule_item.id)
        update_req = RequestFactory.Schedule.update_req(schedule_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated schedule item (ID: {})".format(schedule_item.id))
        updated_schedule = copy.copy(schedule_item)
        return updated_schedule._parse_common_tags(server_response.content, self.parent_srv.namespace)

    @api(version="2.3")
    def create(self, schedule_item: ScheduleItem) -> ScheduleItem:
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
    @parameter_added_in(flow="3.3")
    def add_to_schedule(
        self,
        schedule_id: str,
        workbook: "WorkbookItem" = None,
        datasource: "DatasourceItem" = None,
        flow: "FlowItem" = None,
        task_type: str = None,
    ) -> List[AddResponse]:

        # There doesn't seem to be a good reason to allow one item of each type?
        if workbook and datasource:
            warnings.warn("Passing in multiple items for add_to_schedule will be deprecated", PendingDeprecationWarning)
        items: List[
            Tuple[str, Union[WorkbookItem, FlowItem, DatasourceItem], str, Callable[[Optional[str], str], bytes], str]
        ] = []

        if workbook is not None:
            if not task_type:
                task_type = TaskItem.Type.ExtractRefresh
            items.append((schedule_id, workbook, "workbook", RequestFactory.Schedule.add_workbook_req, task_type))
        if datasource is not None:
            if not task_type:
                task_type = TaskItem.Type.ExtractRefresh
            items.append((schedule_id, datasource, "datasource", RequestFactory.Schedule.add_datasource_req, task_type))
        if flow is not None and not (workbook or datasource):  # Cannot pass a flow with any other type
            if not task_type:
                task_type = TaskItem.Type.RunFlow
            items.append(
                (schedule_id, flow, "flow", RequestFactory.Schedule.add_flow_req, task_type)
            )  # type:ignore[arg-type]

        results = (self._add_to(*x) for x in items)
        # list() is needed for python 3.x compatibility
        return list(filter(lambda x: not x.result, results))  # type:ignore[arg-type]

    def _add_to(
        self,
        schedule_id,
        resource: Union["DatasourceItem", "WorkbookItem", "FlowItem"],
        type_: str,
        req_factory: Callable[
            [
                str,
                str,
            ],
            bytes,
        ],
        item_task_type,
    ) -> AddResponse:
        id_ = resource.id
        url = "{0}/{1}/{2}s".format(self.siteurl, schedule_id, type_)
        add_req = req_factory(id_, task_type=item_task_type)  # type: ignore[call-arg, arg-type]
        response = self.put_request(url, add_req)

        error, warnings, task_created = ScheduleItem.parse_add_to_schedule_response(response, self.parent_srv.namespace)
        if task_created:
            logger.info("Added {} to {} to schedule {}".format(type_, id_, schedule_id))

        if error is not None or warnings is not None:
            return AddResponse(
                result=False,
                error=error,
                warnings=warnings,
                task_created=task_created,
            )
        else:
            return OK
