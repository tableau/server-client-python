import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, Union

from defusedxml.ElementTree import fromstring

from tableauserverclient.datetime_helpers import parse_datetime
from .interval_item import (
    IntervalItem,
    HourlyInterval,
    DailyInterval,
    WeeklyInterval,
    MonthlyInterval,
)
from .property_decorators import (
    property_is_enum,
)

Interval = Union[HourlyInterval, DailyInterval, WeeklyInterval, MonthlyInterval]


class ScheduleItem(object):
    class Type:
        Extract = "Extract"
        Flow = "Flow"
        Subscription = "Subscription"
        DataAcceleration = "DataAcceleration"
        ActiveDirectorySync = "ActiveDirectorySync"
        System = "System"

    class ExecutionOrder:
        Parallel = "Parallel"
        Serial = "Serial"

    class State:
        Active = "Active"
        Suspended = "Suspended"

    def __init__(self, name: str, priority: int, schedule_type: str, execution_order: str, interval_item: Interval):
        self._created_at: Optional[datetime] = None
        self._end_schedule_at: Optional[datetime] = None
        self._id: Optional[str] = None
        self._next_run_at: Optional[datetime] = None
        self._state: Optional[str] = None
        self._updated_at: Optional[datetime] = None
        self.interval_item: Interval = interval_item
        self.execution_order: str = execution_order
        self.name: str = name
        self.priority: int = priority
        self.schedule_type: str = schedule_type

    def __str__(self):
        return '<Schedule#{_id} "{_name}" {interval_item}>'.format(**vars(self))

    def __repr__(self):
        return self.__str__() + "  { " + ", ".join(" % s: % s" % item for item in vars(self).items()) + "}"

    @property
    def created_at(self) -> Optional[datetime]:
        return self._created_at

    @property
    def end_schedule_at(self) -> Optional[datetime]:
        return self._end_schedule_at

    @property
    def execution_order(self) -> str:
        return self._execution_order

    @execution_order.setter
    @property_is_enum(ExecutionOrder)
    def execution_order(self, value: str):
        self._execution_order = value

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def next_run_at(self) -> Optional[datetime]:
        return self._next_run_at

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, value: int):
        self._priority = value

    @property
    def schedule_type(self) -> str:
        return self._schedule_type

    @schedule_type.setter
    @property_is_enum(Type)
    def schedule_type(self, value: str):
        self._schedule_type = value

    @property
    def state(self) -> Optional[str]:
        return self._state

    @state.setter
    @property_is_enum(State)
    def state(self, value: str):
        self._state = value

    @property
    def updated_at(self) -> Optional[datetime]:
        return self._updated_at

    @property
    def warnings(self):
        return self._warnings

    def _parse_common_tags(self, schedule_xml, ns):
        if not isinstance(schedule_xml, ET.Element):
            schedule_xml = fromstring(schedule_xml).find(".//t:schedule", namespaces=ns)
        if schedule_xml is not None:
            (
                _,
                name,
                _,
                _,
                updated_at,
                _,
                next_run_at,
                end_schedule_at,
                execution_order,
                priority,
                interval_item,
            ) = self._parse_element(schedule_xml, ns)

            self._set_values(
                id_=None,
                name=name,
                state=None,
                created_at=None,
                updated_at=updated_at,
                schedule_type=None,
                next_run_at=next_run_at,
                end_schedule_at=end_schedule_at,
                execution_order=execution_order,
                priority=priority,
                interval_item=interval_item,
            )

        return self

    def _set_values(
        self,
        id_,
        name,
        state,
        created_at,
        updated_at,
        schedule_type,
        next_run_at,
        end_schedule_at,
        execution_order,
        priority,
        interval_item,
        warnings=None,
    ):
        if id_ is not None:
            self._id = id_
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
        if warnings:
            self._warnings = warnings

    @classmethod
    def from_response(cls, resp, ns):
        parsed_response = fromstring(resp)
        return cls.from_element(parsed_response, ns)

    @classmethod
    def from_element(cls, parsed_response, ns):
        warnings = cls._read_warnings(parsed_response, ns)

        all_schedule_items = []
        all_schedule_xml = parsed_response.findall(".//t:schedule", namespaces=ns)
        for schedule_xml in all_schedule_xml:
            (
                id_,
                name,
                state,
                created_at,
                updated_at,
                schedule_type,
                next_run_at,
                end_schedule_at,
                execution_order,
                priority,
                interval_item,
            ) = cls._parse_element(schedule_xml, ns)

            schedule_item = cls(name, priority, schedule_type, execution_order, interval_item)

            schedule_item._set_values(
                id_=id_,
                name=None,
                state=state,
                created_at=created_at,
                updated_at=updated_at,
                schedule_type=None,
                next_run_at=next_run_at,
                end_schedule_at=end_schedule_at,
                execution_order=None,
                priority=None,
                interval_item=None,
                warnings=warnings,
            )

            all_schedule_items.append(schedule_item)
        return all_schedule_items

    @staticmethod
    def _parse_interval_item(parsed_response, frequency, ns):
        start_time = parsed_response.get("start", None)
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        end_time = parsed_response.get("end", None)
        if end_time is not None:
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()
        interval_elems = parsed_response.findall(".//t:intervals/t:interval", namespaces=ns)
        interval = []
        for interval_elem in interval_elems:
            interval.extend(interval_elem.attrib.items())

        if frequency == IntervalItem.Frequency.Daily:
            converted_intervals = []

            for i in interval:
                # We use fractional hours for the two minute-based intervals.
                # Need to convert to hours from minutes here
                if i[0] == IntervalItem.Occurrence.Minutes:
                    converted_intervals.append(float(i[1]) / 60)
                elif i[0] == IntervalItem.Occurrence.Hours:
                    converted_intervals.append(float(i[1]))
                else:
                    converted_intervals.append(i[1])

            return DailyInterval(start_time, *converted_intervals)

        if frequency == IntervalItem.Frequency.Hourly:
            converted_intervals = []

            for i in interval:
                # We use fractional hours for the two minute-based intervals.
                # Need to convert to hours from minutes here
                if i[0] == IntervalItem.Occurrence.Minutes:
                    converted_intervals.append(float(i[1]) / 60)
                elif i[0] == IntervalItem.Occurrence.Hours:
                    converted_intervals.append(i[1])
                else:
                    converted_intervals.append(i[1])

            return HourlyInterval(start_time, end_time, tuple(converted_intervals))

        if frequency == IntervalItem.Frequency.Weekly:
            interval_values = [i[1] for i in interval]
            return WeeklyInterval(start_time, *interval_values)

        if frequency == IntervalItem.Frequency.Monthly:
            interval_values = [i[1] for i in interval]

            return MonthlyInterval(start_time, tuple(interval_values))

    @staticmethod
    def _parse_element(schedule_xml, ns):
        id = schedule_xml.get("id", None)
        name = schedule_xml.get("name", None)
        state = schedule_xml.get("state", None)
        created_at = parse_datetime(schedule_xml.get("createdAt", None))
        updated_at = parse_datetime(schedule_xml.get("updatedAt", None))
        schedule_type = schedule_xml.get("type", None)
        frequency = schedule_xml.get("frequency", None)
        next_run_at = parse_datetime(schedule_xml.get("nextRunAt", None))
        end_schedule_at = parse_datetime(schedule_xml.get("endScheduleAt", None))
        execution_order = schedule_xml.get("executionOrder", None)

        priority = schedule_xml.get("priority", None)
        if priority:
            priority = int(priority)

        interval_item = None
        frequency_detail_elem = schedule_xml.find(".//t:frequencyDetails", namespaces=ns)
        if frequency_detail_elem is not None:
            interval_item = ScheduleItem._parse_interval_item(frequency_detail_elem, frequency, ns)

        return (
            id,
            name,
            state,
            created_at,
            updated_at,
            schedule_type,
            next_run_at,
            end_schedule_at,
            execution_order,
            priority,
            interval_item,
        )

    @staticmethod
    def parse_add_to_schedule_response(response, ns):
        parsed_response = fromstring(response.content)
        warnings = ScheduleItem._read_warnings(parsed_response, ns)
        all_task_xml = parsed_response.findall(".//t:task", namespaces=ns)

        error = (
            "Status {}: {}".format(response.status_code, response.reason)
            if response.status_code < 200 or response.status_code >= 300
            else None
        )
        task_created = len(all_task_xml) > 0
        return error, warnings, task_created

    @staticmethod
    def _read_warnings(parsed_response, ns):
        all_warning_xml = parsed_response.findall(".//t:warning", namespaces=ns)
        warnings = list() if len(all_warning_xml) > 0 else None
        for warning_xml in all_warning_xml:
            warnings.append(warning_xml.get("message", None))
        return warnings
