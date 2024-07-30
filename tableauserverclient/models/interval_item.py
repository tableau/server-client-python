from abc import abstractmethod
from enum import StrEnum
from .property_decorators import property_is_valid_time, property_not_nullable


class IntervalItem(object):
    class Frequency(StrEnum):
        Hourly = "Hourly"
        Daily = "Daily"
        Weekly = "Weekly"
        Monthly = "Monthly"

    class Occurrence(StrEnum):
        Minutes = "minutes"
        Hours = "hours"
        WeekDay = "weekDay"
        MonthDay = "monthDay"
        MonthWeek = "monthWeek" # e.g every 2nd Tuesday

    class Day(StrEnum):
        Sunday = "Sunday"
        Monday = "Monday"
        Tuesday = "Tuesday"
        Wednesday = "Wednesday"
        Thursday = "Thursday"
        Friday = "Friday"
        Saturday = "Saturday"
        LastDay = "LastDay"
    
    
class BaseInterval:
    def __init__(self, start_time, end_time, interval_value):
        self.start_time = start_time
        if end_time:
            self.end_time = end_time
        self._interval = interval_value

    def __repr__(self):
        end = f" end={self.end_time}" if end else ""
        return f"<{self.__class__.__name__} start={self.start_time}{end} interval={self.interval}>"

    @property
    def _frequency(self):
        return self._frequency

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
    def end_time(self, value):
        self._end_time = value

    @property
    def interval(self):
        return self._interval

    # must be implemented by each subclass
    @interval.setter
    @abstractmethod
    def interval(self, intervals):
        assert(False)
    

class HourlyInterval(BaseInterval):

    # requires exactly one of an hours or minutes attribute
    # can have any number of weekday attributes (TODO: what happens if there is none? is it valid to repeat a weekday?)

    @classmethod
    def __init__(self, start_time, end_time, interval_value):
        self._frequency = IntervalItem.Frequency.Hourly
        # interval should be a tuple, if it is not, assign as a tuple with single value
        if isinstance(interval_value, tuple):
            self.interval = interval_value
        else:
            self.interval = (interval_value,)
        super.__init__(self, start_time, end_time, self.interval)
            
    HOUR_VALUE = 1
    MINUTE_VALUE = 60

    def interval(self, intervals):
        
        count_hours = 0
        for interval in intervals:
            # if an hourly interval is a string, then it is a weekDay interval
            if isinstance(interval, str) and not interval.isnumeric():
                if not hasattr(IntervalItem.Day, interval):
                    error = "Invalid weekDay interval {}".format(interval)
                    raise ValueError(error)
                interval_type = IntervalItem.Occurrence.WeekDay
                interval_value = interval

            # if an hourly interval is a number, it is an hours or minutes interval
            elif isinstance(interval, int):
                if count_hours > 0:
                    raise ValueError("The schedule must have exactly one value for hours/minutes between runs.")
                count_hours = count_hours + 1
                if interval == self.HOUR_VALUE:
                    interval_type = IntervalItem.Occurrence.Hours
                    interval_value = interval
                elif interval == self.MINUTE_VALUE:
                    interval_type = IntervalItem.Occurrence.Minutes
                    interval_value = self.to_minutes(interval)
                else:
                    error = "Invalid interval {} not in {}".format(interval, list(self.HOUR_VALUE, self.MINUTE_VALUE))
                    raise ValueError(error)
            else: 
                error = "Invalid interval {} must be a Weekday or an integer.".format(interval)
                raise ValueError(error)
                
            self._interval_type_pairs.append((interval_type, str(interval_value)))
        self._interval = intervals



class DailyInterval(BaseInterval):
    def __init__(self, start_time, end_time, *interval_values):
        super.__init__(self, start_time, end_time, *interval_values)
        self._frequency = IntervalItem.Occurrence.WeekDay

    @property
    def interval(self):
        return self._interval

    @interval.setter
    def interval(self, intervals):
        VALID_INTERVALS = {0.25, 0.5, 1, 2, 4, 6, 8, 12, 24}
        # must have exactly one defined hours attribute. If the value is <24, it must also have an endtime
        # can have any number of weekday attributes. 
        # TODO: What happens if none? is it valid to repeat a weekday?
        
        for interval in intervals:
            # if an hourly interval is a string, then it is a weekDay interval
            if isinstance(interval, str) and not interval.isnumeric() and not hasattr(IntervalItem.Day, interval):
                error = f"Invalid weekDay interval {interval}"
                raise ValueError(error)

            # if an hourly interval is a number, it is an hours or minutes interval
            if isinstance(interval, (int, float)) and float(interval) not in VALID_INTERVALS:
                error = f"Invalid interval {interval} not in {str(VALID_INTERVALS)}"
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


class WeeklyInterval(IntervalItem):
    def __init__(self, start_time, *interval_values):
        super.__init__(self, start_time)
        self._frequency = IntervalItem.Frequency.Weekly

        """
        Note: Updating a schedule without specifying days of the week will reset any existing weekly interval 
        to include all 7 days. If you need the job you are updating to remain scheduled on selected days, make 
        sure to include that information in your update request. 
        """
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


class MonthlyInterval(IntervalItem):
    def __init__(self, start_time, interval_value):
        super.__init__(self, start_time)
        self._frequency = IntervalItem.Frequency.Monthly

        # interval should be a tuple, if it is not, assign as a tuple with single value
        if isinstance(interval_value, tuple):
            self.interval = interval_value
        else:
            self.interval = (interval_value,)

    def interval(self, interval_values):
            
        error = "Invalid interval value for a monthly frequency: {}.".format(interval_values)
        # There are two possible formats for this: (day_of_month) or (occurrence_of_weekday, weekday)
        
        # Which week of the month it should occur
        VALID_OCCURRENCE = ["First", "Second", "Third", "Fourth", "Fifth", IntervalItem.LastDay]

        # Valid values are the whole numbers 1 to 31 or LastDay.
        # This could be a str or int, but there's only 32 possible values so just manually check the whole set
        VALID_DAY_OF_MONTH = list(range(32)).append(IntervalItem.LastDay)        
        
        VALID_WEEKDAY = list(IntervalItem.Day.__members__)
        
        # This is weird because the value could be a str or an int
        # The only valid str is 'LastDay' so we check that first. If that's not it
        # try to convert it to an int, if that fails because it's an incorrect string
        # like 'badstring' we catch and re-raise. Otherwise we convert to int and check
        # that it's in range 1-31
        for interval_value in interval_values:
            error = "Invalid interval value for a monthly frequency: {}.".format(interval_value)

        for interval_value in interval_values:
            if interval_value not in VALID_INTERVALS:
                error = f"Invalid monthly interval: {interval_value}"
                raise ValueError(error)

        self._interval = interval_values

    def _interval_type_pairs(self):
        return [(IntervalItem.Occurrence.MonthDay, self.interval)]
    