from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC

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
