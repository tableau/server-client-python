import unittest
import tableauserverclient as TSC


class DatasourceModelTests(unittest.TestCase):
    def test_require_boolean_query_tag_fails(self):
        conn = TSC.ConnectionItem()
        conn._connection_type = "postgres"
        with self.assertRaises(ValueError):
            conn.query_tagging = "no"

    def test_set_query_tag_normal_conn(self):
        conn = TSC.ConnectionItem()
        conn._connection_type = "postgres"
        conn.query_tagging = True
        self.assertEqual(conn.query_tagging, True)

    def test_ignore_query_tag_for_hyper(self):
        conn = TSC.ConnectionItem()
        conn._connection_type = "hyper"
        conn.query_tagging = True
        self.assertEqual(conn.query_tagging, None)

    def test_ignore_query_tag_for_teradata(self):
        conn = TSC.ConnectionItem()
        conn._connection_type = "teradata"
        conn.query_tagging = True
        self.assertEqual(conn.query_tagging, None)

    def test_ignore_query_tag_for_snowflake(self):
        conn = TSC.ConnectionItem()
        conn._connection_type = "snowflake"
        conn.query_tagging = True
        self.assertEqual(conn.query_tagging, None)
