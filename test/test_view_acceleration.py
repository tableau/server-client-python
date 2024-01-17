import os
import requests_mock
import unittest

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_BY_ID_ACCELERATION_STATUS_XML = os.path.join(TEST_ASSET_DIR, "workbook_get_by_id_acceleration_status.xml")
POPULATE_VIEWS_XML = os.path.join(TEST_ASSET_DIR, "workbook_populate_views.xml")
UPDATE_VIEWS_ACCELERATION_STATUS_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_views_acceleration_status.xml")
UPDATE_WORKBOOK_ACCELERATION_STATUS_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_acceleration_status.xml")


class WorkbookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.workbooks.baseurl

    def test_get_by_id(self) -> None:
        with open(GET_BY_ID_ACCELERATION_STATUS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42", text=response_xml)
            single_workbook = self.server.workbooks.get_by_id("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

        self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", single_workbook.id)
        self.assertEqual("SafariSample", single_workbook.name)
        self.assertEqual("SafariSample", single_workbook.content_url)
        self.assertEqual("http://tableauserver/#/workbooks/2/views", single_workbook.webpage_url)
        self.assertEqual(False, single_workbook.show_tabs)
        self.assertEqual(26, single_workbook.size)
        self.assertEqual("2016-07-26T20:34:56Z", format_datetime(single_workbook.created_at))
        self.assertEqual("description for SafariSample", single_workbook.description)
        self.assertEqual("2016-07-26T20:35:05Z", format_datetime(single_workbook.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", single_workbook.project_id)
        self.assertEqual("default", single_workbook.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", single_workbook.owner_id)
        self.assertEqual(set(["Safari", "Sample"]), single_workbook.tags)
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", single_workbook.views[0].id)
        self.assertEqual("ENDANGERED SAFARI", single_workbook.views[0].name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", single_workbook.views[0].content_url)
        self.assertEqual(True, single_workbook.views[0].data_acceleration_config["acceleration_enabled"])
        self.assertEqual("Enabled", single_workbook.views[0].data_acceleration_config["acceleration_status"])
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff9", single_workbook.views[1].id)
        self.assertEqual("ENDANGERED SAFARI 2", single_workbook.views[1].name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI2", single_workbook.views[1].content_url)
        self.assertEqual(False, single_workbook.views[1].data_acceleration_config["acceleration_enabled"])
        self.assertEqual("Suspended", single_workbook.views[1].data_acceleration_config["acceleration_status"])

    def test_update_workbook_acceleration(self) -> None:
        with open(UPDATE_WORKBOOK_ACCELERATION_STATUS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_acceleration_config = {
                "acceleration_enabled": True,
                "accelerate_now": False,
                "last_updated_at": None,
                "acceleration_status": None,
            }
            # update with parameter includeViewAccelerationStatus=True
            single_workbook = self.server.workbooks.update(single_workbook, True)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual("1d0304cd-3796-429f-b815-7258370b9b74", single_workbook.project_id)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", single_workbook.views[0].content_url)
        self.assertEqual(True, single_workbook.views[0].data_acceleration_config["acceleration_enabled"])
        self.assertEqual("Pending", single_workbook.views[0].data_acceleration_config["acceleration_status"])
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff9", single_workbook.views[1].id)
        self.assertEqual("ENDANGERED SAFARI 2", single_workbook.views[1].name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI2", single_workbook.views[1].content_url)
        self.assertEqual(True, single_workbook.views[1].data_acceleration_config["acceleration_enabled"])
        self.assertEqual("Pending", single_workbook.views[1].data_acceleration_config["acceleration_status"])

    def test_update_views_acceleration(self) -> None:
        with open(POPULATE_VIEWS_XML, "rb") as f:
            views_xml = f.read().decode("utf-8")
        with open(UPDATE_VIEWS_ACCELERATION_STATUS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/views", text=views_xml)
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_acceleration_config = {
                "acceleration_enabled": False,
                "accelerate_now": False,
                "last_updated_at": None,
                "acceleration_status": None,
            }
            self.server.workbooks.populate_views(single_workbook)
            single_workbook.views = [single_workbook.views[1], single_workbook.views[2]]
            # update with parameter includeViewAccelerationStatus=True
            single_workbook = self.server.workbooks.update(single_workbook, True)

        views_list = single_workbook.views
        self.assertEqual("097dbe13-de89-445f-b2c3-02f28bd010c1", views_list[0].id)
        self.assertEqual("GDP per capita", views_list[0].name)
        self.assertEqual(False, views_list[0].data_acceleration_config["acceleration_enabled"])
        self.assertEqual("Disabled", views_list[0].data_acceleration_config["acceleration_status"])

        self.assertEqual("2c1ab9d7-8d64-4cc6-b495-52e40c60c330", views_list[1].id)
        self.assertEqual("Country ranks", views_list[1].name)
        self.assertEqual(True, views_list[1].data_acceleration_config["acceleration_enabled"])
        self.assertEqual("Pending", views_list[1].data_acceleration_config["acceleration_status"])

        self.assertEqual("0599c28c-6d82-457e-a453-e52c1bdb00f5", views_list[2].id)
        self.assertEqual("Interest rates", views_list[2].name)
        self.assertEqual(True, views_list[2].data_acceleration_config["acceleration_enabled"])
        self.assertEqual("Pending", views_list[2].data_acceleration_config["acceleration_status"])
