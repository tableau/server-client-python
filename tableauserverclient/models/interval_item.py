import xml.etree.ElementTree as ET
from datetime import datetime
from .property_decorators import property_is_valid_time
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


class HourlyInterval(object):
    def __init__(self, start_time, end_time, interval_occurrence, interval_value):

        self.start_time = start_time
        self.end_time = end_time
        self._frequency = IntervalItem.Frequency.Hourly
        self.interval = interval_occurrence, str(interval_value)

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    def start_time(self, value):
        self._start_time = value

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    @property_is_valid_time
    def end_time(self, value):
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
        VALID_OCCUR_TYPES = {Hours, Minutes}

        if interval_occurrence not in VALID_OCCUR_TYPES:
            error = "Invalid interval type {} not in {}.".format(interval_occurrence, str(VALID_OCCUR_TYPES))
            raise ValueError(error)
        elif interval_occurrence == Hours and int(interval_value) not in VALID_HOUR_INTERVALS:
            error = "Invalid hour value {} not in {}".format(interval_value, str(VALID_HOUR_INTERVALS))
            raise ValueError(error)
        elif interval_occurrence == Minutes and int(interval_value) not in VALID_MIN_INTERVALS:
            error = "Invalid minute value {} not in {}".format(interval_value, str(VALID_MIN_INTERVALS))
            raise ValueError(error)

        self._interval = [(interval_occurrence, str(interval_value))]


class DailyInterval(object):
    def __init__(self, start_time):
        self.start_time = start_time
        self._frequency = IntervalItem.Frequency.Daily
        self.end_time = None
        self.interval = None

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    def start_time(self, value):
        self._start_time = value


class WeeklyInterval(object):
    def __init__(self, start_time, *interval_values):
        self.start_time = start_time
        self._frequency = IntervalItem.Frequency.Weekly
        self.interval = interval_values
        self.end_time = None

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    def start_time(self, value):
        self._start_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval_values):
        if not all(hasattr(IntervalItem.Day, day) for day in interval_values):
            raise ValueError("Invalid week day defined " + str(interval_values))

        self._interval = [(IntervalItem.Occurrence.WeekDay, day) for day in interval_values]


class MonthlyInterval(object):
    def __init__(self, start_time, interval_value):
        self.start_time = start_time
        self._frequency = IntervalItem.Frequency.Monthly
        self.interval = str(interval_value)
        self.end_time = None

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    def start_time(self, value):
        self._start_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval_value):
        error = "Invalid interval value for a monthly frequency: {}.".format(interval_value)

        # This is weird because the value could be a str or an int
        # The only valid str is 'LastDay' so we check that first. If that's not it
        # try to convert it to an int, if that fails because it's an incorrect string
        # like 'badstring' we catch and re-raise. Otherwise we convert to int and check
        # that it's in range 1-31

        if interval_value != "LastDay":
            try:
                if not (1 <= int(interval_value) <= 31):
                    raise ValueError(error)
            except ValueError as e:
                if interval_value != "LastDay":
                    raise ValueError(error)

        self._interval = [(IntervalItem.Occurrence.MonthDay, str(interval_value))]
