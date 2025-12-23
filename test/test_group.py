from pathlib import Path
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

import pytest

TEST_ASSET_DIR = Path(__file__).absolute().parent / "assets"

GET_XML = TEST_ASSET_DIR / "group_get.xml"
GET_XML_ALL_FIELDS = TEST_ASSET_DIR / "group_get_all_fields.xml"
POPULATE_USERS = TEST_ASSET_DIR / "group_populate_users.xml"
POPULATE_USERS_EMPTY = TEST_ASSET_DIR / "group_populate_users_empty.xml"
ADD_USER = TEST_ASSET_DIR / "group_add_user.xml"
ADD_USERS = TEST_ASSET_DIR / "group_add_users.xml"
ADD_USER_POPULATE = TEST_ASSET_DIR / "group_users_added.xml"
CREATE_GROUP = TEST_ASSET_DIR / "group_create.xml"
CREATE_GROUP_AD = TEST_ASSET_DIR / "group_create_ad.xml"
CREATE_GROUP_ASYNC = TEST_ASSET_DIR / "group_create_async.xml"
UPDATE_XML = TEST_ASSET_DIR / "group_update.xml"
UPDATE_ASYNC_XML = TEST_ASSET_DIR / "group_update_async.xml"


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
        m.get(server.groups.baseurl, text=response_xml)
        all_groups, pagination_item = server.groups.get()

    assert 3 == pagination_item.total_available
    assert "ef8b19c0-43b6-11e6-af50-63f5805dbe3c" == all_groups[0].id
    assert "All Users" == all_groups[0].name
    assert "local" == all_groups[0].domain_name

    assert "e7833b48-c6f7-47b5-a2a7-36e7dd232758" == all_groups[1].id
    assert "Another group" == all_groups[1].name
    assert "local" == all_groups[1].domain_name

    assert "86a66d40-f289-472a-83d0-927b0f954dc8" == all_groups[2].id
    assert "TableauExample" == all_groups[2].name
    assert "local" == all_groups[2].domain_name


