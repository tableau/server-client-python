import tableauserverclient as TSC
import tableauserverclient.server.request_factory as TSC_RF
from tableauserverclient.helpers.strings import redact_xml
import pytest
import sys


def test_embedded_extract_req() -> None:
    include_all = True
    embedded_datasources = None
    xml_result = TSC_RF.RequestFactory.Workbook.embedded_extract_req(include_all, embedded_datasources)


def test_generate_xml() -> None:
    workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
    TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item)


def test_generate_xml_invalid_connection() -> None:
    workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
    conn = TSC.ConnectionItem()
    with pytest.raises(ValueError):
        request = TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item, connections=[conn])


def test_generate_xml_invalid_connection_credentials() -> None:
    workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
    conn = TSC.ConnectionItem()
    conn.server_address = "address"
    creds = TSC.ConnectionCredentials("username", "password")
    creds.name = None
    conn.connection_credentials = creds
    with pytest.raises(ValueError):
        request = TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item, connections=[conn])


def test_generate_xml_valid_connection_credentials() -> None:
    workbook_item: TSC.WorkbookItem = TSC.WorkbookItem("name", "project_id")
    conn = TSC.ConnectionItem()
    conn.server_address = "address"
    creds = TSC.ConnectionCredentials("username", "DELETEME")
    conn.connection_credentials = creds
    request = TSC_RF.RequestFactory.Workbook._generate_xml(workbook_item, connections=[conn])
    assert request.find(b"DELETEME") > 0


def test_redact_passwords_in_xml() -> None:
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
