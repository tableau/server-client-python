import xml.etree.ElementTree as ET
from datetime import datetime
from .. import NAMESPACE


class IntervalItem(object):
    class Frequency:
        Hourly = "Hourly"
        Daily = "Daily"
        Weekly = "Weekly"
        Monthly = "Monthly"

    class Occurrence:
        Hours = "hours"
        Minutes = "minutes"
        WeekDay = "weekDay"
        MonthDay = "monthDay"

    class Day:
        Sunday = "Sunday"
        Monday = "Monday"
        Tuesday = "Tuesday"
        Wednesday = "Wednesday"
        Thursday = "Thursday"
        Friday = "Friday"
        Saturday = "Saturday"
        LastDay = "LastDay"

    end_time = None
    frequency = None
    interval = None
    start_time = None

    @staticmethod
    def _validate_time(t):
        units_of_time = {"hour", "minute", "second"}

        if not any(hasattr(t, unit) for unit in units_of_time):
            error = "Invalid time object defined."
            raise ValueError(error)

    @classmethod
    def from_response(cls, resp, frequency):
        cls.from_xml_element(ET.fromstring(resp), frequency)

    @classmethod
    def from_xml_element(cls, parsed_response, frequency):
        start_time = parsed_response.get("start", None)
        start_time = datetime.strptime(start_time, "%H:%M:%S").time()
        end_time = parsed_response.get("end", None)
        if end_time is not None:
            end_time = datetime.strptime(end_time, "%H:%M:%S").time()
        interval_elems = parsed_response.findall(".//t:intervals/t:interval", namespaces=NAMESPACE)
        interval = []
        for interval_elem in interval_elems:
            interval.extend(interval_elem.attrib.items())

        # If statement of doom until I think of a better way

        if frequency == IntervalItem.Frequency.Daily:
            return DailyInterval(start_time)

        if frequency == IntervalItem.Frequency.Hourly:
            interval_occurrence, interval_value = interval.pop()
            return HourlyInterval(start_time, end_time, interval_occurrence, interval_value)

        if frequency == IntervalItem.Frequency.Weekly:
            interval_values = [i[1] for i in interval]
            return WeeklyInterval(start_time, *interval_values)

        if frequency == IntervalItem.Frequency.Monthly:
            interval_occurrence, interval_value = interval.pop()
            return MonthlyInterval(start_time, interval_value)


class HourlyInterval(IntervalItem):
    def __init__(self, start_time, end_time, interval_occurrence, interval_value):

        self.start_time = start_time
        self.end_time = end_time
        self.frequency = IntervalItem.Frequency.Hourly
        self.interval = interval_occurrence.lower(), str(interval_value)

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        self._validate_time(value)

        self._start_time = value

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        self._validate_time(value)
        self._end_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, intervals):
        interval_occurrence, interval_value = intervals

        Hours = IntervalItem.Occurrence.Hours
        Minutes = IntervalItem.Occurrence.Minutes

        VALID_HOUR_INTERVALS = {1, 2, 4, 6, 8, 12}
        VALID_MIN_INTERVALS = {15, 30}

        if interval_occurrence not in {Hours, Minutes}:
            error = "Invalid interval type defined: {}.".format(interval_occurrence)
            raise ValueError(error)
        elif interval_occurrence == Hours and int(interval_value) not in VALID_HOUR_INTERVALS:
            error = "Invalid hour value defined: {}.".format(interval_value)
            raise ValueError(error)
        elif interval_occurrence == Minutes and int(interval_value) not in VALID_MIN_INTERVALS:
            error = "Invalid minute value defined: {}".format(interval_value)
            raise ValueError(error)

        self._interval = [(interval_occurrence.lower(), str(interval_value))]


class DailyInterval(IntervalItem):
    def __init__(self, start_time):
        self.start_time = start_time
        self.frequency = IntervalItem.Frequency.Daily

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        self._validate_time(value)

        self._start_time = value


class WeeklyInterval(IntervalItem):
    def __init__(self, start_time, *interval_values):
        self.start_time = start_time
        self.frequency = IntervalItem.Frequency.Weekly
        self.interval = interval_values

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        self._validate_time(value)

        self._start_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval_values):
        if not all(hasattr(IntervalItem.Day, day) for day in interval_values):
            raise ValueError("Invalid week day defined " + str(interval_values))

        self._interval = [(IntervalItem.Occurrence.WeekDay, day) for day in interval_values]


class MonthlyInterval(IntervalItem):
    def __init__(self, start_time, interval_value):
        self._validate_time(start_time)

        if (int(interval_value) < 1 or int(interval_value) > 31) and interval_value != IntervalItem.Day.LastDay:
            error = "Invalid interval value defined for a monthly frequency: {}.".format(interval_value)
            raise ValueError(error)

        self.start_time = start_time
        self.frequency = IntervalItem.Frequency.Monthly
        self.interval = str(interval_value)

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        self._validate_time(value)

        self._start_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval_value):
        if (int(interval_value) < 1 or int(interval_value) > 31) and interval_value != IntervalItem.Day.LastDay:
            error = "Invalid interval value defined for a monthly frequency: {}.".format(interval_value)
            raise ValueError(error)

        self._interval = [(IntervalItem.Occurrence.MonthDay, str(interval_value))]
