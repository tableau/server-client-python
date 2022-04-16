import unittest
import tableauserverclient as TSC
import tableauserverclient.server.request_factory as TSC_RF


class WorkbookRequestTests(unittest.TestCase):
    def test_embedded_extract_req(self):
        include_all = True
        embedded_datasources = None
        xml_result = TSC_RF.RequestFactory.Workbook.embedded_extract_req(include_all, embedded_datasources)

    def test_generate_xml(self):
        workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name")
        workbook_item.project_id = "testval"
        workbook_item.show_tabs = False
        TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item)
