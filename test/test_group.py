from pathlib import Path
import unittest
import os
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = Path(__file__).absolute().parent / "assets"

# TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = os.path.join(TEST_ASSET_DIR, "group_get.xml")
POPULATE_USERS = os.path.join(TEST_ASSET_DIR, "group_populate_users.xml")
POPULATE_USERS_EMPTY = os.path.join(TEST_ASSET_DIR, "group_populate_users_empty.xml")
ADD_USER = os.path.join(TEST_ASSET_DIR, "group_add_user.xml")
ADD_USERS = TEST_ASSET_DIR / "group_add_users.xml"
ADD_USER_POPULATE = os.path.join(TEST_ASSET_DIR, "group_users_added.xml")
CREATE_GROUP = os.path.join(TEST_ASSET_DIR, "group_create.xml")
CREATE_GROUP_AD = os.path.join(TEST_ASSET_DIR, "group_create_ad.xml")
CREATE_GROUP_ASYNC = os.path.join(TEST_ASSET_DIR, "group_create_async.xml")
UPDATE_XML = os.path.join(TEST_ASSET_DIR, "group_update.xml")
UPDATE_ASYNC_XML = TEST_ASSET_DIR / "group_update_async.xml"


class GroupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.groups.baseurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_groups, pagination_item = self.server.groups.get()

        self.assertEqual(3, pagination_item.total_available)
        self.assertEqual("ef8b19c0-43b6-11e6-af50-63f5805dbe3c", all_groups[0].id)
        self.assertEqual("All Users", all_groups[0].name)
        self.assertEqual("local", all_groups[0].domain_name)

        self.assertEqual("e7833b48-c6f7-47b5-a2a7-36e7dd232758", all_groups[1].id)
        self.assertEqual("Another group", all_groups[1].name)
        self.assertEqual("local", all_groups[1].domain_name)

        self.assertEqual("86a66d40-f289-472a-83d0-927b0f954dc8", all_groups[2].id)
        self.assertEqual("TableauExample", all_groups[2].name)
        self.assertEqual("local", all_groups[2].domain_name)

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.groups.get)

    def test_populate_users(self) -> None:
        with open(POPULATE_USERS, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users?pageNumber=1&pageSize=100",
                text=response_xml,
                complete_qs=True,
            )
            single_group = TSC.GroupItem(name="Test Group")
            single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
            self.server.groups.populate_users(single_group)

            self.assertEqual(1, len(list(single_group.users)))
            user = list(single_group.users).pop()
            self.assertEqual("dd2239f6-ddf1-4107-981a-4cf94e415794", user.id)
            self.assertEqual("alice", user.name)
            self.assertEqual("Publisher", user.site_role)
            self.assertEqual("2016-08-16T23:17:06Z", format_datetime(user.last_login))

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758", status_code=204)
            self.server.groups.delete("e7833b48-c6f7-47b5-a2a7-36e7dd232758")

    def test_remove_user(self) -> None:
        with open(POPULATE_USERS, "rb") as f:
            response_xml_populate = f.read().decode("utf-8")

        with open(POPULATE_USERS_EMPTY, "rb") as f:
            response_xml_empty = f.read().decode("utf-8")

        with requests_mock.mock() as m:
            url = self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users" "/dd2239f6-ddf1-4107-981a-4cf94e415794"

            m.delete(url, status_code=204)
            #  We register the get endpoint twice. The first time we have 1 user, the second we have 'removed' them.
            m.get(self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_populate)

            single_group = TSC.GroupItem("test")
            single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
            self.server.groups.populate_users(single_group)
            self.assertEqual(1, len(list(single_group.users)))
            self.server.groups.remove_user(single_group, "dd2239f6-ddf1-4107-981a-4cf94e415794")

            m.get(self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_empty)
            self.assertEqual(0, len(list(single_group.users)))

    def test_add_user(self) -> None:
        with open(ADD_USER, "rb") as f:
            response_xml_add = f.read().decode("utf-8")
        with open(ADD_USER_POPULATE, "rb") as f:
            response_xml_populate = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_add)
            m.get(self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml_populate)
            single_group = TSC.GroupItem("test")
            single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"

            self.server.groups.add_user(single_group, "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7")
            self.server.groups.populate_users(single_group)
            self.assertEqual(1, len(list(single_group.users)))
            user = list(single_group.users).pop()
            self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", user.id)
            self.assertEqual("testuser", user.name)
            self.assertEqual("ServerAdministrator", user.site_role)

    def test_add_users(self) -> None:
        self.server.version = "3.21"
        self.baseurl = self.server.groups.baseurl

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
            m.post(f"{self.baseurl}/{group.id}/users", text=ADD_USERS.read_text())
            resp_users = self.server.groups.add_users(group, users)

        for user, resp_user in zip(users, resp_users):
            with self.subTest(user=user, resp_user=resp_user):
                assert user.id == resp_user.id
                assert user.name == resp_user.name
                assert user.site_role == resp_user.site_role

    def test_remove_users(self) -> None:
        self.server.version = "3.21"
        self.baseurl = self.server.groups.baseurl

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
            m.put(f"{self.baseurl}/{group.id}/users/remove")
            self.server.groups.remove_users(group, users)

    def test_add_user_before_populating(self) -> None:
        with open(GET_XML, "rb") as f:
            get_xml_response = f.read().decode("utf-8")
        with open(ADD_USER, "rb") as f:
            add_user_response = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=get_xml_response)
            m.post(
                self.baseurl + "/ef8b19c0-43b6-11e6-af50-63f5805dbe3c/users",
                text=add_user_response,
            )
            all_groups, pagination_item = self.server.groups.get()
            single_group = all_groups[0]
            self.server.groups.add_user(single_group, "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7")

    def test_add_user_missing_user_id(self) -> None:
        with open(POPULATE_USERS, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml)
            single_group = TSC.GroupItem(name="Test Group")
            single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
            self.server.groups.populate_users(single_group)

        self.assertRaises(ValueError, self.server.groups.add_user, single_group, "")

    def test_add_user_missing_group_id(self) -> None:
        single_group = TSC.GroupItem("test")
        self.assertRaises(
            TSC.MissingRequiredFieldError,
            self.server.groups.add_user,
            single_group,
            "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7",
        )

    def test_remove_user_before_populating(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            m.delete(
                self.baseurl + "/ef8b19c0-43b6-11e6-af50-63f5805dbe3c/users/5de011f8-5aa9-4d5b-b991-f462c8dd6bb7",
                text="ok",
            )
            all_groups, pagination_item = self.server.groups.get()
            single_group = all_groups[0]
            self.server.groups.remove_user(single_group, "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7")

    def test_remove_user_missing_user_id(self) -> None:
        with open(POPULATE_USERS, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users", text=response_xml)
            single_group = TSC.GroupItem(name="Test Group")
            single_group._id = "e7833b48-c6f7-47b5-a2a7-36e7dd232758"
            self.server.groups.populate_users(single_group)

        self.assertRaises(ValueError, self.server.groups.remove_user, single_group, "")

    def test_remove_user_missing_group_id(self) -> None:
        single_group = TSC.GroupItem("test")
        self.assertRaises(
            TSC.MissingRequiredFieldError,
            self.server.groups.remove_user,
            single_group,
            "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7",
        )

    def test_create_group(self) -> None:
        with open(CREATE_GROUP, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            group_to_create = TSC.GroupItem("試供品")
            group = self.server.groups.create(group_to_create)
            self.assertEqual(group.name, "試供品")
            self.assertEqual(group.id, "3e4a9ea0-a07a-4fe6-b50f-c345c8c81034")

    def test_create_ad_group(self) -> None:
        with open(CREATE_GROUP_AD, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            group_to_create = TSC.GroupItem("試供品")
            group_to_create.domain_name = "just-has-to-exist"
            group = self.server.groups.create_AD_group(group_to_create, False)
            self.assertEqual(group.name, "試供品")
            self.assertEqual(group.license_mode, "onLogin")
            self.assertEqual(group.minimum_site_role, "Creator")
            self.assertEqual(group.domain_name, "active-directory-domain-name")

    def test_create_group_async(self) -> None:
        with open(CREATE_GROUP_ASYNC, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            group_to_create = TSC.GroupItem("試供品")
            group_to_create.domain_name = "woohoo"
            job = self.server.groups.create_AD_group(group_to_create, True)
            self.assertEqual(job.mode, "Asynchronous")
            self.assertEqual(job.type, "GroupImport")

    def test_update(self) -> None:
        with open(UPDATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/ef8b19c0-43b6-11e6-af50-63f5805dbe3c", text=response_xml)
            group = TSC.GroupItem(name="Test Group")
            group._domain_name = "local"
            group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"
            group = self.server.groups.update(group)

        self.assertEqual("ef8b19c0-43b6-11e6-af50-63f5805dbe3c", group.id)
        self.assertEqual("Group updated name", group.name)
        self.assertEqual("ExplorerCanPublish", group.minimum_site_role)
        self.assertEqual("onLogin", group.license_mode)

    # async update is not supported for local groups
    def test_update_local_async(self) -> None:
        group = TSC.GroupItem("myGroup")
        group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"
        self.assertRaises(ValueError, self.server.groups.update, group, as_job=True)

        # mimic group returned from server where domain name is set to 'local'
        group.domain_name = "local"
        self.assertRaises(ValueError, self.server.groups.update, group, as_job=True)

    def test_update_ad_async(self) -> None:
        group = TSC.GroupItem("myGroup", "example.com")
        group._id = "ef8b19c0-43b6-11e6-af50-63f5805dbe3c"
        group.minimum_site_role = TSC.UserItem.Roles.Viewer

        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{group.id}?asJob=True", text=UPDATE_ASYNC_XML.read_bytes().decode("utf8"))
            job = self.server.groups.update(group, as_job=True)

        self.assertEqual(job.id, "c2566efc-0767-4f15-89cb-56acb4349c1b")
        self.assertEqual(job.mode, "Asynchronous")
        self.assertEqual(job.type, "GroupSync")
