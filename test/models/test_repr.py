import inspect
from typing import Any
from test.models._models import get_unimplemented_models
import tableauserverclient as TSC

import pytest


def is_concrete(obj: Any):
    return inspect.isclass(obj) and not inspect.isabstract(obj)

@pytest.mark.parametrize("class_name, obj", inspect.getmembers(TSC, is_concrete))
def test_by_reflection(class_name, obj):
    instance = try_instantiate_class(class_name, obj)
    if instance:
        class_type = type(instance)
        if class_type in get_unimplemented_models():
            print(f"Class '{class_name}' has no repr defined, skipping test")
            return
        else:
            assert type(instance.__repr__).__name__ == "method"
            print(instance.__repr__.__name__)



# Instantiate a class if it doesn't require any parameters
def try_instantiate_class(name: str, obj: Any) -> Any | None:
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
            return None
        else:
            print(f"Class '{name}' does not require any parameters for instantiation.")
            # Instantiate the class
            instance = obj()
            return instance
    else:
        print(f"Class '{name}' does not have a constructor (__init__ method).")
        return None
