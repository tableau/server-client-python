import xml.etree.ElementTree as ET
from datetime import datetime, time
from .. import NAMESPACE


class IntervalItem(object):
    class Frequency:
        Hourly = "Hourly"
        Daily = "Daily"
        Weekly = "Weekly"
        Monthly = "Monthly"

    class Occurrence:
        Hours = "Hours"
        Minutes = "Minutes"
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

    def __init__(self, frequency, interval, start_time, end_time=None):
        self.end_time = end_time
        self.frequency = frequency
        self.interval = interval
        self.start_time = start_time

    @staticmethod
    def _validate_time(t):
        if not hasattr(t, "hour") or not hasattr(t, "minute") or not hasattr(t, "second"):
            error = "Invalid time object defined."
            raise ValueError(error)

    @classmethod
    def create_hourly(cls, start_time, end_time, interval_occurrence, interval_value):
        if interval_occurrence != IntervalItem.Occurrence.Hours and \
                        interval_occurrence != IntervalItem.Occurrence.Minutes:
            error = "Invalid interval type defined: {}.".format(interval_occurrence)
            raise ValueError(error)
        elif interval_occurrence == IntervalItem.Occurrence.Hours and interval_value not in [1, 2, 4, 6, 8, 12]:
            error = "Invalid hour value defined: {}.".format(interval_value)
            raise ValueError(error)
        elif interval_occurrence == IntervalItem.Occurrence.Minutes and interval_value not in [15, 30]:
            error = "Invalid minute value defined: {}".format(interval_value)
            raise ValueError(error)

        cls._validate_time(start_time)
        cls._validate_time(end_time)
        interval = [(interval_occurrence.lower(), str(interval_value))]
        return cls(IntervalItem.Frequency.Hourly, interval, start_time, end_time)

    @classmethod
    def create_daily(cls, start_time):
        cls._validate_time(start_time)
        return cls(IntervalItem.Frequency.Daily, None, start_time)

    @classmethod
    def create_weekly(cls, start_time, *interval_value):
        interval = []
        for day in interval_value:
            if not hasattr(IntervalItem.Day, day):
                error = "Invalid week day defined: {}.".format(day)
                raise ValueError(error)
            interval.append((IntervalItem.Occurrence.WeekDay, day))
        cls._validate_time(start_time)
        return cls(IntervalItem.Frequency.Weekly, interval, start_time)

    @classmethod
    def create_monthly(cls, start_time, interval_value):
        if (interval_value < 1 or interval_value > 31) and interval_value != IntervalItem.Day.LastDay:
            error = "Invalid interval value defined for a monthly frequency: {}.".format(interval_value)
            raise ValueError(error)
        interval = [(IntervalItem.Occurrence.MonthDay, str(interval_value))]
        cls._validate_time(start_time)
        return cls(IntervalItem.Frequency.Monthly, interval, start_time)

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
        return cls(frequency, interval, start_time, end_time)
