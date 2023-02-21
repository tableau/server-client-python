import pytest

from unittest import TestCase
import _models


# ensure that all models have a __repr__ method implemented
class TestAllModels(TestCase):

    """
    ColumnItem wrapper_descriptor
    ConnectionCredentials wrapper_descriptor
    DataAccelerationReportItem wrapper_descriptor
    DatabaseItem wrapper_descriptor
    DQWItem wrapper_descriptor
    UnpopulatedPropertyError wrapper_descriptor
    FavoriteItem wrapper_descriptor
    FlowRunItem wrapper_descriptor
    IntervalItem wrapper_descriptor
    DailyInterval wrapper_descriptor
    WeeklyInterval wrapper_descriptor
    MonthlyInterval wrapper_descriptor
    HourlyInterval wrapper_descriptor
    BackgroundJobItem wrapper_descriptor
    PaginationItem wrapper_descriptor
    Permission wrapper_descriptor
    ServerInfoItem wrapper_descriptor
    SiteItem wrapper_descriptor
    TableItem wrapper_descriptor
    Resource wrapper_descriptor
    """

    # not all models have __repr__ yet: see above list
    @pytest.mark.xfail()
    def test_repr_is_implemented(self):
        m = _models.get_defined_models()
        for model in m:
            with self.subTest(model.__name__, model=model):
                print(model.__name__, type(model.__repr__).__name__)
                self.assertEqual(type(model.__repr__).__name__, "function")
