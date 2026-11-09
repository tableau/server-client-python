from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.request_factory import RequestFactory

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "table_get.xml"
UPDATE_XML = TEST_ASSET_DIR / "table_update.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.5"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.tables.baseurl, text=response_xml)
        all_tables, pagination_item = server.tables.get()

    assert 4 == pagination_item.total_available
    assert "10224773-ecee-42ac-b822-d786b0b8e4d9" == all_tables[0].id
    assert "dim_Product" == all_tables[0].name

    assert "53c77bc1-fb41-4342-a75a-f68ac0656d0d" == all_tables[1].id
    assert "customer" == all_tables[1].name
    assert "dbo" == all_tables[1].schema
    assert "9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0" == all_tables[1].contact_id
    assert False == all_tables[1].certified


def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.tables.baseurl + "/10224773-ecee-42ac-b822-d786b0b8e4d9", text=response_xml)
        single_table = TSC.TableItem("test")
        single_table._id = "10224773-ecee-42ac-b822-d786b0b8e4d9"

        single_table.contact_id = "8e1a8235-c9ee-4d61-ae82-2ffacceed8e0"
        single_table.certified = True
        single_table.certification_note = "Test"
        single_table = server.tables.update(single_table)

    assert "10224773-ecee-42ac-b822-d786b0b8e4d9" == single_table.id
    assert "8e1a8235-c9ee-4d61-ae82-2ffacceed8e0" == single_table.contact_id
    assert True == single_table.certified
    assert "Test" == single_table.certification_note


def test_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.tables.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5", status_code=204)
        server.tables.delete("0448d2ed-590d-4fa0-b272-a2a8a24555b5")


def test_update_req_omits_unset_fields() -> None:
    item = TSC.TableItem("test")
    xml = ET.fromstring(RequestFactory.Table.update_req(item))
    assert xml.findall("table")[0].attrib == {}


def test_update_req_sends_set_fields() -> None:
    item = TSC.TableItem("test")
    item.certified = False
    item.certification_note = "note"
    item.description = "desc"
    attrib = ET.fromstring(RequestFactory.Table.update_req(item)).findall("table")[0].attrib
    assert attrib["isCertified"] == "false"
    assert attrib["certificationNote"] == "note"
    assert attrib["description"] == "desc"


def test_update_req_empty_strings_clear_fields() -> None:
    item = TSC.TableItem("test")
    item.certification_note = ""
    item.description = ""
    attrib = ET.fromstring(RequestFactory.Table.update_req(item)).findall("table")[0].attrib
    assert attrib == {"certificationNote": "", "description": ""}


def test_update_tags_not_supported(server) -> None:
    server.version = "3.9"
    item = TSC.TableItem("test")
    item._id = "10224773-ecee-42ac-b822-d786b0b8e4d9"
    with pytest.raises(NotImplementedError, match="add_tags and delete_tags"):
        server.tables.update_tags(item)


def test_update_tags_checks_version(server) -> None:
    server.version = "3.5"
    item = TSC.TableItem("test")
    with pytest.raises(TSC.server.exceptions.EndpointUnavailableError):
        server.tables.update_tags(item)
