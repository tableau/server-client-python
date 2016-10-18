import re
from functools import wraps


def property_is_enum(enum_type):
    def property_type_decorator(func):
        @wraps(func)
        def wrapper(self, value):
            if value is not None and not hasattr(enum_type, value):
                error = "Invalid value: {0}. {1} must be of type {2}.".format(value, func.__name__, enum_type.__name__)
                raise ValueError(error)
            return func(self, value)

        return wrapper

    return property_type_decorator


def property_is_boolean(func):
    @wraps(func)
    def wrapper(self, value):
        if not isinstance(value, bool):
            error = "Boolean expected for {0} flag.".format(func.__name__)
            raise ValueError(error)
        return func(self, value)

    return wrapper


def property_not_nullable(func):
    @wraps(func)
    def wrapper(self, value):
        if value is None:
            error = "{0} must be defined.".format(func.__name__)
            raise ValueError(error)
        return func(self, value)

    return wrapper


def property_not_empty(func):
    @wraps(func)
    def wrapper(self, value):
        if not value:
            error = "{0} must not be empty.".format(func.__name__)
            raise ValueError(error)
        return func(self, value)

    return wrapper


def property_is_valid_time(func):
    @wraps(func)
    def wrapper(self, value):
        units_of_time = {"hour", "minute", "second"}

        if not any(hasattr(value, unit) for unit in units_of_time):
            error = "Invalid time object defined."
            raise ValueError(error)
        return func(self, value)

    return wrapper


def property_is_int(range):
    def property_type_decorator(func):
        @wraps(func)
        def wrapper(self, value):
            error = "Invalid priority defined: {}.".format(value)

            if range is None:
                if isinstance(value, int):
                    return func(self, value)
                else:
                    raise ValueError(error)

            min, max = range

            if value < min or value > max:

                raise ValueError(error)

            return func(self, value)

        return wrapper

    return property_type_decorator


def property_matches(regex_to_match, error):

    compiled_re = re.compile(regex_to_match)

    def wrapper(func):
        @wraps(func)
        def validate_regex_decorator(self, value):
            if not compiled_re.match(value):
                raise ValueError(error)
            return func(self, value)
        return validate_regex_decorator
    return wrapper
