import xml.etree.ElementTree as ET
from .. import NAMESPACE
from .schedule_item import ScheduleItem


class TaskItem(object):
    def __init__(self, id_, task_type, priority, consecutive_failed_count=0, schedule_id=None):
        self.id = id_
        self.task_type = task_type
        self.priority = priority
        self.consecutive_failed_count = consecutive_failed_count
        self.schedule_id = schedule_id

    def __repr__(self):
        return "<Task#{id} {task_type} pri({priority}) failed({consecutive_failed_count}) schedule_id({" \
               "schedule_id})>".format(**self.__dict__)

    @classmethod
    def from_response(cls, xml):
        parsed_response = ET.fromstring(xml)
        all_tasks_xml = parsed_response.findall(
            './/t:task/t:extractRefresh', namespaces=NAMESPACE)

        all_tasks = (TaskItem._parse_element(x) for x in all_tasks_xml)

        return list(all_tasks)

    @classmethod
    def _parse_element(cls, element):
        schedule = None
        schedule_element = element.find('.//t:schedule', namespaces=NAMESPACE)
        if schedule_element is not None:
            schedule = schedule_element.get('id', None)
        task_type = element.get('type', None)
        priority = int(element.get('priority', -1))
        consecutive_failed_count = int(element.get('consecutiveFailedCount', 0))
        id_ = element.get('id', None)
        return cls(id_, task_type, priority, consecutive_failed_count, schedule)
