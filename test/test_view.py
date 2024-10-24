import os
import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient import UserItem, GroupItem, PermissionsRule
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

ADD_TAGS_XML = os.path.join(TEST_ASSET_DIR, "view_add_tags.xml")
GET_XML = os.path.join(TEST_ASSET_DIR, "view_get.xml")
GET_XML_ID = os.path.join(TEST_ASSET_DIR, "view_get_id.xml")
GET_XML_USAGE = os.path.join(TEST_ASSET_DIR, "view_get_usage.xml")
GET_XML_ID_USAGE = os.path.join(TEST_ASSET_DIR, "view_get_id_usage.xml")
POPULATE_PREVIEW_IMAGE = os.path.join(TEST_ASSET_DIR, "Sample View Image.png")
POPULATE_PDF = os.path.join(TEST_ASSET_DIR, "populate_pdf.pdf")
POPULATE_CSV = os.path.join(TEST_ASSET_DIR, "populate_csv.csv")
POPULATE_EXCEL = os.path.join(TEST_ASSET_DIR, "populate_excel.xlsx")
POPULATE_PERMISSIONS_XML = os.path.join(TEST_ASSET_DIR, "view_populate_permissions.xml")
UPDATE_PERMISSIONS = os.path.join(TEST_ASSET_DIR, "view_update_permissions.xml")
UPDATE_XML = os.path.join(TEST_ASSET_DIR, "workbook_update.xml")


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.2"

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.views.baseurl
        self.siteurl = self.server.views.siteurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_views, pagination_item = self.server.views.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", all_views[0].id)
        self.assertEqual("ENDANGERED SAFARI", all_views[0].name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", all_views[0].content_url)
        self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", all_views[0].workbook_id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_views[0].owner_id)
        self.assertEqual("5241e88d-d384-4fd7-9c2f-648b5247efc5", all_views[0].project_id)
        self.assertEqual(set(["tag1", "tag2"]), all_views[0].tags)
        self.assertIsNone(all_views[0].created_at)
        self.assertIsNone(all_views[0].updated_at)
        self.assertIsNone(all_views[0].sheet_type)

        self.assertEqual("fd252f73-593c-4c4e-8584-c032b8022adc", all_views[1].id)
        self.assertEqual("Overview", all_views[1].name)
        self.assertEqual("Superstore/sheets/Overview", all_views[1].content_url)
        self.assertEqual("6d13b0ca-043d-4d42-8c9d-3f3313ea3a00", all_views[1].workbook_id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_views[1].owner_id)
        self.assertEqual("5b534f74-3226-11e8-b47a-cb2e00f738a3", all_views[1].project_id)
        self.assertEqual("2002-05-30T09:00:00Z", format_datetime(all_views[1].created_at))
        self.assertEqual("2002-06-05T08:00:59Z", format_datetime(all_views[1].updated_at))
        self.assertEqual("story", all_views[1].sheet_type)

    def test_get_by_id(self) -> None:
        with open(GET_XML_ID, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5", text=response_xml)
            view = self.server.views.get_by_id("d79634e1-6063-4ec9-95ff-50acbf609ff5")

        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", view.id)
        self.assertEqual("ENDANGERED SAFARI", view.name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", view.content_url)
        self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", view.workbook_id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", view.owner_id)
        self.assertEqual("5241e88d-d384-4fd7-9c2f-648b5247efc5", view.project_id)
        self.assertEqual(set(["tag1", "tag2"]), view.tags)
        self.assertEqual("2002-05-30T09:00:00Z", format_datetime(view.created_at))
        self.assertEqual("2002-06-05T08:00:59Z", format_datetime(view.updated_at))
        self.assertEqual("story", view.sheet_type)

    def test_get_by_id_usage(self) -> None:
        with open(GET_XML_ID_USAGE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5?includeUsageStatistics=true", text=response_xml)
            view = self.server.views.get_by_id("d79634e1-6063-4ec9-95ff-50acbf609ff5", usage=True)

        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", view.id)
        self.assertEqual("ENDANGERED SAFARI", view.name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", view.content_url)
        self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", view.workbook_id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", view.owner_id)
        self.assertEqual("5241e88d-d384-4fd7-9c2f-648b5247efc5", view.project_id)
        self.assertEqual(set(["tag1", "tag2"]), view.tags)
        self.assertEqual("2002-05-30T09:00:00Z", format_datetime(view.created_at))
        self.assertEqual("2002-06-05T08:00:59Z", format_datetime(view.updated_at))
        self.assertEqual("story", view.sheet_type)
        self.assertEqual(7, view.total_views)

    def test_get_by_id_missing_id(self) -> None:
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.views.get_by_id, None)

    def test_get_with_usage(self) -> None:
        with open(GET_XML_USAGE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "?includeUsageStatistics=true", text=response_xml)
            all_views, pagination_item = self.server.views.get(usage=True)

        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", all_views[0].id)
        self.assertEqual(7, all_views[0].total_views)
        self.assertIsNone(all_views[0].created_at)
        self.assertIsNone(all_views[0].updated_at)
        self.assertIsNone(all_views[0].sheet_type)

        self.assertEqual("fd252f73-593c-4c4e-8584-c032b8022adc", all_views[1].id)
        self.assertEqual(13, all_views[1].total_views)
        self.assertEqual("2002-05-30T09:00:00Z", format_datetime(all_views[1].created_at))
        self.assertEqual("2002-06-05T08:00:59Z", format_datetime(all_views[1].updated_at))
        self.assertEqual("story", all_views[1].sheet_type)

    def test_get_with_usage_and_filter(self) -> None:
        with open(GET_XML_USAGE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "?includeUsageStatistics=true&filter=name:in:[foo,bar]", text=response_xml)
            options = TSC.RequestOptions()
            options.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.In, ["foo", "bar"])
            )
            all_views, pagination_item = self.server.views.get(req_options=options, usage=True)

        self.assertEqual("ENDANGERED SAFARI", all_views[0].name)
        self.assertEqual(7, all_views[0].total_views)
        self.assertEqual("Overview", all_views[1].name)
        self.assertEqual(13, all_views[1].total_views)

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.views.get)

    def test_populate_preview_image(self) -> None:
        with open(POPULATE_PREVIEW_IMAGE, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(
                self.siteurl + "/workbooks/3cc6cd06-89ce-4fdc-b935-5294135d6d42/"
                "views/d79634e1-6063-4ec9-95ff-50acbf609ff5/previewImage",
                content=response,
            )
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            single_view._workbook_id = "3cc6cd06-89ce-4fdc-b935-5294135d6d42"
            self.server.views.populate_preview_image(single_view)
            self.assertEqual(response, single_view.preview_image)

    def test_populate_preview_image_missing_id(self) -> None:
        single_view = TSC.ViewItem()
        single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.views.populate_preview_image, single_view)

        single_view._id = None
        single_view._workbook_id = "3cc6cd06-89ce-4fdc-b935-5294135d6d42"
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.views.populate_preview_image, single_view)

    def test_populate_image(self) -> None:
        with open(POPULATE_PREVIEW_IMAGE, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/image", content=response)
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            self.server.views.populate_image(single_view)
            self.assertEqual(response, single_view.image)

    def test_populate_image_with_options(self) -> None:
        with open(POPULATE_PREVIEW_IMAGE, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/image?resolution=high&maxAge=10", content=response
            )
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High, maxage=10)
            self.server.views.populate_image(single_view, req_option)
            self.assertEqual(response, single_view.image)

    def test_populate_pdf(self) -> None:
        with open(POPULATE_PDF, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/pdf?type=letter&orientation=portrait&maxAge=5",
                content=response,
            )
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"

            size = TSC.PDFRequestOptions.PageType.Letter
            orientation = TSC.PDFRequestOptions.Orientation.Portrait
            req_option = TSC.PDFRequestOptions(size, orientation, 5)

            self.server.views.populate_pdf(single_view, req_option)
            self.assertEqual(response, single_view.pdf)

    def test_populate_csv(self) -> None:
        with open(POPULATE_CSV, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/data?maxAge=1", content=response)
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            request_option = TSC.CSVRequestOptions(maxage=1)
            self.server.views.populate_csv(single_view, request_option)

            csv_file = b"".join(single_view.csv)
            self.assertEqual(response, csv_file)

    def test_populate_csv_default_maxage(self) -> None:
        with open(POPULATE_CSV, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/data", content=response)
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            self.server.views.populate_csv(single_view)

            csv_file = b"".join(single_view.csv)
            self.assertEqual(response, csv_file)

    def test_populate_image_missing_id(self) -> None:
        single_view = TSC.ViewItem()
        single_view._id = None
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.views.populate_image, single_view)

    def test_populate_permissions(self) -> None:
        with open(POPULATE_PERMISSIONS_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/e490bec4-2652-4fda-8c4e-f087db6fa328/permissions", text=response_xml)
            single_view = TSC.ViewItem()
            single_view._id = "e490bec4-2652-4fda-8c4e-f087db6fa328"

            self.server.views.populate_permissions(single_view)
            permissions = single_view.permissions

            self.assertEqual(permissions[0].grantee.tag_name, "group")
            self.assertEqual(permissions[0].grantee.id, "c8f2773a-c83a-11e8-8c8f-33e6d787b506")
            self.assertDictEqual(
                permissions[0].capabilities,
                {
                    TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.AddComment: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.ExportImage: TSC.Permission.Mode.Allow,
                },
            )

    def test_add_permissions(self) -> None:
        with open(UPDATE_PERMISSIONS, "rb") as f:
            response_xml = f.read().decode("utf-8")

        single_view = TSC.ViewItem()
        single_view._id = "21778de4-b7b9-44bc-a599-1506a2639ace"

        bob = UserItem.as_reference("7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
        group_of_people = GroupItem.as_reference("5e5e1978-71fa-11e4-87dd-7382f5c437af")

        new_permissions = [PermissionsRule(bob, {"Write": "Allow"}), PermissionsRule(group_of_people, {"Read": "Deny"})]

        with requests_mock.mock() as m:
            m.put(self.baseurl + "/21778de4-b7b9-44bc-a599-1506a2639ace/permissions", text=response_xml)
            permissions = self.server.views.update_permissions(single_view, new_permissions)

        self.assertEqual(permissions[0].grantee.tag_name, "group")
        self.assertEqual(permissions[0].grantee.id, "5e5e1978-71fa-11e4-87dd-7382f5c437af")
        self.assertDictEqual(permissions[0].capabilities, {TSC.Permission.Capability.Read: TSC.Permission.Mode.Deny})

        self.assertEqual(permissions[1].grantee.tag_name, "user")
        self.assertEqual(permissions[1].grantee.id, "7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
        self.assertDictEqual(permissions[1].capabilities, {TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow})

    def test_update_tags(self) -> None:
        with open(ADD_TAGS_XML, "rb") as f:
            add_tags_xml = f.read().decode("utf-8")
        with open(UPDATE_XML, "rb") as f:
            update_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/tags", text=add_tags_xml)
            m.delete(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/tags/b", status_code=204)
            m.delete(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/tags/d", status_code=204)
            m.put(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5", text=update_xml)
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            single_view._initial_tags.update(["a", "b", "c", "d"])
            single_view.tags.update(["a", "c", "e"])
            updated_view = self.server.views.update(single_view)

        self.assertEqual(single_view.tags, updated_view.tags)
        self.assertEqual(single_view._initial_tags, updated_view._initial_tags)

    def test_populate_excel(self) -> None:
        self.server.version = "3.8"
        self.baseurl = self.server.views.baseurl
        with open(POPULATE_EXCEL, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/crosstab/excel?maxAge=1", content=response)
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            request_option = TSC.ExcelRequestOptions(maxage=1)
            self.server.views.populate_excel(single_view, request_option)

            excel_file = b"".join(single_view.excel)
            self.assertEqual(response, excel_file)

    def test_filter_excel(self) -> None:
        self.server.version = "3.8"
        self.baseurl = self.server.views.baseurl
        with open(POPULATE_EXCEL, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/crosstab/excel?maxAge=1", content=response)
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            request_option = TSC.ExcelRequestOptions(maxage=1)
            request_option.vf("stuff", "1")
            self.server.views.populate_excel(single_view, request_option)

            excel_file = b"".join(single_view.excel)
            self.assertEqual(response, excel_file)

    def test_pdf_height(self) -> None:
        self.server.version = "3.8"
        self.baseurl = self.server.views.baseurl
        with open(POPULATE_PDF, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/pdf?vizHeight=1080&vizWidth=1920",
                content=response,
            )
            single_view = TSC.ViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"

            req_option = TSC.PDFRequestOptions(
                viz_height=1080,
                viz_width=1920,
            )

            self.server.views.populate_pdf(single_view, req_option)
            self.assertEqual(response, single_view.pdf)

    def test_pdf_errors(self) -> None:
        req_option = TSC.PDFRequestOptions(viz_height=1080)
        with self.assertRaises(ValueError):
            req_option.get_query_params()
        req_option = TSC.PDFRequestOptions(viz_width=1920)
        with self.assertRaises(ValueError):
            req_option.get_query_params()
