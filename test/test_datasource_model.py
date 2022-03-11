import unittest

import tableauserverclient as TSC


class DatasourceModelTests(unittest.TestCase):
    def test_invalid_project_id(self):
        self.assertRaises(ValueError, TSC.DatasourceItem, None)
        datasource = TSC.DatasourceItem("10")
        with self.assertRaises(ValueError):
            datasource.project_id = None
