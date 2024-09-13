import os
import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = os.path.join(TEST_ASSET_DIR, "user_get.xml")
GET_EMPTY_XML = os.path.join(TEST_ASSET_DIR, "user_get_empty.xml")
GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, "user_get_by_id.xml")
UPDATE_XML = os.path.join(TEST_ASSET_DIR, "user_update.xml")
ADD_XML = os.path.join(TEST_ASSET_DIR, "user_add.xml")
POPULATE_WORKBOOKS_XML = os.path.join(TEST_ASSET_DIR, "user_populate_workbooks.xml")
GET_FAVORITES_XML = os.path.join(TEST_ASSET_DIR, "favorites_get.xml")
POPULATE_GROUPS_XML = os.path.join(TEST_ASSET_DIR, "user_populate_groups.xml")

USERNAMES = os.path.join(TEST_ASSET_DIR, "Data", "usernames.csv")
USERS = os.path.join(TEST_ASSET_DIR, "Data", "user_details.csv")


class UserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.users.baseurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "?fields=_all_", text=response_xml)
            all_users, pagination_item = self.server.users.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual(2, len(all_users))

        self.assertTrue(any(user.id == "dd2239f6-ddf1-4107-981a-4cf94e415794" for user in all_users))
        single_user = next(user for user in all_users if user.id == "dd2239f6-ddf1-4107-981a-4cf94e415794")
        self.assertEqual("alice", single_user.name)
        self.assertEqual("Publisher", single_user.site_role)
        self.assertEqual("2016-08-16T23:17:06Z", format_datetime(single_user.last_login))
        self.assertEqual("alice cook", single_user.fullname)
        self.assertEqual("alicecook@test.com", single_user.email)

        self.assertTrue(any(user.id == "2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3" for user in all_users))
        single_user = next(user for user in all_users if user.id == "2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3")
        self.assertEqual("Bob", single_user.name)
        self.assertEqual("Interactor", single_user.site_role)
        self.assertEqual("Bob Smith", single_user.fullname)
        self.assertEqual("bob@test.com", single_user.email)

    def test_get_empty(self) -> None:
        with open(GET_EMPTY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_users, pagination_item = self.server.users.get()

        self.assertEqual(0, pagination_item.total_available)
        self.assertEqual([], all_users)

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.users.get)

    def test_get_by_id(self) -> None:
        with open(GET_BY_ID_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794", text=response_xml)
            single_user = self.server.users.get_by_id("dd2239f6-ddf1-4107-981a-4cf94e415794")

        self.assertEqual("dd2239f6-ddf1-4107-981a-4cf94e415794", single_user.id)
        self.assertEqual("alice", single_user.name)
        self.assertEqual("Alice", single_user.fullname)
        self.assertEqual("Publisher", single_user.site_role)
        self.assertEqual("ServerDefault", single_user.auth_setting)
        self.assertEqual("2016-08-16T23:17:06Z", format_datetime(single_user.last_login))
        self.assertEqual("local", single_user.domain_name)

    def test_get_by_id_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.users.get_by_id, "")

    def test_update(self) -> None:
        with open(UPDATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794", text=response_xml)
            single_user = TSC.UserItem("test", "Viewer")
            single_user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_user.name = "Cassie"
            single_user.fullname = "Cassie"
            single_user.email = "cassie@email.com"
            single_user = self.server.users.update(single_user)

        self.assertEqual("Cassie", single_user.name)
        self.assertEqual("Cassie", single_user.fullname)
        self.assertEqual("cassie@email.com", single_user.email)
        self.assertEqual("Viewer", single_user.site_role)

    def test_update_missing_id(self) -> None:
        single_user = TSC.UserItem("test", "Interactor")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.users.update, single_user)

    def test_remove(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794", status_code=204)
            self.server.users.remove("dd2239f6-ddf1-4107-981a-4cf94e415794")

    def test_remove_with_replacement(self) -> None:
        with requests_mock.mock() as m:
            m.delete(
                self.baseurl
                + "/dd2239f6-ddf1-4107-981a-4cf94e415794"
                + "?mapAssetsTo=4cc4c17f-898a-4de4-abed-a1681c673ced",
                status_code=204,
            )
            self.server.users.remove("dd2239f6-ddf1-4107-981a-4cf94e415794", "4cc4c17f-898a-4de4-abed-a1681c673ced")

    def test_remove_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.users.remove, "")

    def test_add(self) -> None:
        with open(ADD_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl + "", text=response_xml)
            new_user = TSC.UserItem(name="Cassie", site_role="Viewer", auth_setting="ServerDefault")
            new_user = self.server.users.add(new_user)

        self.assertEqual("4cc4c17f-898a-4de4-abed-a1681c673ced", new_user.id)
        self.assertEqual("Cassie", new_user.name)
        self.assertEqual("Viewer", new_user.site_role)
        self.assertEqual("ServerDefault", new_user.auth_setting)

    def test_populate_workbooks(self) -> None:
        with open(POPULATE_WORKBOOKS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794/workbooks", text=response_xml)
            single_user = TSC.UserItem("test", "Interactor")
            single_user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            self.server.users.populate_workbooks(single_user)

            workbook_list = list(single_user.workbooks)
            self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", workbook_list[0].id)
            self.assertEqual("SafariSample", workbook_list[0].name)
            self.assertEqual("SafariSample", workbook_list[0].content_url)
            self.assertEqual(False, workbook_list[0].show_tabs)
            self.assertEqual(26, workbook_list[0].size)
            self.assertEqual("2016-07-26T20:34:56Z", format_datetime(workbook_list[0].created_at))
            self.assertEqual("2016-07-26T20:35:05Z", format_datetime(workbook_list[0].updated_at))
            self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", workbook_list[0].project_id)
            self.assertEqual("default", workbook_list[0].project_name)
            self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", workbook_list[0].owner_id)
            self.assertEqual({"Safari", "Sample"}, workbook_list[0].tags)

    def test_populate_workbooks_missing_id(self) -> None:
        single_user = TSC.UserItem("test", "Interactor")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.users.populate_workbooks, single_user)

    def test_populate_favorites(self) -> None:
        self.server.version = "2.5"
        baseurl = self.server.favorites.baseurl
        single_user = TSC.UserItem("test", "Interactor")
        with open(GET_FAVORITES_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(f"{baseurl}/{single_user.id}", text=response_xml)
            self.server.users.populate_favorites(single_user)
        self.assertIsNotNone(single_user._favorites)
        self.assertEqual(len(single_user.favorites["workbooks"]), 1)
        self.assertEqual(len(single_user.favorites["views"]), 1)
        self.assertEqual(len(single_user.favorites["projects"]), 1)
        self.assertEqual(len(single_user.favorites["datasources"]), 1)

        workbook = single_user.favorites["workbooks"][0]
        view = single_user.favorites["views"][0]
        datasource = single_user.favorites["datasources"][0]
        project = single_user.favorites["projects"][0]

        self.assertEqual(workbook.id, "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00")
        self.assertEqual(view.id, "d79634e1-6063-4ec9-95ff-50acbf609ff5")
        self.assertEqual(datasource.id, "e76a1461-3b1d-4588-bf1b-17551a879ad9")
        self.assertEqual(project.id, "1d0304cd-3796-429f-b815-7258370b9b74")

    def test_populate_groups(self) -> None:
        self.server.version = "3.7"
        with open(POPULATE_GROUPS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.server.users.baseurl + "/dd2239f6-ddf1-4107-981a-4cf94e415794/groups", text=response_xml)
            single_user = TSC.UserItem("test", "Interactor")
            single_user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            self.server.users.populate_groups(single_user)

            group_list = list(single_user.groups)

            self.assertEqual(3, len(group_list))
            self.assertEqual("ef8b19c0-43b6-11e6-af50-63f5805dbe3c", group_list[0].id)
            self.assertEqual("All Users", group_list[0].name)
            self.assertEqual("local", group_list[0].domain_name)

            self.assertEqual("e7833b48-c6f7-47b5-a2a7-36e7dd232758", group_list[1].id)
            self.assertEqual("Another group", group_list[1].name)
            self.assertEqual("local", group_list[1].domain_name)

            self.assertEqual("86a66d40-f289-472a-83d0-927b0f954dc8", group_list[2].id)
            self.assertEqual("TableauExample", group_list[2].name)
            self.assertEqual("local", group_list[2].domain_name)

    def test_get_usernames_from_file(self):
        with open(ADD_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.server.users.baseurl, text=response_xml)
            user_list, failures = self.server.users.create_from_file(USERNAMES)
        assert user_list[0].name == "Cassie", user_list
        assert failures == [], failures

    def test_get_users_from_file(self):
        with open(ADD_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.server.users.baseurl, text=response_xml)
            users, failures = self.server.users.create_from_file(USERS)
        assert users[0].name == "Cassie", users
        assert failures == []
