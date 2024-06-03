from .property_decorators import property_is_valid_time, property_not_nullable


class IntervalItem(object):
    class Frequency:
        Hourly = "Hourly"
        Daily = "Daily"
        Weekly = "Weekly"
        Monthly = "Monthly"

    class Occurrence:
        Minutes = "minutes"
        Hours = "hours"
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
    def __init__(self, start_time, end_time, interval_value):
        self.start_time = start_time
        self.end_time = end_time

        # interval should be a tuple, if it is not, assign as a tuple with single value
        if isinstance(interval_value, tuple):
            self.interval = interval_value
        else:
            self.interval = (interval_value,)

    def __repr__(self):
        return f"<{self.__class__.__name__} start={self.start_time} end={self.end_time} interval={self.interval}>"

    @property
    def _frequency(self):
        return IntervalItem.Frequency.Hourly

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    @property_not_nullable
    def start_time(self, value):
        self._start_time = value

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    @property_is_valid_time
    @property_not_nullable
    def end_time(self, value):
        self._end_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, intervals):
        VALID_INTERVALS = {0.25, 0.5, 1, 2, 4, 6, 8, 12, 24}
        for interval in intervals:
            # if an hourly interval is a string, then it is a weekDay interval
            if isinstance(interval, str) and not interval.isnumeric() and not hasattr(IntervalItem.Day, interval):
                error = "Invalid weekDay interval {}".format(interval)
                raise ValueError(error)

            # if an hourly interval is a number, it is an hours or minutes interval
            if isinstance(interval, (int, float)) and float(interval) not in VALID_INTERVALS:
                error = "Invalid interval {} not in {}".format(interval, str(VALID_INTERVALS))
                raise ValueError(error)

        self._interval = intervals

    def _interval_type_pairs(self):
        interval_type_pairs = []
        for interval in self.interval:
            # We use fractional hours for the two minute-based intervals.
            # Need to convert to minutes from hours here
            if interval in {0.25, 0.5}:
                calculated_interval = int(interval * 60)
                interval_type = IntervalItem.Occurrence.Minutes

                interval_type_pairs.append((interval_type, str(calculated_interval)))
            else:
                # if the interval is a non-numeric string, it will always be a weekDay
                if isinstance(interval, str) and not interval.isnumeric():
                    interval_type = IntervalItem.Occurrence.WeekDay

                    interval_type_pairs.append((interval_type, str(interval)))
                # otherwise the interval is hours
                else:
                    interval_type = IntervalItem.Occurrence.Hours

                    interval_type_pairs.append((interval_type, str(interval)))

        return interval_type_pairs


class DailyInterval(object):
    def __init__(self, start_time, *interval_values):
        self.start_time = start_time
        self.interval = interval_values

    def __repr__(self):
        return f"<{self.__class__.__name__} start={self.start_time} interval={self.interval}>"

    @property
    def _frequency(self):
        return IntervalItem.Frequency.Daily

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    @property_not_nullable
    def start_time(self, value):
        self._start_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, intervals):
        VALID_INTERVALS = {0.25, 0.5, 1, 2, 4, 6, 8, 12, 24}

        for interval in intervals:
            # if an hourly interval is a string, then it is a weekDay interval
            if isinstance(interval, str) and not interval.isnumeric() and not hasattr(IntervalItem.Day, interval):
                error = "Invalid weekDay interval {}".format(interval)
                raise ValueError(error)

            # if an hourly interval is a number, it is an hours or minutes interval
            if isinstance(interval, (int, float)) and float(interval) not in VALID_INTERVALS:
                error = "Invalid interval {} not in {}".format(interval, str(VALID_INTERVALS))
                raise ValueError(error)

        self._interval = intervals

    def _interval_type_pairs(self):
        interval_type_pairs = []
        for interval in self.interval:
            # We use fractional hours for the two minute-based intervals.
            # Need to convert to minutes from hours here
            if interval in {0.25, 0.5}:
                calculated_interval = int(interval * 60)
                interval_type = IntervalItem.Occurrence.Minutes

                interval_type_pairs.append((interval_type, str(calculated_interval)))
            else:
                # if the interval is a non-numeric string, it will always be a weekDay
                if isinstance(interval, str) and not interval.isnumeric():
                    interval_type = IntervalItem.Occurrence.WeekDay

                    interval_type_pairs.append((interval_type, str(interval)))
                # otherwise the interval is hours
                else:
                    interval_type = IntervalItem.Occurrence.Hours

                    interval_type_pairs.append((interval_type, str(interval)))

        return interval_type_pairs


class WeeklyInterval(object):
    def __init__(self, start_time, *interval_values):
        self.start_time = start_time
        self.interval = interval_values

    def __repr__(self):
        return f"<{self.__class__.__name__} start={self.start_time} interval={self.interval}>"

    @property
    def _frequency(self):
        return IntervalItem.Frequency.Weekly

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    @property_not_nullable
    def start_time(self, value):
        self._start_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval_values):
        if not all(hasattr(IntervalItem.Day, day) for day in interval_values):
            raise ValueError("Invalid week day defined " + str(interval_values))

        self._interval = interval_values

    def _interval_type_pairs(self):
        return [(IntervalItem.Occurrence.WeekDay, day) for day in self.interval]


class MonthlyInterval(object):
    def __init__(self, start_time, interval_value):
        self.start_time = start_time

        # interval should be a tuple, if it is not, assign as a tuple with single value
        if isinstance(interval_value, tuple):
            self.interval = interval_value
        else:
            self.interval = (interval_value,)

    def __repr__(self):
        return f"<{self.__class__.__name__} start={self.start_time} interval={self.interval}>"

    @property
    def _frequency(self):
        return IntervalItem.Frequency.Monthly

    @property
    def start_time(self):
        return self._start_time

    @start_time.setter
    @property_is_valid_time
    @property_not_nullable
    def start_time(self, value):
        self._start_time = value

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, interval_values):
        # This is weird because the value could be a str or an int
        # The only valid str is 'LastDay' so we check that first. If that's not it
        # try to convert it to an int, if that fails because it's an incorrect string
        # like 'badstring' we catch and re-raise. Otherwise we convert to int and check
        # that it's in range 1-31
        for interval_value in interval_values:
            error = "Invalid interval value for a monthly frequency: {}.".format(interval_value)

            if interval_value != "LastDay":
                try:
                    if not (1 <= int(interval_value) <= 31):
                        raise ValueError(error)
                except ValueError:
                    if interval_value != "LastDay":
                        raise ValueError(error)

        self._interval = interval_values

    def _interval_type_pairs(self):
        return [(IntervalItem.Occurrence.MonthDay, self.interval)]
