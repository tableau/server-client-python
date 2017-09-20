import xml.etree.ElementTree as ET
from .target import Target


class TaskItem(object):
    def __init__(self, id_, task_type, priority, consecutive_failed_count=0, schedule_id=None, target=None):
        self.id = id_
        self.task_type = task_type
        self.priority = priority
        self.consecutive_failed_count = consecutive_failed_count
        self.schedule_id = schedule_id
        self.target = target

    def __repr__(self):
        return "<Task#{id} {task_type} pri({priority}) failed({consecutive_failed_count}) schedule_id({" \
               "schedule_id}) target({target})>".format(**self.__dict__)

    @classmethod
    def from_response(cls, xml, ns):
        parsed_response = ET.fromstring(xml)
        all_tasks_xml = parsed_response.findall(
            './/t:task/t:extractRefresh', namespaces=ns)

        all_tasks = (TaskItem._parse_element(x, ns) for x in all_tasks_xml)

        return list(all_tasks)

    @classmethod
    def _parse_element(cls, element, ns):
        schedule = None
        target = None
        schedule_element = element.find('.//t:schedule', namespaces=ns)
        workbook_element = element.find('.//t:workbook', namespaces=ns)
        datasource_element = element.find('.//t:datasource', namespaces=ns)
        if schedule_element is not None:
            schedule = schedule_element.get('id', None)

        # according to the Tableau Server REST API documentation,
        # there should be only one of workbook or datasource
        if workbook_element is not None:
            workbook_id = workbook_element.get('id', None)
            target = Target(workbook_id, "workbook")
        if datasource_element is not None:
            datasource_id = datasource_element.get('id', None)
            target = Target(datasource_id, "datasource")

        task_type = element.get('type', None)
        priority = int(element.get('priority', -1))
        consecutive_failed_count = int(element.get('consecutiveFailedCount', 0))
        id_ = element.get('id', None)
        return cls(id_, task_type, priority, consecutive_failed_count, schedule, target)
