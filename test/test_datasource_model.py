import datetime
import unittest
import tableauserverclient as TSC


class DatasourceModelTests(unittest.TestCase):
    def test_invalid_project_id(self):
        self.assertRaises(ValueError, TSC.DatasourceItem, None)
        datasource = TSC.DatasourceItem("10")
        with self.assertRaises(ValueError):
            datasource.project_id = None

    def test_datetime_conversion(self):
        datasource = TSC.DatasourceItem("10")
        datasource.created_at = "2016-08-18T19:25:36Z"
        actual = datasource.created_at
        self.assertIsInstance(actual, datetime.datetime)
        self.assertEquals(actual.year, 2016)
        self.assertEquals(actual.month, 8)
        self.assertEquals(actual.day, 18)
        self.assertEquals(actual.hour, 19)
        self.assertEquals(actual.minute, 25)
        self.assertEquals(actual.second, 36)

    def test_datetime_conversion_allows_datetime_passthrough(self):
        datasource = TSC.DatasourceItem("10")
        now = datetime.datetime.utcnow()
        datasource.created_at = now
        self.assertEquals(datasource.created_at, now)

    def test_datetime_conversion_is_timezone_aware(self):
        datasource = TSC.DatasourceItem("10")
        datasource.created_at = "2016-08-18T19:25:36Z"
        actual = datasource.created_at
        self.assertEquals(actual.utcoffset().seconds, 0)

    def test_datetime_conversion_rejects_things_that_cannot_be_converted(self):
        datasource = TSC.DatasourceItem("10")
        with self.assertRaises(ValueError):
            datasource.created_at = object()
        with self.assertRaises(ValueError):
            datasource.created_at = "This is so not a datetime"
