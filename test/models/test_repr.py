import inspect

from unittest import TestCase
import tableauserverclient.models as TSC_models  # type: ignore  # did not set types for this
import tableauserverclient as TSC

from typing import Any


# ensure that all models can be instantiated
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


not_yet_done = [
    "DQWItem",
    "UnpopulatedPropertyError",
    "FavoriteItem",
    "FileuploadItem",
    "FlowRunItem",
    "IntervalItem",
    "LinkedTaskItem",
    "LinkedTaskStepItem",
    "LinkedTaskFlowRunItem",
    "Permission",
    "SiteAuthConfiguration",
    "Resource",
    "TagItem",
    "ExtractItem",
]


class TestAllModels(TestCase):

    # confirm that all models can be instantiated without params, and have __repr__ implemented
    # not all do have __repr__ yet: see above list 'not_yet_done'
    def test_repr_is_implemented(self):
        m = TSC_models
        for type_name in m.__dict__:
            if type_name in not_yet_done:
                continue
            model = getattr(m, type_name)
            if inspect.isclass(model):
                with self.subTest(type_name):
                    self.assertTrue(hasattr(model, "__repr__"))
                    self.assertEqual(type(model.__repr__).__name__, "function")

    # 2 - Iterate through the objects in the module
    def test_by_reflection(self):
        for class_name, obj in inspect.getmembers(TSC, is_concrete):
            with self.subTest(class_name, obj=obj):
                instantiate_class(class_name, obj)


def is_concrete(obj: Any):
    return inspect.isclass(obj) and not inspect.isabstract(obj)
