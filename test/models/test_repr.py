from unittest import TestCase
import _models  # type: ignore  # did not set types for this


# ensure that all models have a __repr__ method implemented
class TestAllModels(TestCase):

    # not all models have __repr__ yet: see above list
    def test_repr_is_implemented(self):
        m = _models.get_defined_models()
        for model in m:
            with self.subTest(model.__name__, model=model):
                print(model.__name__, type(model.__repr__).__name__)
                self.assertEqual(type(model.__repr__).__name__, "function")
