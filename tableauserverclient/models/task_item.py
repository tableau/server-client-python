from datetime import datetime
from typing import List, Optional

from defusedxml.ElementTree import fromstring

from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.schedule_item import ScheduleItem
from tableauserverclient.models.target import Target


class TaskItem(object):
    class Type:
        ExtractRefresh = "extractRefresh"
        DataAcceleration = "dataAcceleration"
        RunFlow = "runFlow"

    # This mapping is used to convert task type returned from server
    _TASK_TYPE_MAPPING = {
        "RefreshExtractTask": Type.ExtractRefresh,
        "MaterializeViewsTask": Type.DataAcceleration,
    }

    def __init__(
        self,
        id_: str,
        task_type: str,
        priority: int,
        consecutive_failed_count: int = 0,
        schedule_id: Optional[str] = None,
        schedule_item: Optional[ScheduleItem] = None,
        last_run_at: Optional[datetime] = None,
        target: Optional[Target] = None,
    ):
        self.id = id_
        self.task_type = task_type
        self.priority = priority
        self.consecutive_failed_count = consecutive_failed_count
        self.schedule_id = schedule_id
        self.schedule_item = schedule_item
        self.last_run_at = last_run_at
        self.target = target

    def __repr__(self) -> str:
        return (
            "<Task#{id} {task_type} pri({priority}) failed({consecutive_failed_count}) schedule_id({"
            "schedule_id}) target({target})>".format(**self.__dict__)
        )

    @classmethod
    def from_response(cls, xml, ns, task_type=Type.ExtractRefresh) -> List["TaskItem"]:
        parsed_response = fromstring(xml)
        all_tasks_xml = parsed_response.findall(".//t:task/t:{}".format(task_type), namespaces=ns)

        all_tasks = (TaskItem._parse_element(x, ns) for x in all_tasks_xml)

        return list(all_tasks)

    @classmethod
    def _parse_element(cls, element, ns):
        schedule_item = None
        target = None
        last_run_at = None
        workbook_element = element.find(".//t:workbook", namespaces=ns)
        datasource_element = element.find(".//t:datasource", namespaces=ns)
        last_run_at_element = element.find(".//t:lastRunAt", namespaces=ns)

        schedule_item_list = ScheduleItem.from_element(element, ns)
        schedule_item = next(iter(schedule_item_list), None)

        # according to the Tableau Server REST API documentation,
        # there should be only one of workbook or datasource
        if workbook_element is not None:
            workbook_id = workbook_element.get("id", None)
            target = Target(workbook_id, "workbook")
        if datasource_element is not None:
            datasource_id = datasource_element.get("id", None)
            target = Target(datasource_id, "datasource")
        if last_run_at_element is not None:
            last_run_at = parse_datetime(last_run_at_element.text)

        # Server response has different names for task types
        task_type = cls._translate_task_type(element.get("type", None))

        priority = int(element.get("priority", -1))
        consecutive_failed_count = int(element.get("consecutiveFailedCount", 0))
        id_ = element.get("id", None)
        return cls(
            id_,
            task_type,
            priority,
            consecutive_failed_count,
            schedule_item.id if schedule_item is not None else None,
            schedule_item,
            last_run_at,
            target,
        )

    @staticmethod
    def _translate_task_type(task_type: str) -> str:
        if task_type in TaskItem._TASK_TYPE_MAPPING:
            return TaskItem._TASK_TYPE_MAPPING[task_type]
        else:
            return task_type
