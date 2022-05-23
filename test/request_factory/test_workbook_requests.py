import unittest
import tableauserverclient as TSC
import tableauserverclient.server.request_factory as TSC_RF
from tableauserverclient.helpers.strings import redact_xml
import pytest
import sys


class WorkbookRequestTests(unittest.TestCase):
    def test_embedded_extract_req(self):
        include_all = True
        embedded_datasources = None
        xml_result = TSC_RF.RequestFactory.Workbook.embedded_extract_req(include_all, embedded_datasources)

    def test_generate_xml(self):
        workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
        TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item)

    def test_generate_xml_invalid_connection(self):
        workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
        conn = TSC.ConnectionItem()
        with self.assertRaises(ValueError):
            request = TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item, connections=[conn])

    def test_generate_xml_invalid_connection_credentials(self):
        workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
        conn = TSC.ConnectionItem()
        conn.server_address = "address"
        creds = TSC.ConnectionCredentials("username", "password")
        creds.name = None
        conn.connection_credentials = creds
        with self.assertRaises(ValueError):
            request = TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item, connections=[conn])

    def test_generate_xml_valid_connection_credentials(self):
        workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
        conn = TSC.ConnectionItem()
        conn.server_address = "address"
        creds = TSC.ConnectionCredentials("username", "DELETEME")
        conn.connection_credentials = creds
        request = TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item, connections=[conn])
        assert request.find(b"DELETEME") > 0

    def test_redact_passwords_in_xml(self):
        if sys.version_info < (3, 7):
            pytest.skip("Redaction is only implemented for 3.7+.")
        workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
        conn = TSC.ConnectionItem()
        conn.server_address = "address"
        creds = TSC.ConnectionCredentials("username", "DELETEME")
        conn.connection_credentials = creds
        request = TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item, connections=[conn])
        redacted = redact_xml(request)
        assert request.find(b"DELETEME") > 0, request
        assert redacted.find(b"DELETEME") == -1, redacted
