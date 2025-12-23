from pathlib import Path

from defusedxml import ElementTree as ET
import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime, parse_datetime
from tableauserverclient.server.endpoint.users_endpoint import create_users_csv, remove_users_csv

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "user_get.xml"
GET_XML_ALL_FIELDS = TEST_ASSET_DIR / "user_get_all_fields.xml"
GET_EMPTY_XML = TEST_ASSET_DIR / "user_get_empty.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "user_get_by_id.xml"
UPDATE_XML = TEST_ASSET_DIR / "user_update.xml"
ADD_XML = TEST_ASSET_DIR / "user_add.xml"
POPULATE_WORKBOOKS_XML = TEST_ASSET_DIR / "user_populate_workbooks.xml"
GET_FAVORITES_XML = TEST_ASSET_DIR / "favorites_get.xml"
POPULATE_GROUPS_XML = TEST_ASSET_DIR / "user_populate_groups.xml"

USERNAMES = TEST_ASSET_DIR / "Data" / "usernames.csv"
USERS = TEST_ASSET_DIR / "Data" / "user_details.csv"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.users.baseurl + "?fields=_all_", text=response_xml)
        all_users, pagination_item = server.users.get()

    assert 2 == pagination_item.total_available
    assert 2 == len(all_users)

    assert any(user.id == "dd2239f6-ddf1-4107-981a-4cf94e415794" for user in all_users)
    single_user = next(user for user in all_users if user.id == "dd2239f6-ddf1-4107-981a-4cf94e415794")
    assert "alice" == single_user.name
    assert "Publisher" == single_user.site_role
    assert "2016-08-16T23:17:06Z" == format_datetime(single_user.last_login)
    assert "alice cook" == single_user.fullname
    assert "alicecook@test.com" == single_user.email

    assert any(user.id == "2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3" for user in all_users)
    single_user = next(user for user in all_users if user.id == "2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3")
    assert "Bob" == single_user.name
    assert "Interactor" == single_user.site_role
    assert "Bob Smith" == single_user.fullname
    assert "bob@test.com" == single_user.email


def test_get_empty(server: TSC.Server) -> None:
    response_xml = GET_EMPTY_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.users.baseurl, text=response_xml)
        all_users, pagination_item = server.users.get()

    assert 0 == pagination_item.total_available
    assert [] == all_users


