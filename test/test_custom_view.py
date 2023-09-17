import os
import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = os.path.join(TEST_ASSET_DIR, "custom_view_get.xml")
GET_XML_ID = os.path.join(TEST_ASSET_DIR, "custom_view_get_id.xml")
POPULATE_PREVIEW_IMAGE = os.path.join(TEST_ASSET_DIR, "Sample View Image.png")
CUSTOM_VIEW_UPDATE_XML = os.path.join(TEST_ASSET_DIR, "custom_view_update.xml")


class CustomViewTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.19"  # custom views only introduced in 3.19

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.custom_views.baseurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
            print(response_xml)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_views, pagination_item = self.server.custom_views.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", all_views[0].id)
        self.assertEqual("ENDANGERED SAFARI", all_views[0].name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", all_views[0].content_url)
        self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", all_views[0].workbook.id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_views[0].owner.id)
        self.assertIsNone(all_views[0].created_at)
        self.assertIsNone(all_views[0].updated_at)
        self.assertFalse(all_views[0].shared)

        self.assertEqual("fd252f73-593c-4c4e-8584-c032b8022adc", all_views[1].id)
        self.assertEqual("Overview", all_views[1].name)
        self.assertEqual("6d13b0ca-043d-4d42-8c9d-3f3313ea3a00", all_views[1].workbook.id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_views[1].owner.id)
        self.assertEqual("2002-05-30T09:00:00Z", format_datetime(all_views[1].created_at))
        self.assertEqual("2002-06-05T08:00:59Z", format_datetime(all_views[1].updated_at))
        self.assertTrue(all_views[1].shared)

    def test_get_by_id(self) -> None:
        with open(GET_XML_ID, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5", text=response_xml)
            view: TSC.CustomViewItem = self.server.custom_views.get_by_id("d79634e1-6063-4ec9-95ff-50acbf609ff5")

        self.assertEqual("d79634e1-6063-4ec9-95ff-50acbf609ff5", view.id)
        self.assertEqual("ENDANGERED SAFARI", view.name)
        self.assertEqual("SafariSample/sheets/ENDANGEREDSAFARI", view.content_url)
        if view.workbook:
            self.assertEqual("3cc6cd06-89ce-4fdc-b935-5294135d6d42", view.workbook.id)
        if view.owner:
            self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", view.owner.id)
        if view.view:
            self.assertEqual("5241e88d-d384-4fd7-9c2f-648b5247efc5", view.view.id)
        self.assertEqual("2002-05-30T09:00:00Z", format_datetime(view.created_at))
        self.assertEqual("2002-06-05T08:00:59Z", format_datetime(view.updated_at))

    def test_get_by_id_missing_id(self) -> None:
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.custom_views.get_by_id, None)

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.custom_views.get)

    def test_populate_image(self) -> None:
        with open(POPULATE_PREVIEW_IMAGE, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/image", content=response)
            single_view = TSC.CustomViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            self.server.custom_views.populate_image(single_view)
            self.assertEqual(response, single_view.image)

    def test_populate_image_with_options(self) -> None:
        with open(POPULATE_PREVIEW_IMAGE, "rb") as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/image?resolution=high&maxAge=10", content=response
            )
            single_view = TSC.CustomViewItem()
            single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
            req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High, maxage=10)
            self.server.custom_views.populate_image(single_view, req_option)
            self.assertEqual(response, single_view.image)

    def test_populate_image_missing_id(self) -> None:
        single_view = TSC.CustomViewItem()
        single_view._id = None
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.custom_views.populate_image, single_view)

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42", status_code=204)
            self.server.custom_views.delete("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    def test_delete_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.custom_views.delete, "")

    def test_update(self) -> None:
        with open(CUSTOM_VIEW_UPDATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            the_custom_view = TSC.CustomViewItem("1d0304cd-3796-429f-b815-7258370b9b74", name="Best test ever")
            the_custom_view._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            the_custom_view.owner = TSC.UserItem()
            the_custom_view.owner.id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            the_custom_view = self.server.custom_views.update(the_custom_view)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", the_custom_view.id)
        if the_custom_view.owner:
            self.assertEqual("dd2239f6-ddf1-4107-981a-4cf94e415794", the_custom_view.owner.id)
        self.assertEqual("Best test ever", the_custom_view.name)

    def test_update_missing_id(self) -> None:
        cv = TSC.CustomViewItem(name="test")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.custom_views.update, cv)
