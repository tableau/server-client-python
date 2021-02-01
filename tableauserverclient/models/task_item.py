import xml.etree.ElementTree as ET
from .target import Target
from .schedule_item import ScheduleItem
from ..datetime_helpers import parse_datetime
import datetime

from typing import List, Mapping, TypeVar

T = TypeVar('T', bound='TaskItem')


class TaskItem(object):
    class Type:
        ExtractRefresh = "extractRefresh"
        DataAcceleration = "dataAcceleration"

    def __init__(self, id_: str, task_type: 'TaskItem.Type', priority: int, consecutive_failed_count: int = 0,
                 schedule_id: str = None, schedule_item: ScheduleItem = None,
                 last_run_at: datetime.datetime = None, target: Target = None) -> T:
        self.id = id_
        self.task_type = task_type
        self.priority = priority
        self.consecutive_failed_count = consecutive_failed_count
        self.schedule_id = schedule_id
        self.schedule_item = schedule_item
        self.last_run_at = last_run_at
        self.target = target

    def __repr__(self) -> str:
        return "<Task#{id} {task_type} pri({priority}) failed({consecutive_failed_count}) schedule_id({" \
               "schedule_id}) target({target})>".format(**self.__dict__)

    @classmethod
    def from_response(cls, xml: str, ns: Mapping, task_type: 'TaskItem.Type' = Type.ExtractRefresh) -> List[T]:
        parsed_response = ET.fromstring(xml)
        all_tasks_xml = parsed_response.findall(
            './/t:task/t:{}'.format(task_type), namespaces=ns)

        all_tasks = (TaskItem._parse_element(x, ns) for x in all_tasks_xml)

        return list(all_tasks)

    @classmethod
    def _parse_element(cls, element: ET.ElementTree, ns: Mapping) -> tuple:
        schedule_item = None
        target = None
        last_run_at = None
        workbook_element = element.find('.//t:workbook', namespaces=ns)
        datasource_element = element.find('.//t:datasource', namespaces=ns)
        last_run_at_element = element.find('.//t:lastRunAt', namespaces=ns)

        schedule_item_list = ScheduleItem.from_element(element, ns)
        if len(schedule_item_list) >= 1:
            schedule_item = schedule_item_list[0]

        # according to the Tableau Server REST API documentation,
        # there should be only one of workbook or datasource
        if workbook_element is not None:
            workbook_id = workbook_element.get('id', None)
            target = Target(workbook_id, "workbook")
        if datasource_element is not None:
            datasource_id = datasource_element.get('id', None)
            target = Target(datasource_id, "datasource")
        if last_run_at_element is not None:
            last_run_at = parse_datetime(last_run_at_element.text)

        task_type = element.get('type', None)
        priority = int(element.get('priority', -1))
        consecutive_failed_count = int(element.get('consecutiveFailedCount', 0))
        id_ = element.get('id', None)
        return cls(id_, task_type, priority, consecutive_failed_count, schedule_item.id,
                   schedule_item, last_run_at, target)