def test_get_before_signin(server: TSC.Server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.users.get()


def test_get_by_id(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.users.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794", text=response_xml)
        single_user = server.users.get_by_id("dd2239f6-ddf1-4107-981a-4cf94e415794")

    assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == single_user.id
    assert "alice" == single_user.name
    assert "Alice" == single_user.fullname
    assert "Publisher" == single_user.site_role
    assert "ServerDefault" == single_user.auth_setting
    assert "2016-08-16T23:17:06Z" == format_datetime(single_user.last_login)
    assert "local" == single_user.domain_name


def test_get_by_id_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.users.get_by_id("")


def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.users.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794", text=response_xml)
        single_user = TSC.UserItem("test", "Viewer")
        single_user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_user.name = "Cassie"
        single_user.fullname = "Cassie"
        single_user.email = "cassie@email.com"
        single_user = server.users.update(single_user)

    assert "Cassie" == single_user.name
    assert "Cassie" == single_user.fullname
    assert "cassie@email.com" == single_user.email
    assert "Viewer" == single_user.site_role


def test_update_missing_id(server: TSC.Server) -> None:
    single_user = TSC.UserItem("test", "Interactor")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.users.update(single_user)


def test_remove(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.users.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794", status_code=204)
        server.users.remove("dd2239f6-ddf1-4107-981a-4cf94e415794")


def test_remove_with_replacement(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(
            server.users.baseurl
            + "/dd2239f6-ddf1-4107-981a-4cf94e415794"
            + "?mapAssetsTo=4cc4c17f-898a-4de4-abed-a1681c673ced",
            status_code=204,
        )
        server.users.remove("dd2239f6-ddf1-4107-981a-4cf94e415794", "4cc4c17f-898a-4de4-abed-a1681c673ced")


def test_remove_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.users.remove("")


def test_add(server: TSC.Server) -> None:
    response_xml = ADD_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.users.baseurl + "", text=response_xml)
        new_user = TSC.UserItem(name="Cassie", site_role="Viewer", auth_setting="ServerDefault")
        new_user = server.users.add(new_user)

    assert "4cc4c17f-898a-4de4-abed-a1681c673ced" == new_user.id
    assert "Cassie" == new_user.name
    assert "Viewer" == new_user.site_role
    assert "ServerDefault" == new_user.auth_setting


def test_populate_workbooks(server: TSC.Server) -> None:
    response_xml = POPULATE_WORKBOOKS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.users.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794/workbooks", text=response_xml)
        single_user = TSC.UserItem("test", "Interactor")
        single_user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        server.users.populate_workbooks(single_user)

        workbook_list = list(single_user.workbooks)
        assert "3cc6cd06-89ce-4fdc-b935-5294135d6d42" == workbook_list[0].id
        assert "SafariSample" == workbook_list[0].name
        assert "SafariSample" == workbook_list[0].content_url
        assert False == workbook_list[0].show_tabs
        assert 26 == workbook_list[0].size
        assert "2016-07-26T20:34:56Z" == format_datetime(workbook_list[0].created_at)
        assert "2016-07-26T20:35:05Z" == format_datetime(workbook_list[0].updated_at)
        assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == workbook_list[0].project_id
        assert "default" == workbook_list[0].project_name
        assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == workbook_list[0].owner_id
        assert {"Safari", "Sample"} == workbook_list[0].tags


def test_populate_owned_workbooks(server: TSC.Server) -> None:
    response_xml = POPULATE_WORKBOOKS_XML.read_text()
    # Query parameter ownedBy is case sensitive.
    with requests_mock.mock(case_sensitive=True) as m:
        m.get(server.users.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794/workbooks?ownedBy=true", text=response_xml)
        single_user = TSC.UserItem("test", "Interactor")
        single_user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        server.users.populate_workbooks(single_user, owned_only=True)
        list(single_user.workbooks)

        request_history = m.request_history[0]

    assert "ownedBy" in request_history.qs, "ownedBy not in request history"
    assert "true" in request_history.qs["ownedBy"], "ownedBy not set to true in request history"


def test_populate_workbooks_missing_id(server: TSC.Server) -> None:
    single_user = TSC.UserItem("test", "Interactor")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.users.populate_workbooks(single_user)


def test_populate_favorites(server: TSC.Server) -> None:
    server.version = "2.5"
    baseurl = server.favorites.baseurl
    single_user = TSC.UserItem("test", "Interactor")
    response_xml = GET_FAVORITES_XML.read_text()
    with requests_mock.mock() as m:
        m.get(f"{baseurl}/{single_user.id}", text=response_xml)
        server.users.populate_favorites(single_user)
    assert single_user._favorites is not None
    assert len(single_user.favorites["workbooks"]) == 1
    assert len(single_user.favorites["views"]) == 1
    assert len(single_user.favorites["projects"]) == 1
    assert len(single_user.favorites["datasources"]) == 1

    workbook = single_user.favorites["workbooks"][0]
    view = single_user.favorites["views"][0]
    datasource = single_user.favorites["datasources"][0]
    project = single_user.favorites["projects"][0]

    assert workbook.id == "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00"
    assert view.id == "d79634e1-6063-4ec9-95ff-50acbf609ff5"
    assert datasource.id == "e76a1461-3b1d-4588-bf1b-17551a879ad9"
    assert project.id == "1d0304cd-3796-429f-b815-7258370b9b74"


def test_populate_groups(server: TSC.Server) -> None:
    server.version = "3.7"
    response_xml = POPULATE_GROUPS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.users.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794/groups", text=response_xml)
        single_user = TSC.UserItem("test", "Interactor")
        single_user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        server.users.populate_groups(single_user)

        group_list = list(single_user.groups)

        assert 3 == len(group_list)
        assert "ef8b19c0-43b6-11e6-af50-63f5805dbe3c" == group_list[0].id
        assert "All Users" == group_list[0].name
        assert "local" == group_list[0].domain_name

        assert "e7833b48-c6f7-47b5-a2a7-36e7dd232758" == group_list[1].id
        assert "Another group" == group_list[1].name
        assert "local" == group_list[1].domain_name

        assert "86a66d40-f289-472a-83d0-927b0f954dc8" == group_list[2].id
        assert "TableauExample" == group_list[2].name
        assert "local" == group_list[2].domain_name


def test_get_usernames_from_file(server: TSC.Server):
    response_xml = ADD_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.users.baseurl, text=response_xml)
        user_list, failures = server.users.create_from_file(str(USERNAMES))
    assert user_list[0].name == "Cassie", user_list
    assert failures == [], failures


def test_get_users_from_file(server: TSC.Server):
    response_xml = ADD_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.users.baseurl, text=response_xml)
        users, failures = server.users.create_from_file(str(USERS))
    assert users[0].name == "Cassie", users
    assert failures == []


def test_get_users_all_fields(server: TSC.Server) -> None:
    server.version = "3.7"
    baseurl = server.users.baseurl
    response_xml = GET_XML_ALL_FIELDS.read_text()

    with requests_mock.mock() as m:
        m.get(f"{baseurl}?fields=_all_", text=response_xml)
        all_users, _ = server.users.get()

    assert all_users[0].auth_setting == "TableauIDWithMFA"
    assert all_users[0].email == "bob@example.com"
    assert all_users[0].external_auth_user_id == "38c870c3ac5e84ec66e6ced9fb23681835b07e56d5660371ac1f705cc65bd610"
    assert all_users[0].fullname == "Bob Smith"
    assert all_users[0].id == "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
    assert all_users[0].last_login == parse_datetime("2025-02-04T06:39:20Z")
    assert all_users[0].name == "bob@example.com"
    assert all_users[0].site_role == "SiteAdministratorCreator"
    assert all_users[0].locale is None
    assert all_users[0].language == "en"
    assert all_users[0].idp_configuration_id == "22222222-2222-2222-2222-222222222222"
    assert all_users[0].domain_name == "TABID_WITH_MFA"
    assert all_users[1].auth_setting == "TableauIDWithMFA"
    assert all_users[1].email == "alice@example.com"
    assert all_users[1].external_auth_user_id == "96f66b893b22669cdfa632275d354cd1d92cea0266f3be7702151b9b8c52be29"
    assert all_users[1].fullname == "Alice Jones"
    assert all_users[1].id == "f6d72445-285b-48e5-8380-f90b519ce682"
    assert all_users[1].name == "alice@example.com"
    assert all_users[1].site_role == "ExplorerCanPublish"
    assert all_users[1].locale is None
    assert all_users[1].language == "en"
    assert all_users[1].idp_configuration_id == "22222222-2222-2222-2222-222222222222"
    assert all_users[1].domain_name == "TABID_WITH_MFA"


def test_add_user_idp_configuration(server: TSC.Server) -> None:
    response_xml = ADD_XML.read_text()
    user = TSC.UserItem(name="Cassie", site_role="Viewer")
    user.idp_configuration_id = "012345"

    with requests_mock.mock() as m:
        m.post(server.users.baseurl, text=response_xml)
        user = server.users.add(user)

        history = m.request_history[0]

    tree = ET.fromstring(history.text)
    user_elem = tree.find(".//user")
    assert user_elem is not None
    assert user_elem.attrib["idpConfigurationId"] == "012345"


def test_update_user_idp_configuration(server: TSC.Server) -> None:
    response_xml = ADD_XML.read_text()
    user = TSC.UserItem(name="Cassie", site_role="Viewer")
    user._id = "0123456789"
    user.idp_configuration_id = "012345"

    with requests_mock.mock() as m:
        m.put(f"{server.users.baseurl}/{user.id}", text=response_xml)
        user = server.users.update(user)

        history = m.request_history[0]

    tree = ET.fromstring(history.text)
    user_elem = tree.find(".//user")
    assert user_elem is not None
    assert user_elem.attrib["idpConfigurationId"] == "012345"
