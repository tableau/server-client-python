import inspect

from unittest import TestCase
import _models  # type: ignore  # did not set types for this
import tableauserverclient as TSC

from typing import Any


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


class TestAllModels(TestCase):
    # not all models have __repr__ yet: see above list
    def test_repr_is_implemented(self):
        m = _models.get_defined_models()
        for model in m:
            with self.subTest(model.__name__, model=model):
                print(model.__name__, type(model.__repr__).__name__)
                self.assertEqual(type(model.__repr__).__name__, "function")

    # 2 - Iterate through the objects in the module
    def test_by_reflection(self):
        for class_name, obj in inspect.getmembers(TSC, is_concrete):
            with self.subTest(class_name, obj=obj):
                instantiate_class(class_name, obj)


def is_concrete(obj: Any):
    return inspect.isclass(obj) and not inspect.isabstract(obj)
