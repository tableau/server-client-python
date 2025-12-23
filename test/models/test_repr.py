import inspect
from typing import Any

import _models  # type: ignore  # did not set types for this
import tableauserverclient as TSC

import pytest


# ensure that all models that don't need parameters can be instantiated
# todo....
def instantiate_class(name: str, obj: Any):
    # Get the constructor (init) of the class
    constructor = getattr(obj, "__init__", None)
    if constructor:
        # Get the parameters of the constructor (excluding 'self')
        parameters = inspect.signature(constructor).parameters.values()
        required_parameters = [
            param for param in parameters if param.default == inspect.Parameter.empty and param.name != "self"
        ]
        if required_parameters:
            print(f"Class '{name}' requires the following parameters for instantiation:")
            for param in required_parameters:
                print(f"- {param.name}")
        else:
            print(f"Class '{name}' does not require any parameters for instantiation.")
            # Instantiate the class
            instance = obj()
            print(f"Instantiated: {name} -> {instance}")
    else:
        print(f"Class '{name}' does not have a constructor (__init__ method).")


def is_concrete(obj: Any):
    return inspect.isclass(obj) and not inspect.isabstract(obj)


@pytest.mark.parametrize("class_name, obj", inspect.getmembers(TSC, is_concrete))
def test_by_reflection(class_name, obj):
    instantiate_class(class_name, obj)


@pytest.mark.parametrize("model", _models.get_defined_models())
def test_repr_is_implemented(model):
    print(model.__name__, type(model.__repr__).__name__)
    assert type(model.__repr__).__name__ == "function"
