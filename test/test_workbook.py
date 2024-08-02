import os
import re
import requests_mock
import tempfile
import unittest
from defusedxml.ElementTree import fromstring
from io import BytesIO
from pathlib import Path

import pytest

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.models import UserItem, GroupItem, PermissionsRule
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import asset

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

ADD_TAGS_XML = os.path.join(TEST_ASSET_DIR, "workbook_add_tags.xml")
GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, "workbook_get_by_id.xml")
GET_BY_ID_XML_PERSONAL = os.path.join(TEST_ASSET_DIR, "workbook_get_by_id_personal.xml")
GET_EMPTY_XML = os.path.join(TEST_ASSET_DIR, "workbook_get_empty.xml")
GET_INVALID_DATE_XML = os.path.join(TEST_ASSET_DIR, "workbook_get_invalid_date.xml")
GET_XML = os.path.join(TEST_ASSET_DIR, "workbook_get.xml")
ODATA_XML = os.path.join(TEST_ASSET_DIR, "odata_connection.xml")
POPULATE_CONNECTIONS_XML = os.path.join(TEST_ASSET_DIR, "workbook_populate_connections.xml")
POPULATE_PDF = os.path.join(TEST_ASSET_DIR, "populate_pdf.pdf")
POPULATE_POWERPOINT = os.path.join(TEST_ASSET_DIR, "populate_powerpoint.pptx")
POPULATE_PERMISSIONS_XML = os.path.join(TEST_ASSET_DIR, "workbook_populate_permissions.xml")
POPULATE_PREVIEW_IMAGE = os.path.join(TEST_ASSET_DIR, "RESTAPISample Image.png")
POPULATE_VIEWS_XML = os.path.join(TEST_ASSET_DIR, "workbook_populate_views.xml")
POPULATE_VIEWS_USAGE_XML = os.path.join(TEST_ASSET_DIR, "workbook_populate_views_usage.xml")
PUBLISH_XML = os.path.join(TEST_ASSET_DIR, "workbook_publish.xml")
PUBLISH_ASYNC_XML = os.path.join(TEST_ASSET_DIR, "workbook_publish_async.xml")
REFRESH_XML = os.path.join(TEST_ASSET_DIR, "workbook_refresh.xml")
REVISION_XML = os.path.join(TEST_ASSET_DIR, "workbook_revision.xml")
UPDATE_XML = os.path.join(TEST_ASSET_DIR, "workbook_update.xml")
UPDATE_PERMISSIONS = os.path.join(TEST_ASSET_DIR, "workbook_update_permissions.xml")


class WorkbookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.workbooks.baseurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_workbooks, pagination_item = self.server.workbooks.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("6d13b0ca-043d-4d42-8c9d-3f3313ea3a00", all_workbooks[0].id)
        self.assertEqual("Superstore", all_workbooks[0].name)
        self.assertEqual("Superstore", all_workbooks[0].content_url)
        self.assertEqual(False, all_workbooks[0].show_tabs)
        self.assertEqual("http://tableauserver/#/workbooks/1/views", all_workbooks[0].webpage_url)
        self.assertEqual(1, all_workbooks[0].size)
        self.assertEqual("2016-08-03T20:34:04Z", format_datetime(all_workbooks[0].created_at))
        self.assertEqual("description for Superstore", all_workbooks[0].description)
        self.assertEqual("2016-08-04T17:56:41Z", format_datetime(all_workbooks[0].updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", all_workbooks[0].project_id)
        self.assertEqual("default", all_workbooks[0].project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_workbooks[0].owner_id)

        self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", all_workbooks[1].id)
        self.assertEqual("SafariSample", all_workbooks[1].name)
        self.assertEqual("SafariSample", all_workbooks[1].content_url)
        self.assertEqual("http://tableauserver/#/workbooks/2/views", all_workbooks[1].webpage_url)
        self.assertEqual(False, all_workbooks[1].show_tabs)
        self.assertEqual(26, all_workbooks[1].size)
        self.assertEqual("2016-07-26T20:34:56Z", format_datetime(all_workbooks[1].created_at))
        self.assertEqual("description for SafariSample", all_workbooks[1].description)
        self.assertEqual("2016-07-26T20:35:05Z", format_datetime(all_workbooks[1].updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", all_workbooks[1].project_id)
        self.assertEqual("default", all_workbooks[1].project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_workbooks[1].owner_id)
        self.assertEqual(set(["Safari", "Sample"]), all_workbooks[1].tags)

    def test_get_ignore_invalid_date(self) -> None:
        with open(GET_INVALID_DATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_workbooks, pagination_item = self.server.workbooks.get()
        self.assertEqual(None, format_datetime(all_workbooks[0].created_at))
        self.assertEqual("2016-08-04T17:56:41Z", format_datetime(all_workbooks[0].updated_at))

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.workbooks.get)

    def test_get_empty(self) -> None:
        with open(GET_EMPTY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_workbooks, pagination_item = self.server.workbooks.get()

        self.assertEqual(0, pagination_item.total_available)
        self.assertEqual([], all_workbooks)

    def test_get_by_id(self) -> None:
        with open(GET_BY_ID_XML, "rb") as f:
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

    def test_get_by_id_personal(self) -> None:
        # workbooks in personal space don't have project_id or project_name
        with open(GET_BY_ID_XML_PERSONAL, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d43", text=response_xml)
            single_workbook = self.server.workbooks.get_by_id("3cc6cd06-89ce-4fdc-b935-5294135d6d43")

        self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d43", single_workbook.id)
        self.assertEqual("SafariSample", single_workbook.name)
        self.assertEqual("SafariSample", single_workbook.content_url)
        self.assertEqual("http://tableauserver/#/workbooks/2/views", single_workbook.webpage_url)
        self.assertEqual(False, single_workbook.show_tabs)
        self.assertEqual(26, single_workbook.size)
        self.assertEqual("2016-07-26T20:34:56Z", format_datetime(single_workbook.created_at))
        self.assertEqual("description for SafariSample", single_workbook.description)
        self.assertEqual("2016-07-26T20:35:05Z", format_datetime(single_workbook.updated_at))
        self.assertTrue(single_workbook.project_id)
        self.assertIsNone(single_workbook.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", single_workbook.owner_id)
        self.assertEqual(set(["Safari", "Sample"]), single_workbook.tags)
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", single_workbook.views[0].id)
        self.assertEqual("ENDANGERED SAFARI", single_workbook.views[0].name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", single_workbook.views[0].content_url)

    def test_get_by_id_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.workbooks.get_by_id, "")

    def test_refresh_id(self) -> None:
        self.server.version = "2.8"
        self.baseurl = self.server.workbooks.baseurl
        with open(REFRESH_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/refresh", status_code=202, text=response_xml)
            self.server.workbooks.refresh("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    def test_refresh_object(self) -> None:
        self.server.version = "2.8"
        self.baseurl = self.server.workbooks.baseurl
        workbook = TSC.WorkbookItem("")
        workbook._id = "3cc6cd06-89ce-4fdc-b935-5294135d6d42"
        with open(REFRESH_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/refresh", status_code=202, text=response_xml)
            self.server.workbooks.refresh(workbook)

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42", status_code=204)
            self.server.workbooks.delete("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    def test_delete_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.workbooks.delete, "")

    def test_update(self) -> None:
        with open(UPDATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_workbook.name = "renamedWorkbook"
            single_workbook.data_acceleration_config = {
                "acceleration_enabled": True,
                "accelerate_now": False,
                "last_updated_at": None,
                "acceleration_status": None,
            }
            single_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual(True, single_workbook.show_tabs)
        self.assertEqual("1d0304cd-3796-429f-b815-7258370b9b74", single_workbook.project_id)
        self.assertEqual("dd2239f6-ddf1-4107-981a-4cf94e415794", single_workbook.owner_id)
        self.assertEqual("renamedWorkbook", single_workbook.name)
        self.assertEqual(True, single_workbook.data_acceleration_config["acceleration_enabled"])
        self.assertEqual(False, single_workbook.data_acceleration_config["accelerate_now"])

    def test_update_missing_id(self) -> None:
        single_workbook = TSC.WorkbookItem("test")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.workbooks.update, single_workbook)

    def test_update_copy_fields(self) -> None:
        with open(POPULATE_CONNECTIONS_XML, "rb") as f:
            connection_xml = f.read().decode("utf-8")
        with open(UPDATE_XML, "rb") as f:
            update_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/connections", text=connection_xml)
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=update_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            self.server.workbooks.populate_connections(single_workbook)
            updated_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual(single_workbook._connections, updated_workbook._connections)
        self.assertEqual(single_workbook._views, updated_workbook._views)
        self.assertEqual(single_workbook.tags, updated_workbook.tags)
        self.assertEqual(single_workbook._initial_tags, updated_workbook._initial_tags)
        self.assertEqual(single_workbook._preview_image, updated_workbook._preview_image)

    def test_update_tags(self) -> None:
        with open(ADD_TAGS_XML, "rb") as f:
            add_tags_xml = f.read().decode("utf-8")
        with open(UPDATE_XML, "rb") as f:
            update_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/tags", text=add_tags_xml)
            m.delete(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/tags/b", status_code=204)
            m.delete(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/tags/d", status_code=204)
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=update_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook._initial_tags.update(["a", "b", "c", "d"])
            single_workbook.tags.update(["a", "c", "e"])
            updated_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual(single_workbook.tags, updated_workbook.tags)
        self.assertEqual(single_workbook._initial_tags, updated_workbook._initial_tags)

    def test_download(self) -> None:
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
                headers={"Content-Disposition": 'name="tableau_workbook"; filename="RESTAPISample.twbx"'},
            )
            file_path = self.server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2")
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_download_object(self) -> None:
        with BytesIO() as file_object:
            with requests_mock.mock() as m:
                m.get(
                    self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
                    headers={"Content-Disposition": 'name="tableau_workbook"; filename="RESTAPISample.twbx"'},
                )
                file_path = self.server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2", filepath=file_object)
                self.assertTrue(isinstance(file_path, BytesIO))

    def test_download_sanitizes_name(self) -> None:
        filename = "Name,With,Commas.twbx"
        disposition = 'name="tableau_workbook"; filename="{}"'.format(filename)
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
                headers={"Content-Disposition": disposition},
            )
            file_path = self.server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2")
            self.assertEqual(os.path.basename(file_path), "NameWithCommas.twbx")
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_download_extract_only(self) -> None:
        # Pretend we're 2.5 for 'extract_only'
        self.server.version = "2.5"
        self.baseurl = self.server.workbooks.baseurl

        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content?includeExtract=False",
                headers={"Content-Disposition": 'name="tableau_workbook"; filename="RESTAPISample.twbx"'},
                complete_qs=True,
            )
            # Technically this shouldn't download a twbx, but we are interested in the qs, not the file
            file_path = self.server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2", include_extract=False)
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_download_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.workbooks.download, "")

    def test_populate_views(self) -> None:
        with open(POPULATE_VIEWS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/views", text=response_xml)
            single_workbook = TSC.WorkbookItem("test")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            self.server.workbooks.populate_views(single_workbook)

            views_list = single_workbook.views
            self.assertEqual("097dbe13-de89-445f-b2c3-02f28bd010c1", views_list[0].id)
            self.assertEqual("GDP per capita", views_list[0].name)
            self.assertEqual("RESTAPISample/sheets/GDPpercapita", views_list[0].content_url)

            self.assertEqual("2c1ab9d7-8d64-4cc6-b495-52e40c60c330", views_list[1].id)
            self.assertEqual("Country ranks", views_list[1].name)
            self.assertEqual("RESTAPISample/sheets/Countryranks", views_list[1].content_url)

            self.assertEqual("0599c28c-6d82-457e-a453-e52c1bdb00f5", views_list[2].id)
            self.assertEqual("Interest rates", views_list[2].name)
            self.assertEqual("RESTAPISample/sheets/Interestrates", views_list[2].content_url)

    def test_populate_views_with_usage(self) -> None:
        with open(POPULATE_VIEWS_USAGE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/views?includeUsageStatistics=true",
                text=response_xml,
            )
            single_workbook = TSC.WorkbookItem("test")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            self.server.workbooks.populate_views(single_workbook, usage=True)

            views_list = single_workbook.views
            self.assertEqual("097dbe13-de89-445f-b2c3-02f28bd010c1", views_list[0].id)
            self.assertEqual(2, views_list[0].total_views)
            self.assertEqual("2c1ab9d7-8d64-4cc6-b495-52e40c60c330", views_list[1].id)
            self.assertEqual(37, views_list[1].total_views)
            self.assertEqual("0599c28c-6d82-457e-a453-e52c1bdb00f5", views_list[2].id)
            self.assertEqual(0, views_list[2].total_views)

    def test_populate_views_missing_id(self) -> None:
        single_workbook = TSC.WorkbookItem("test")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.workbooks.populate_views, single_workbook)

    def test_populate_connections(self) -> None:
        with open(POPULATE_CONNECTIONS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/connections", text=response_xml)
            single_workbook = TSC.WorkbookItem("test")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            self.server.workbooks.populate_connections(single_workbook)

            self.assertEqual("37ca6ced-58d7-4dcf-99dc-f0a85223cbef", single_workbook.connections[0].id)
            self.assertEqual("dataengine", single_workbook.connections[0].connection_type)
            self.assertEqual("4506225a-0d32-4ab1-82d3-c24e85f7afba", single_workbook.connections[0].datasource_id)
            self.assertEqual("World Indicators", single_workbook.connections[0].datasource_name)

    def test_populate_permissions(self) -> None:
        with open(POPULATE_PERMISSIONS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/21778de4-b7b9-44bc-a599-1506a2639ace/permissions", text=response_xml)
            single_workbook = TSC.WorkbookItem("test")
            single_workbook._id = "21778de4-b7b9-44bc-a599-1506a2639ace"

            self.server.workbooks.populate_permissions(single_workbook)
            permissions = single_workbook.permissions

            self.assertEqual(permissions[0].grantee.tag_name, "group")
            self.assertEqual(permissions[0].grantee.id, "5e5e1978-71fa-11e4-87dd-7382f5c437af")
            self.assertDictEqual(
                permissions[0].capabilities,
                {
                    TSC.Permission.Capability.WebAuthoring: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.Filter: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.AddComment: TSC.Permission.Mode.Allow,
                },
            )

            self.assertEqual(permissions[1].grantee.tag_name, "user")
            self.assertEqual(permissions[1].grantee.id, "7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
            self.assertDictEqual(
                permissions[1].capabilities,
                {
                    TSC.Permission.Capability.ExportImage: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.ShareView: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Deny,
                    TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Deny,
                },
            )

    def test_add_permissions(self) -> None:
        with open(UPDATE_PERMISSIONS, "rb") as f:
            response_xml = f.read().decode("utf-8")

        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "21778de4-b7b9-44bc-a599-1506a2639ace"

        bob = UserItem.as_reference("7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
        group_of_people = GroupItem.as_reference("5e5e1978-71fa-11e4-87dd-7382f5c437af")

        new_permissions = [PermissionsRule(bob, {"Write": "Allow"}), PermissionsRule(group_of_people, {"Read": "Deny"})]

        with requests_mock.mock() as m:
            m.put(self.baseurl + "/21778de4-b7b9-44bc-a599-1506a2639ace/permissions", text=response_xml)
            permissions = self.server.workbooks.update_permissions(single_workbook, new_permissions)

        self.assertEqual(permissions[0].grantee.tag_name, "group")
        self.assertEqual(permissions[0].grantee.id, "5e5e1978-71fa-11e4-87dd-7382f5c437af")
        self.assertDictEqual(permissions[0].capabilities, {TSC.Permission.Capability.Read: TSC.Permission.Mode.Deny})

        self.assertEqual(permissions[1].grantee.tag_name, "user")
        self.assertEqual(permissions[1].grantee.id, "7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
        self.assertDictEqual(permissions[1].capabilities, {TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow})

    def test_populate_connections_missing_id(self) -> None:
        single_workbook = TSC.WorkbookItem("test")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.workbooks.populate_connections, single_workbook)

    def test_populate_pdf(self) -> None:
        self.server.version = "3.4"
        self.baseurl = self.server.workbooks.baseurl
        with open(POPULATE_PDF, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/pdf?type=a5&orientation=landscape",
                content=response,
            )
            single_workbook = TSC.WorkbookItem("test")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"

            type = TSC.PDFRequestOptions.PageType.A5
            orientation = TSC.PDFRequestOptions.Orientation.Landscape
            req_option = TSC.PDFRequestOptions(type, orientation)

            self.server.workbooks.populate_pdf(single_workbook, req_option)
            self.assertEqual(response, single_workbook.pdf)

    def test_populate_powerpoint(self) -> None:
        self.server.version = "3.8"
        self.baseurl = self.server.workbooks.baseurl
        with open(POPULATE_POWERPOINT, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/powerpoint",
                content=response,
            )
            single_workbook = TSC.WorkbookItem("test")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"

            self.server.workbooks.populate_powerpoint(single_workbook)
            self.assertEqual(response, single_workbook.powerpoint)

    def test_populate_preview_image(self) -> None:
        with open(POPULATE_PREVIEW_IMAGE, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/previewImage", content=response)
            single_workbook = TSC.WorkbookItem("test")
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            self.server.workbooks.populate_preview_image(single_workbook)

            self.assertEqual(response, single_workbook.preview_image)

    def test_populate_preview_image_missing_id(self) -> None:
        single_workbook = TSC.WorkbookItem("test")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.workbooks.populate_preview_image, single_workbook)

    def test_publish(self) -> None:
        with open(PUBLISH_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)

            new_workbook = TSC.WorkbookItem(
                name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
            )

            new_workbook.description = "REST API Testing"

            sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
            publish_mode = self.server.PublishMode.CreateNew

            new_workbook = self.server.workbooks.publish(new_workbook, sample_workbook, publish_mode)

        self.assertEqual("a8076ca1-e9d8-495e-bae6-c684dbb55836", new_workbook.id)
        self.assertEqual("RESTAPISample", new_workbook.name)
        self.assertEqual("RESTAPISample_0", new_workbook.content_url)
        self.assertEqual(False, new_workbook.show_tabs)
        self.assertEqual(1, new_workbook.size)
        self.assertEqual("2016-08-18T18:33:24Z", format_datetime(new_workbook.created_at))
        self.assertEqual("2016-08-18T20:31:34Z", format_datetime(new_workbook.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", new_workbook.project_id)
        self.assertEqual("default", new_workbook.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", new_workbook.owner_id)
        self.assertEqual("fe0b4e89-73f4-435e-952d-3a263fbfa56c", new_workbook.views[0].id)
        self.assertEqual("GDP per capita", new_workbook.views[0].name)
        self.assertEqual("RESTAPISample_0/sheets/GDPpercapita", new_workbook.views[0].content_url)
        self.assertEqual("REST API Testing", new_workbook.description)

    def test_publish_a_packaged_file_object(self) -> None:
        with open(PUBLISH_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)

            new_workbook = TSC.WorkbookItem(
                name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
            )

            sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")

            with open(sample_workbook, "rb") as fp:
                publish_mode = self.server.PublishMode.CreateNew

                new_workbook = self.server.workbooks.publish(new_workbook, fp, publish_mode)

        self.assertEqual("a8076ca1-e9d8-495e-bae6-c684dbb55836", new_workbook.id)
        self.assertEqual("RESTAPISample", new_workbook.name)
        self.assertEqual("RESTAPISample_0", new_workbook.content_url)
        self.assertEqual(False, new_workbook.show_tabs)
        self.assertEqual(1, new_workbook.size)
        self.assertEqual("2016-08-18T18:33:24Z", format_datetime(new_workbook.created_at))
        self.assertEqual("2016-08-18T20:31:34Z", format_datetime(new_workbook.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", new_workbook.project_id)
        self.assertEqual("default", new_workbook.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", new_workbook.owner_id)
        self.assertEqual("fe0b4e89-73f4-435e-952d-3a263fbfa56c", new_workbook.views[0].id)
        self.assertEqual("GDP per capita", new_workbook.views[0].name)
        self.assertEqual("RESTAPISample_0/sheets/GDPpercapita", new_workbook.views[0].content_url)

    def test_publish_non_packeged_file_object(self) -> None:
        with open(PUBLISH_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)

            new_workbook = TSC.WorkbookItem(
                name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
            )

            sample_workbook = os.path.join(TEST_ASSET_DIR, "RESTAPISample.twb")

            with open(sample_workbook, "rb") as fp:
                publish_mode = self.server.PublishMode.CreateNew

                new_workbook = self.server.workbooks.publish(new_workbook, fp, publish_mode)

        self.assertEqual("a8076ca1-e9d8-495e-bae6-c684dbb55836", new_workbook.id)
        self.assertEqual("RESTAPISample", new_workbook.name)
        self.assertEqual("RESTAPISample_0", new_workbook.content_url)
        self.assertEqual(False, new_workbook.show_tabs)
        self.assertEqual(1, new_workbook.size)
        self.assertEqual("2016-08-18T18:33:24Z", format_datetime(new_workbook.created_at))
        self.assertEqual("2016-08-18T20:31:34Z", format_datetime(new_workbook.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", new_workbook.project_id)
        self.assertEqual("default", new_workbook.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", new_workbook.owner_id)
        self.assertEqual("fe0b4e89-73f4-435e-952d-3a263fbfa56c", new_workbook.views[0].id)
        self.assertEqual("GDP per capita", new_workbook.views[0].name)
        self.assertEqual("RESTAPISample_0/sheets/GDPpercapita", new_workbook.views[0].content_url)

    def test_publish_path_object(self) -> None:
        with open(PUBLISH_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)

            new_workbook = TSC.WorkbookItem(
                name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
            )

            sample_workbook = Path(TEST_ASSET_DIR) / "SampleWB.twbx"
            publish_mode = self.server.PublishMode.CreateNew

            new_workbook = self.server.workbooks.publish(new_workbook, sample_workbook, publish_mode)

        self.assertEqual("a8076ca1-e9d8-495e-bae6-c684dbb55836", new_workbook.id)
        self.assertEqual("RESTAPISample", new_workbook.name)
        self.assertEqual("RESTAPISample_0", new_workbook.content_url)
        self.assertEqual(False, new_workbook.show_tabs)
        self.assertEqual(1, new_workbook.size)
        self.assertEqual("2016-08-18T18:33:24Z", format_datetime(new_workbook.created_at))
        self.assertEqual("2016-08-18T20:31:34Z", format_datetime(new_workbook.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", new_workbook.project_id)
        self.assertEqual("default", new_workbook.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", new_workbook.owner_id)
        self.assertEqual("fe0b4e89-73f4-435e-952d-3a263fbfa56c", new_workbook.views[0].id)
        self.assertEqual("GDP per capita", new_workbook.views[0].name)
        self.assertEqual("RESTAPISample_0/sheets/GDPpercapita", new_workbook.views[0].content_url)

    def test_publish_with_hidden_views_on_workbook(self) -> None:
        with open(PUBLISH_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)

            new_workbook = TSC.WorkbookItem(
                name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
            )

            sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
            publish_mode = self.server.PublishMode.CreateNew

            new_workbook.hidden_views = ["GDP per capita"]
            new_workbook = self.server.workbooks.publish(new_workbook, sample_workbook, publish_mode)
            request_body = m._adapter.request_history[0]._request.body
            # order of attributes in xml is unspecified
            self.assertTrue(re.search(rb"<views><view.*?hidden=\"true\".*?\/><\/views>", request_body))
            self.assertTrue(re.search(rb"<views><view.*?name=\"GDP per capita\".*?\/><\/views>", request_body))

    @pytest.mark.filterwarnings("ignore:'as_job' not available")
    def test_publish_with_query_params(self) -> None:
        with open(PUBLISH_ASYNC_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)

            new_workbook = TSC.WorkbookItem(
                name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
            )

            sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
            publish_mode = self.server.PublishMode.CreateNew

            self.server.workbooks.publish(
                new_workbook, sample_workbook, publish_mode, as_job=True, skip_connection_check=True
            )

            request_query_params = m._adapter.request_history[0].qs
            self.assertTrue("asjob" in request_query_params)
            self.assertTrue(request_query_params["asjob"])
            self.assertTrue("skipconnectioncheck" in request_query_params)
            self.assertTrue(request_query_params["skipconnectioncheck"])

    def test_publish_async(self) -> None:
        self.server.version = "3.0"
        baseurl = self.server.workbooks.baseurl
        with open(PUBLISH_ASYNC_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(baseurl, text=response_xml)

            new_workbook = TSC.WorkbookItem(
                name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
            )

            sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
            publish_mode = self.server.PublishMode.CreateNew

            new_job = self.server.workbooks.publish(new_workbook, sample_workbook, publish_mode, as_job=True)

        self.assertEqual("7c3d599e-949f-44c3-94a1-f30ba85757e4", new_job.id)
        self.assertEqual("PublishWorkbook", new_job.type)
        self.assertEqual("0", new_job.progress)
        self.assertEqual("2018-06-29T23:22:32Z", format_datetime(new_job.created_at))
        self.assertEqual(1, new_job.finish_code)

    def test_publish_invalid_file(self) -> None:
        new_workbook = TSC.WorkbookItem("test", "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
        self.assertRaises(IOError, self.server.workbooks.publish, new_workbook, ".", self.server.PublishMode.CreateNew)

    def test_publish_invalid_file_type(self) -> None:
        new_workbook = TSC.WorkbookItem("test", "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
        self.assertRaises(
            ValueError,
            self.server.workbooks.publish,
            new_workbook,
            os.path.join(TEST_ASSET_DIR, "SampleDS.tds"),
            self.server.PublishMode.CreateNew,
        )

    def test_publish_unnamed_file_object(self) -> None:
        new_workbook = TSC.WorkbookItem("test")

        with open(os.path.join(TEST_ASSET_DIR, "SampleWB.twbx"), "rb") as f:
            self.assertRaises(
                ValueError, self.server.workbooks.publish, new_workbook, f, self.server.PublishMode.CreateNew
            )

    def test_publish_non_bytes_file_object(self) -> None:
        new_workbook = TSC.WorkbookItem("test")

        with open(os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")) as f:
            self.assertRaises(
                TypeError, self.server.workbooks.publish, new_workbook, f, self.server.PublishMode.CreateNew
            )

    def test_publish_file_object_of_unknown_type_raises_exception(self) -> None:
        new_workbook = TSC.WorkbookItem("test")
        with BytesIO() as file_object:
            file_object.write(bytes.fromhex("89504E470D0A1A0A"))
            file_object.seek(0)
            self.assertRaises(
                ValueError, self.server.workbooks.publish, new_workbook, file_object, self.server.PublishMode.CreateNew
            )

    def test_publish_multi_connection(self) -> None:
        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )
        connection1 = TSC.ConnectionItem()
        connection1.server_address = "mysql.test.com"
        connection1.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)
        connection2 = TSC.ConnectionItem()
        connection2.server_address = "pgsql.test.com"
        connection2.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)

        response = RequestFactory.Workbook._generate_xml(new_workbook, connections=[connection1, connection2])
        # Can't use ConnectionItem parser due to xml namespace problems
        connection_results = fromstring(response).findall(".//connection")

        self.assertEqual(connection_results[0].get("serverAddress", None), "mysql.test.com")
        self.assertEqual(connection_results[0].find("connectionCredentials").get("name", None), "test")  # type: ignore[union-attr]
        self.assertEqual(connection_results[1].get("serverAddress", None), "pgsql.test.com")
        self.assertEqual(connection_results[1].find("connectionCredentials").get("password", None), "secret")  # type: ignore[union-attr]

    def test_publish_multi_connection_flat(self) -> None:
        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )
        connection1 = TSC.ConnectionItem()
        connection1.server_address = "mysql.test.com"
        connection1.username = "test"
        connection1.password = "secret"
        connection1.embed_password = True
        connection2 = TSC.ConnectionItem()
        connection2.server_address = "pgsql.test.com"
        connection2.username = "test"
        connection2.password = "secret"
        connection2.embed_password = True

        response = RequestFactory.Workbook._generate_xml(new_workbook, connections=[connection1, connection2])
        # Can't use ConnectionItem parser due to xml namespace problems
        connection_results = fromstring(response).findall(".//connection")

        self.assertEqual(connection_results[0].get("serverAddress", None), "mysql.test.com")
        self.assertEqual(connection_results[0].find("connectionCredentials").get("name", None), "test")  # type: ignore[union-attr]
        self.assertEqual(connection_results[1].get("serverAddress", None), "pgsql.test.com")
        self.assertEqual(connection_results[1].find("connectionCredentials").get("password", None), "secret")  # type: ignore[union-attr]

    def test_synchronous_publish_timeout_error(self) -> None:
        with requests_mock.mock() as m:
            m.register_uri("POST", self.baseurl, status_code=504)

            new_workbook = TSC.WorkbookItem(project_id="")
            publish_mode = self.server.PublishMode.CreateNew

            self.assertRaisesRegex(
                InternalServerError,
                "Please use asynchronous publishing to avoid timeouts",
                self.server.workbooks.publish,
                new_workbook,
                asset("SampleWB.twbx"),
                publish_mode,
            )

    def test_delete_extracts_all(self) -> None:
        self.server.version = "3.10"
        self.baseurl = self.server.workbooks.baseurl

        with open(PUBLISH_ASYNC_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(
                self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/deleteExtract", status_code=200, text=response_xml
            )
            self.server.workbooks.delete_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    def test_create_extracts_all(self) -> None:
        self.server.version = "3.10"
        self.baseurl = self.server.workbooks.baseurl

        with open(PUBLISH_ASYNC_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(
                self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract", status_code=200, text=response_xml
            )
            self.server.workbooks.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    def test_create_extracts_one(self) -> None:
        self.server.version = "3.10"
        self.baseurl = self.server.workbooks.baseurl

        datasource = TSC.DatasourceItem("test")
        datasource._id = "1f951daf-4061-451a-9df1-69a8062664f2"

        with open(PUBLISH_ASYNC_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(
                self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract", status_code=200, text=response_xml
            )
            self.server.workbooks.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42", False, datasource)

    def test_revisions(self) -> None:
        self.baseurl = self.server.workbooks.baseurl
        workbook = TSC.WorkbookItem("project", "test")
        workbook._id = "06b944d2-959d-4604-9305-12323c95e70e"

        with open(REVISION_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get("{0}/{1}/revisions".format(self.baseurl, workbook.id), text=response_xml)
            self.server.workbooks.populate_revisions(workbook)
            revisions = workbook.revisions

        self.assertEqual(len(revisions), 3)
        self.assertEqual("2016-07-26T20:34:56Z", format_datetime(revisions[0].created_at))
        self.assertEqual("2016-07-27T20:34:56Z", format_datetime(revisions[1].created_at))
        self.assertEqual("2016-07-28T20:34:56Z", format_datetime(revisions[2].created_at))

        self.assertEqual(False, revisions[0].deleted)
        self.assertEqual(False, revisions[0].current)
        self.assertEqual(False, revisions[1].deleted)
        self.assertEqual(False, revisions[1].current)
        self.assertEqual(False, revisions[2].deleted)
        self.assertEqual(True, revisions[2].current)

        self.assertEqual("Cassie", revisions[0].user_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", revisions[0].user_id)
        self.assertIsNone(revisions[1].user_name)
        self.assertIsNone(revisions[1].user_id)
        self.assertEqual("Cassie", revisions[2].user_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", revisions[2].user_id)

    def test_delete_revision(self) -> None:
        self.baseurl = self.server.workbooks.baseurl
        workbook = TSC.WorkbookItem("project", "test")
        workbook._id = "06b944d2-959d-4604-9305-12323c95e70e"

        with requests_mock.mock() as m:
            m.delete("{0}/{1}/revisions/3".format(self.baseurl, workbook.id))
            self.server.workbooks.delete_revision(workbook.id, "3")

    def test_download_revision(self) -> None:
        with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
            m.get(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/revisions/3/content",
                headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
            )
            file_path = self.server.workbooks.download_revision("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", "3", td)
            self.assertTrue(os.path.exists(file_path))

    def test_bad_download_response(self) -> None:
        with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
            m.get(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content",
                headers={"Content-Disposition": '''name="tableau_workbook"; filename*=UTF-8''"Sample workbook.twb"'''},
            )
            file_path = self.server.workbooks.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", td)
            self.assertTrue(os.path.exists(file_path))

    def test_odata_connection(self) -> None:
        self.baseurl = self.server.workbooks.baseurl
        workbook = TSC.WorkbookItem("project", "test")
        workbook._id = "06b944d2-959d-4604-9305-12323c95e70e"
        connection = TSC.ConnectionItem()
        url = "https://odata.website.com/TestODataEndpoint"
        connection.server_address = url
        connection._connection_type = "odata"
        connection._id = "17376070-64d1-4d17-acb4-a56e4b5b1768"

        creds = TSC.ConnectionCredentials("", "", True)
        connection.connection_credentials = creds
        with open(ODATA_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")

        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{workbook.id}/connections/{connection.id}", text=response_xml)
            self.server.workbooks.update_connection(workbook, connection)

            history = m.request_history

        request = history[0]
        xml = fromstring(request.body)
        xml_connection = xml.find(".//connection")

        assert xml_connection is not None
        self.assertEqual(xml_connection.get("serverAddress"), url)
