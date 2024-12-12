import unittest
import tableauserverclient as TSC


class DatasourceModelTests(unittest.TestCase):
    def test_nullable_project_id(self):
        datasource = TSC.DatasourceItem(name="10")
        self.assertEqual(datasource.project_id, None)

    def test_require_boolean_flag_bridge_fail(self):
        datasource = TSC.DatasourceItem("10")
        with self.assertRaises(ValueError):
            datasource.use_remote_query_agent = "yes"

    def test_require_boolean_flag_bridge_ok(self):
        datasource = TSC.DatasourceItem("10")
        datasource.use_remote_query_agent = True
        self.assertEqual(datasource.use_remote_query_agent, True)
