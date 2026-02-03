import os
import unittest

import tableauserverclient as TSC


class FilterTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_filter_equal(self):
        filter = TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "Superstore")

        self.assertEqual(str(filter), "name:eq:Superstore")

    def test_filter_in(self):
        # create a IN filter condition with project names that
        # contain spaces and "special" characters
        projects_to_find = ["default", "Salesforce Sales Projeśt"]
        filter = TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.In, projects_to_find)

        self.assertEqual(str(filter), "name:in:[default,Salesforce Sales Projeśt]")
