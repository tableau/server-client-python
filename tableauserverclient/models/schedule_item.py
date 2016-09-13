import xml.etree.ElementTree as ET
from .. import NAMESPACE


class ScheduleItem(object):
    def __init__(self):
        self._created_at = None
        self._end_schedule_at = None
        self._frequency = None
        self._id = None
        self._name = None
        self._next_run_at = None
        self._priority = None
        self._state = None
        self._type = None
        self._updated_at = None

    @property
    def created_at(self):
        return self._created_at

    @property
    def end_schedule_at(self):
        return self._end_schedule_at

    @property
    def frequency(self):
        return self._frequency

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def next_run_at(self):
        return self._next_run_at

    @property
    def priority(self):
        return self._priority

    @property
    def state(self):
        return self._state

    @property
    def type(self):
        return self._type

    @property
    def updated_at(self):
        return self._updated_at

    @classmethod
    def from_response(cls, resp):
        all_schedule_items = list()
        parsed_response = ET.fromstring(resp)
        all_schedule_xml = parsed_response.findall('.//t:schedule', namespaces=NAMESPACE)
        for schedule_xml in all_schedule_xml:
            schedule_item = cls()
            schedule_item._id = schedule_xml.get('id', None)
            schedule_item._name = schedule_xml.get('name', None)
            schedule_item._state = schedule_xml.get('state', None)
            schedule_item._created_at = schedule_xml.get('createdAt', None)
            schedule_item._updated_at = schedule_xml.get('updatedAt', None)
            schedule_item._type = schedule_xml.get('type', None)
            schedule_item._frequency = schedule_xml.get('frequency', None)
            schedule_item._next_run_at = schedule_xml.get('nextRunAt', None)
            schedule_item._end_schedule_at = schedule_xml.get('endScheduleAt', None)

            priority = schedule_xml.get('priority', None)
            if priority:
                schedule_item._priority = int(priority)
            all_schedule_items.append(schedule_item)
        return all_schedule_items