def test_get_before_signin(server: TSC.Server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.groups.get()


def test_populate_users(server: TSC.Server) -> None:
    response_xml = POPULATE_USERS.read_text()
    with requests_mock.mock() as m:
        m.get(
            server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users?pageNumber=1&pageSize=100",
            text=response_xml,
            complete_qs=True,
        )
        single_group = TSC.GroupItem(name="Test Group")
        single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
        server.groups.populate_users(single_group)

        assert 1 == len(list(single_group.users))
        user = list(single_group.users).pop()
        assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == user.id
        assert "alice" == user.name
        assert "Publisher" == user.site_role
        assert "2016-08-16T23:17:06Z" == format_datetime(user.last_login)


def test_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758", status_code=204)
        server.groups.delete("e7833b48-c6f7-47b5-a2a7-36e7dd232758")


def test_remove_user(server: TSC.Server) -> None:
    response_xml_populate = POPULATE_USERS.read_text()

    response_xml_empty = POPULATE_USERS_EMPTY.read_text()

    with requests_mock.mock() as m:
        url = (
            server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users"
            "/dd2239f6-ddf1-4107-981a-4cf94e415794"
        )

        m.delete(url, status_code=204)
        #  We register the get endpoint twice. The first time we have 1 user, the second we have 'removed' them.
        m.get(server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_populate)

        single_group = TSC.GroupItem("test")
        single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
        server.groups.populate_users(single_group)
        assert 1 == len(list(single_group.users))
        server.groups.remove_user(single_group, "dd2239f6-ddf1-4107-981a-4cf94e415794")

        m.get(server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_empty)
        assert 0 == len(list(single_group.users))


def test_add_user(server: TSC.Server) -> None:
    response_xml_add = ADD_USER.read_text()
    response_xml_populate = ADD_USER_POPULATE.read_text()
    with requests_mock.mock() as m:
        m.post(server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_add)
        m.get(server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_populate)
        single_group = TSC.GroupItem("test")
        single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"

        server.groups.add_user(single_group, "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7")
        server.groups.populate_users(single_group)
        assert 1 == len(list(single_group.users))
        user = list(single_group.users).pop()
        assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == user.id
        assert "testuser" == user.name
        assert "ServerAdministrator" == user.site_role


def test_add_users(server: TSC.Server) -> None:
    server.version = "3.21"

    def make_user(id: str, name: str, siteRole: str) -> TSC.UserItem:
        user = TSC.UserItem(name, siteRole)
        user._id = id
        return user

    users = [
        make_user(id="5de011f8-4aa9-4d5b-b991-f464c8dd6bb7", name="Alice", siteRole="ServerAdministrator"),
        make_user(id="5de011f8-3aa9-4d5b-b991-f467c8dd6bb8", name="Bob", siteRole="Explorer"),
        make_user(id="5de011f8-2aa9-4d5b-b991-f466c8dd6bb8", name="Charlie", siteRole="Viewer"),
    ]
    group = TSC.GroupItem("test")
    group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"

    with requests_mock.mock() as m:
        m.post(f"{server.groups.baseurl}/{group.id}/users", text=ADD_USERS.read_text())
        resp_users = server.groups.add_users(group, users)

    for user, resp_user in zip(users, resp_users):
        assert user.id == resp_user.id
        assert user.name == resp_user.name
        assert user.site_role == resp_user.site_role


def test_remove_users(server: TSC.Server) -> None:
    server.version = "3.21"

    def make_user(id: str, name: str, siteRole: str) -> TSC.UserItem:
        user = TSC.UserItem(name, siteRole)
        user._id = id
        return user

    users = [
        make_user(id="5de011f8-4aa9-4d5b-b991-f464c8dd6bb7", name="Alice", siteRole="ServerAdministrator"),
        make_user(id="5de011f8-3aa9-4d5b-b991-f467c8dd6bb8", name="Bob", siteRole="Explorer"),
        make_user(id="5de011f8-2aa9-4d5b-b991-f466c8dd6bb8", name="Charlie", siteRole="Viewer"),
    ]
    group = TSC.GroupItem("test")
    group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"

    with requests_mock.mock() as m:
        m.put(f"{server.groups.baseurl}/{group.id}/users/remove")
        server.groups.remove_users(group, users)


def test_add_user_before_populating(server: TSC.Server) -> None:
    get_xml_response = GET_XML.read_text()
    add_user_response = ADD_USER.read_text()
    with requests_mock.mock() as m:
        m.get(server.groups.baseurl, text=get_xml_response)
        m.post(
            server.groups.baseurl + "/ef8b19c0-43b6-11e6-af50-63f5805dbe3c/users",
            text=add_user_response,
        )
        all_groups, pagination_item = server.groups.get()
        single_group = all_groups[0]
        server.groups.add_user(single_group, "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7")


def test_add_user_missing_user_id(server: TSC.Server) -> None:
    response_xml = POPULATE_USERS.read_text()
    with requests_mock.mock() as m:
        m.get(server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml)
        single_group = TSC.GroupItem(name="Test Group")
        single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
        server.groups.populate_users(single_group)

    with pytest.raises(ValueError):
        server.groups.add_user(single_group, "")


def test_add_user_missing_group_id(server: TSC.Server) -> None:
    single_group = TSC.GroupItem("test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.groups.add_user(
            single_group,
            "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7",
        )


def test_remove_user_before_populating(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.groups.baseurl, text=response_xml)
        m.delete(
            server.groups.baseurl + "/ef8b19c0-43b6-11e6-af50-63f5805dbe3c/users/5de011f8-5aa9-4d5b-b991-f462c8dd6bb7",
            text="ok",
        )
        all_groups, pagination_item = server.groups.get()
        single_group = all_groups[0]
        server.groups.remove_user(single_group, "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7")


def test_remove_user_missing_user_id(server: TSC.Server) -> None:
    response_xml = POPULATE_USERS.read_text()
    with requests_mock.mock() as m:
        m.get(server.groups.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml)
        single_group = TSC.GroupItem(name="Test Group")
        single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
        server.groups.populate_users(single_group)

    with pytest.raises(ValueError):
        server.groups.remove_user(single_group, "")


def test_remove_user_missing_group_id(server: TSC.Server) -> None:
    single_group = TSC.GroupItem("test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.groups.remove_user(
            single_group,
            "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7",
        )


def test_create_group(server: TSC.Server) -> None:
    response_xml = CREATE_GROUP.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.groups.baseurl, text=response_xml)
        group_to_create = TSC.GroupItem("試供品")
        group = server.groups.create(group_to_create)
        assert group.name == "試供品"
        assert group.id == "3e4a9ea0-a07a-4fe6-b50f-c345c8c81034"


