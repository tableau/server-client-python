import xml.etree.ElementTree as ET
from .interval_item import IntervalItem
from .. import NAMESPACE


class ScheduleItem(object):
    class Type:
        Extract = "Extract"
        Subscription = "Subscription"

    class ExecutionOrder:
        Parallel = "Parallel"
        Serial = "Serial"

    class State:
        Active = "Active"
        Suspended = "Suspended"

    def __init__(self, name, priority, schedule_type, execution_order, interval_item):
        self._created_at = None
        self._end_schedule_at = None
        self._execution_order = None
        self._frequency = None
        self._id = None
        self._name = None
        self._next_run_at = None
        self._priority = None
        self._schedule_type = None
        self._state = None
        self._updated_at = None
        self.interval_item = interval_item

        # Invoke setter
        self.execution_order = execution_order
        self.name = name
        self.priority = priority
        self.schedule_type = schedule_type

    @property
    def created_at(self):
        return self._created_at

    @property
    def end_schedule_at(self):
        return self._end_schedule_at

    @property
    def execution_order(self):
        return self._execution_order

    @execution_order.setter
    def execution_order(self, value):
        if value and not hasattr(ScheduleItem.ExecutionOrder, value):
            error = "Invalid execution order defined: {}.".format(value)
            raise ValueError(error)
        else:
            self._execution_order = value

    @property
    def frequency(self):
        return self._frequency

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            error = "Name must be defined."
            raise ValueError(error)
        else:
            self._name = value

    @property
    def next_run_at(self):
        return self._next_run_at

    @property
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value < 1 or value > 100:
            error = "Invalid priority defined: {}.".format(value)
            raise ValueError(error)
        else:
            self._priority = value

    @property
    def schedule_type(self):
        return self._schedule_type

    @schedule_type.setter
    def schedule_type(self, value):
        if not value:
            error = "Schedule type must be defined."
            raise ValueError(error)
        elif not hasattr(ScheduleItem.Type, value):
            error = "Invalid schedule type defined: {}.".format(value)
            raise ValueError(error)
        else:
            self._schedule_type = value

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if not hasattr(ScheduleItem.State, value):
            error = "Invalid state defined."
            raise ValueError(error)
        else:
            self._state = value

    @property
    def updated_at(self):
        return self._updated_at

    def _parse_common_tags(self, schedule_xml):
        if not isinstance(schedule_xml, ET.Element):
            schedule_xml = ET.fromstring(schedule_xml).find('.//t:schedule', namespaces=NAMESPACE)
        if schedule_xml is not None:
            (_, name, _, _, updated_at, _, frequency, next_run_at, end_schedule_at, execution_order,
             priority, interval_item) = self._parse_element(schedule_xml)

            self._set_values(id=None,
                             name=name,
                             state=None,
                             created_at=None,
                             updated_at=updated_at,
                             schedule_type=None,
                             frequency=frequency,
                             next_run_at=next_run_at,
                             end_schedule_at=end_schedule_at,
                             execution_order=execution_order,
                             priority=priority,
                             interval_item=interval_item)

        return self

    def _set_values(self, id, name, state, created_at, updated_at, schedule_type, frequency,
                    next_run_at, end_schedule_at, execution_order, priority, interval_item):
        if id is not None:
            self._id = id
        if name:
            self._name = name
        if state:
            self._state = state
        if created_at:
            self._created_at = created_at
        if updated_at:
            self._updated_at = updated_at
        if schedule_type:
            self._schedule_type = schedule_type
        if frequency:
            self._frequency = frequency
        if next_run_at:
            self._next_run_at = next_run_at
        if end_schedule_at:
            self._end_schedule_at = end_schedule_at
        if execution_order:
            self._execution_order = execution_order
        if priority:
            self._priority = priority
        if interval_item:
            self._interval_item = interval_item

    @classmethod
    def from_response(cls, resp):
        all_schedule_items = []
        parsed_response = ET.fromstring(resp)
        all_schedule_xml = parsed_response.findall('.//t:schedule', namespaces=NAMESPACE)
        for schedule_xml in all_schedule_xml:
            (id, name, state, created_at, updated_at, schedule_type, frequency, next_run_at,
             end_schedule_at, execution_order, priority, interval_item) = cls._parse_element(schedule_xml)

            schedule_item = cls(name, priority, schedule_type, execution_order, interval_item)

            schedule_item._set_values(id=id,
                                      name=None,
                                      state=state,
                                      created_at=created_at,
                                      updated_at=updated_at,
                                      schedule_type=None,
                                      frequency=frequency,
                                      next_run_at=next_run_at,
                                      end_schedule_at=end_schedule_at,
                                      execution_order=None,
                                      priority=None,
                                      interval_item=None)

            all_schedule_items.append(schedule_item)
        return all_schedule_items

    @staticmethod
    def _parse_element(schedule_xml):
        id = schedule_xml.get('id', None)
        name = schedule_xml.get('name', None)
        state = schedule_xml.get('state', None)
        created_at = schedule_xml.get('createdAt', None)
        updated_at = schedule_xml.get('updatedAt', None)
        schedule_type = schedule_xml.get('type', None)
        frequency = schedule_xml.get('frequency', None)
        next_run_at = schedule_xml.get('nextRunAt', None)
        end_schedule_at = schedule_xml.get('endScheduleAt', None)
        execution_order = schedule_xml.get('executionOrder', None)

        priority = schedule_xml.get('priority', None)
        if priority:
            priority = int(priority)

        interval_item = None
        frequency_detail_elem = schedule_xml.find('.//t:frequencyDetails', namespaces=NAMESPACE)
        if frequency_detail_elem is not None:
            interval_item = IntervalItem.from_xml_element(frequency_detail_elem, frequency)

        return id, name, state, created_at, updated_at, schedule_type,\
            frequency, next_run_at, end_schedule_at, execution_order, priority, interval_item
