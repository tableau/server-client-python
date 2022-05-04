import unittest
import tableauserverclient as TSC
import tableauserverclient.server.request_factory as TSC_RF
from tableauserverclient import DatasourceItem


class DatasourceRequestTests(unittest.TestCase):
    def test_generate_xml(self):
        datasource_item: TSC.DatasourceItem = TSC.DatasourceItem("name")
        datasource_item.name = "a ds"
        datasource_item.description = "described"
        datasource_item.use_remote_query_agent = False
        datasource_item.ask_data_enablement = DatasourceItem.AskDataEnablement.Enabled
        datasource_item.project_id = "testval"
        TSC_RF.RequestFactory.Datasource._generate_xml(datasource_item)