def test_create_ad_group(server: TSC.Server) -> None:
    response_xml = CREATE_GROUP_AD.read_bytes().decode("utf8")
    with requests_mock.mock() as m:
        m.post(server.groups.baseurl, text=response_xml)
        group_to_create = TSC.GroupItem("試供品")
        group_to_create.domain_name = "just-has-to-exist"
        group = server.groups.create_AD_group(group_to_create, False)
        assert group.name == "試供品"
        assert group.license_mode == "onLogin"
        assert group.minimum_site_role == "Creator"
        assert group.domain_name == "active-directory-domain-name"


def test_create_group_async(server: TSC.Server) -> None:
    response_xml = CREATE_GROUP_ASYNC.read_text()
    with requests_mock.mock() as m:
        m.post(server.groups.baseurl, text=response_xml)
        group_to_create = TSC.GroupItem("試供品")
        group_to_create.domain_name = "woohoo"
        job = server.groups.create_AD_group(group_to_create, True)
        assert job.mode == "Asynchronous"
        assert job.type == "GroupImport"


def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.groups.baseurl + "/ef8b19c0-43b6-11e6-af50-63f5805dbe3c", text=response_xml)
        group = TSC.GroupItem(name="Test Group")
        group._domain_name = "local"
        group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"
        group = server.groups.update(group)

    assert "ef8b19c0-43b6-11e6-af50-63f5805dbe3c" == group.id
    assert "Group updated name" == group.name
    assert "ExplorerCanPublish" == group.minimum_site_role
    assert "onLogin" == group.license_mode


# async update is not supported for local groups
def test_update_local_async(server: TSC.Server) -> None:
    group = TSC.GroupItem("myGroup")
    group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"
    with pytest.raises(ValueError):
        server.groups.update(group, as_job=True)

    # mimic group returned from server where domain name is set to 'local'
    group.domain_name = "local"
    with pytest.raises(ValueError):
        server.groups.update(group, as_job=True)


def test_update_ad_async(server: TSC.Server) -> None:
    group = TSC.GroupItem("myGroup", "example.com")
    group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"
    group.minimum_site_role = TSC.UserItem.Roles.Viewer

    with requests_mock.mock() as m:
        m.put(f"{server.groups.baseurl}/{group.id}?asJob=True", text=UPDATE_ASYNC_XML.read_bytes().decode("utf8"))
        job = server.groups.update(group, as_job=True)

    assert job.id == "c2566efc-0767-4f15-89cb-56acb4349c1b"
    assert job.mode == "Asynchronous"
    assert job.type == "GroupSync"


def test_get_all_fields(server: TSC.Server) -> None:
    ro = TSC.RequestOptions()
    ro.all_fields = True
    server.version = "3.21"
    with requests_mock.mock() as m:
        m.get(f"{server.groups.baseurl}?fields=_all_", text=GET_XML_ALL_FIELDS.read_text())
        groups, pages = server.groups.get(req_options=ro)

    assert pages.total_available == 3
    assert len(groups) == 3
    assert groups[0].id == "28c5b855-16df-482f-ad0b-428c1df58859"
    assert groups[0].name == "All Users"
    assert groups[0].user_count == 2
    assert groups[0].domain_name == "local"
    assert groups[1].id == "ace1ee2d-e7dd-4d7a-9504-a1ccaa5212ea"
    assert groups[1].name == "group1"
    assert groups[1].user_count == 1
    assert groups[2].id == "baf0ed9d-c25d-4114-97ed-5232b8a732fd"
    assert groups[2].name == "test"
    assert groups[2].user_count == 0
