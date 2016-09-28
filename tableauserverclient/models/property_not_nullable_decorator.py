from functools import wraps


def property_not_nullable(func):
    @wraps(func)
    def wrapper(self, value):
        if value is None:
            error = "{0} must be defined.".format(func.func_name)
            raise ValueError(error)
        return func(self, value)

    return wrapper
