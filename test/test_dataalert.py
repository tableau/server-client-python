import unittest

import requests_mock

import tableauserverclient as TSC
from ._utils import read_xml_asset

GET_XML = "data_alerts_get.xml"
GET_BY_ID_XML = "data_alerts_get_by_id.xml"
ADD_USER_TO_ALERT = "data_alerts_add_user.xml"
UPDATE_XML = "data_alerts_update.xml"


class DataAlertTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.server.version = "3.2"

        self.baseurl = self.server.data_alerts.baseurl

    def test_get(self) -> None:
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_alerts, pagination_item = self.server.data_alerts.get()

        self.assertEqual(1, pagination_item.total_available)
        self.assertEqual("5ea59b45-e497-5673-8809-bfe213236f75", all_alerts[0].id)
        self.assertEqual("Data Alert test", all_alerts[0].subject)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_alerts[0].creatorId)
        self.assertEqual("2020-08-10T23:17:06Z", all_alerts[0].createdAt)
        self.assertEqual("2020-08-10T23:17:06Z", all_alerts[0].updatedAt)
        self.assertEqual("Daily", all_alerts[0].frequency)
        self.assertEqual("true", all_alerts[0].public)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_alerts[0].owner_id)
        self.assertEqual("Bob", all_alerts[0].owner_name)
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", all_alerts[0].view_id)
        self.assertEqual("ENDANGERED SAFARI", all_alerts[0].view_name)
        self.assertEqual("6d13b0ca-043d-4d42-8c9d-3f3313ea3a00", all_alerts[0].workbook_id)
        self.assertEqual("Safari stats", all_alerts[0].workbook_name)
        self.assertEqual("5241e88d-d384-4fd7-9c2f-648b5247efc5", all_alerts[0].project_id)
        self.assertEqual("Default", all_alerts[0].project_name)

    def test_get_by_id(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/5ea59b45-e497-5673-8809-bfe213236f75", text=response_xml)
            alert = self.server.data_alerts.get_by_id("5ea59b45-e497-5673-8809-bfe213236f75")

        self.assertTrue(isinstance(alert.recipients, list))
        self.assertEqual(len(alert.recipients), 1)
        self.assertEqual(alert.recipients[0], "dd2239f6-ddf1-4107-981a-4cf94e415794")

    def test_update(self) -> None:
        response_xml = read_xml_asset(UPDATE_XML)
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/5ea59b45-e497-5673-8809-bfe213236f75", text=response_xml)
            single_alert = TSC.DataAlertItem()
            single_alert._id = "5ea59b45-e497-5673-8809-bfe213236f75"
            single_alert._subject = "Data Alert test"
            single_alert._frequency = "Daily"
            single_alert._public = True
            single_alert._owner_id = "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"
            single_alert = self.server.data_alerts.update(single_alert)

        self.assertEqual("5ea59b45-e497-5673-8809-bfe213236f75", single_alert.id)
        self.assertEqual("Data Alert test", single_alert.subject)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", single_alert.creatorId)
        self.assertEqual("2020-08-10T23:17:06Z", single_alert.createdAt)
        self.assertEqual("2020-08-10T23:17:06Z", single_alert.updatedAt)
        self.assertEqual("Daily", single_alert.frequency)
        self.assertEqual("true", single_alert.public)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", single_alert.owner_id)
        self.assertEqual("Bob", single_alert.owner_name)
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", single_alert.view_id)
        self.assertEqual("ENDANGERED SAFARI", single_alert.view_name)
        self.assertEqual("6d13b0ca-043d-4d42-8c9d-3f3313ea3a00", single_alert.workbook_id)
        self.assertEqual("Safari stats", single_alert.workbook_name)
        self.assertEqual("5241e88d-d384-4fd7-9c2f-648b5247efc5", single_alert.project_id)
        self.assertEqual("Default", single_alert.project_name)

    def test_add_user_to_alert(self) -> None:
        response_xml = read_xml_asset(ADD_USER_TO_ALERT)
        single_alert = TSC.DataAlertItem()
        single_alert._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"
        in_user = TSC.UserItem("Bob", TSC.UserItem.Roles.Explorer)
        in_user._id = "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"

        with requests_mock.mock() as m:
            m.post(self.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/users", text=response_xml)

            out_user = self.server.data_alerts.add_user_to_alert(single_alert, in_user)

            self.assertEqual(out_user.id, in_user.id)
            self.assertEqual(out_user.name, in_user.name)
            self.assertEqual(out_user.site_role, in_user.site_role)

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5", status_code=204)
            self.server.data_alerts.delete("0448d2ed-590d-4fa0-b272-a2a8a24555b5")

    def test_delete_user_from_alert(self) -> None:
        alert_id = "5ea59b45-e497-5673-8809-bfe213236f75"
        user_id = "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"
        with requests_mock.mock() as m:
            m.delete(self.baseurl + f"/{alert_id}/users/{user_id}", status_code=204)
            self.server.data_alerts.delete_user_from_alert(alert_id, user_id)
