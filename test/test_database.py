import warnings
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.request_factory import RequestFactory

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "database_get.xml"
POPULATE_PERMISSIONS_XML = TEST_ASSET_DIR / "database_populate_permissions.xml"
UPDATE_XML = TEST_ASSET_DIR / "database_update.xml"
GET_DQW_BY_CONTENT = TEST_ASSET_DIR / "dqw_by_content_type.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    server = TSC.Server("http://test", False)
    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.5"

    return server


def test_get(server):
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.databases.baseurl, text=response_xml)
        all_databases, pagination_item = server.databases.get()

    assert 5 == pagination_item.total_available
    assert "5ea59b45-e497-4827-8809-bfe213236f75" == all_databases[0].id
    assert "hyper" == all_databases[0].connection_type
    assert "hyper_0.hyper" == all_databases[0].name

    assert "23591f2c-4802-4d6a-9e28-574a8ea9bc4c" == all_databases[1].id
    assert "sqlserver" == all_databases[1].connection_type
    assert "testv1" == all_databases[1].name
    assert "9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0" == all_databases[1].contact_id
    assert all_databases[1].certified


def test_update(server):
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.databases.baseurl + "/23591f2c-4802-4d6a-9e28-574a8ea9bc4c", text=response_xml)
        single_database = TSC.DatabaseItem("test")
        single_database.contact_id = "9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0"
        single_database._id = "23591f2c-4802-4d6a-9e28-574a8ea9bc4c"
        single_database.certified = True
        single_database.certification_note = "Test"
        single_database = server.databases.update(single_database)

    assert "23591f2c-4802-4d6a-9e28-574a8ea9bc4c" == single_database.id
    assert "9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0" == single_database.contact_id
    assert single_database.certified
    assert "Test" == single_database.certification_note


def test_populate_permissions(server):
    response_xml = POPULATE_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.databases.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)
        single_database = TSC.DatabaseItem("test")
        single_database._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

        server.databases.populate_permissions(single_database)
        permissions = single_database.permissions

        assert permissions[0].grantee.tag_name == "group"
        assert permissions[0].grantee.id == "5e5e1978-71fa-11e4-87dd-7382f5c437af"
        assert permissions[0].capabilities == {
            TSC.Permission.Capability.ChangePermissions: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        }

        assert permissions[1].grantee.tag_name == "user"
        assert permissions[1].grantee.id == "7c37ee24-c4b1-42b6-a154-eaeab7ee330a"
        assert permissions[1].capabilities == {
            TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
        }


def test_populate_data_quality_warning(server):
    response_xml = GET_DQW_BY_CONTENT.read_text()
    with requests_mock.mock() as m:
        m.get(
            server.databases._data_quality_warnings.baseurl + "/94441d26-9a52-4a42-b0fb-3f94792d1aac",
            text=response_xml,
        )
        single_database = TSC.DatabaseItem("test")
        single_database._id = "94441d26-9a52-4a42-b0fb-3f94792d1aac"

        server.databases.populate_dqw(single_database)
        dqws = single_database.dqws
        first_dqw = dqws.pop()
        assert first_dqw.id == "c2e0e406-84fb-4f4e-9998-f20dd9306710"
        assert first_dqw.warning_type == "WARNING"
        assert first_dqw.message == "Hello, World!"
        assert first_dqw.owner_id == "eddc8c5f-6af0-40be-b6b0-2c790290a43f"
        assert first_dqw.active
        assert first_dqw.severe
        assert str(first_dqw.created_at) == "2021-04-09 18:39:54+00:00"
        assert str(first_dqw.updated_at) == "2021-04-09 18:39:54+00:00"


def test_delete(server):
    with requests_mock.mock() as m:
        m.delete(server.databases.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5", status_code=204)
        server.databases.delete("0448d2ed-590d-4fa0-b272-a2a8a24555b5")


def test_populate_tables_not_supported(server):
    database = TSC.DatabaseItem("test")
    database._id = "23591f2c-4802-4d6a-9e28-574a8ea9bc4c"
    with pytest.raises(NotImplementedError, match="Metadata API"):
        server.databases.populate_tables(database)


def _delete_table_default_permission_setup(server, m):
    database = TSC.DatabaseItem("test")
    database._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"
    rule = TSC.PermissionsRule(
        grantee=TSC.GroupItem.as_reference("5e5e1978-71fa-11e4-87dd-7382f5c437af"),
        capabilities={TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow},
    )
    url = (
        f"{server.databases.baseurl}/{database.id}/default-permissions/tables/groups/"
        "5e5e1978-71fa-11e4-87dd-7382f5c437af/Read/Allow"
    )
    m.delete(url, status_code=204)
    return database, rule


def test_delete_table_default_permissions(server):
    with requests_mock.mock() as m, warnings.catch_warnings():
        warnings.simplefilter("error")
        database, rule = _delete_table_default_permission_setup(server, m)
        server.databases.delete_table_default_permissions(database, rule)
        assert m.call_count == 1


def test_delete_table_default_permissions_swapped_arguments_warns(server):
    with requests_mock.mock() as m:
        database, rule = _delete_table_default_permission_setup(server, m)
        with pytest.warns(DeprecationWarning, match="deprecated") as record:
            server.databases.delete_table_default_permissions(rule, database)
        assert m.call_count == 1
    assert record[0].filename == __file__


def test_update_req_omits_unset_fields() -> None:
    item = TSC.DatabaseItem("test")
    xml = ET.fromstring(RequestFactory.Database.update_req(item))
    assert xml.findall("database")[0].attrib == {}


def test_update_req_sends_set_fields() -> None:
    item = TSC.DatabaseItem("test")
    item.certified = False
    item.certification_note = "note"
    item.description = "desc"
    attrib = ET.fromstring(RequestFactory.Database.update_req(item)).findall("database")[0].attrib
    assert attrib["isCertified"] == "false"
    assert attrib["certificationNote"] == "note"
    assert attrib["description"] == "desc"


def test_update_req_empty_strings_clear_fields() -> None:
    item = TSC.DatabaseItem("test")
    item.certification_note = ""
    item.description = ""
    attrib = ET.fromstring(RequestFactory.Database.update_req(item)).findall("database")[0].attrib
    assert attrib == {"certificationNote": "", "description": ""}


def test_update_req_sends_content_permissions() -> None:
    item = TSC.DatabaseItem("test", content_permissions=TSC.DatabaseItem.ContentPermissions.ManagedByOwner)
    attrib = ET.fromstring(RequestFactory.Database.update_req(item)).findall("database")[0].attrib
    assert attrib == {"contentPermissions": "ManagedByOwner"}


def test_update_tags_not_supported(server) -> None:
    server.version = "3.9"
    item = TSC.DatabaseItem("test")
    item._id = "10224773-ecee-42ac-b822-d786b0b8e4d9"
    with pytest.raises(NotImplementedError, match="add_tags and delete_tags"):
        server.databases.update_tags(item)


def test_update_tags_checks_version(server) -> None:
    server.version = "3.5"
    item = TSC.DatabaseItem("test")
    with pytest.raises(TSC.server.exceptions.EndpointUnavailableError):
        server.databases.update_tags(item)
