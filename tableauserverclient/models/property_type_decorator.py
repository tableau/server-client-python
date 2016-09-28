from functools import wraps


def property_type(enum_type):
    def property_type_decorator(func):
        @wraps(func)
        def wrapper(self, value):
            if value and not hasattr(enum_type, value):
                error = "Invalid value: {0}. {1} must be of type {2}.".format(value, func.func_name, enum_type.__name__)
                raise ValueError(error)
            return func(self, value)

        return wrapper

    return property_type_decorator


def property_type_boolean(func):
    @wraps(func)
    def wrapper(self, value):
        if not isinstance(value, bool):
            error = "Boolean expected for {0} flag.".format(func.func_name)
        return func(self, value)

    return wrapper
