import os
import unittest

import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

CREATE_XML = os.path.join(TEST_ASSET_DIR, "subscription_create.xml")
GET_XML = os.path.join(TEST_ASSET_DIR, "subscription_get.xml")
GET_XML_BY_ID = os.path.join(TEST_ASSET_DIR, "subscription_get_by_id.xml")


class SubscriptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)
        self.server.version = "2.6"

        # Fake Signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.subscriptions.baseurl

    def test_get_subscriptions(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_subscriptions, pagination_item = self.server.subscriptions.get()

        self.assertEqual(2, pagination_item.total_available)
        subscription = all_subscriptions[0]
        self.assertEqual("382e9a6e-0c08-4a95-b6c1-c14df7bac3e4", subscription.id)
        self.assertEqual("NOT FOUND!", subscription.message)
        self.assertTrue(subscription.attach_image)
        self.assertFalse(subscription.attach_pdf)
        self.assertFalse(subscription.suspended)
        self.assertFalse(subscription.send_if_view_empty)
        self.assertIsNone(subscription.page_orientation)
        self.assertIsNone(subscription.page_size_option)
        self.assertEqual("Not Found Alert", subscription.subject)
        self.assertEqual("cdd716ca-5818-470e-8bec-086885dbadee", subscription.target.id)
        self.assertEqual("View", subscription.target.type)
        self.assertEqual("c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e", subscription.user_id)
        self.assertEqual("7617c389-cdca-4940-a66e-69956fcebf3e", subscription.schedule_id)

        subscription = all_subscriptions[1]
        self.assertEqual("23cb7630-afc8-4c8e-b6cd-83ae0322ec66", subscription.id)
        self.assertEqual("overview", subscription.message)
        self.assertFalse(subscription.attach_image)
        self.assertTrue(subscription.attach_pdf)
        self.assertTrue(subscription.suspended)
        self.assertTrue(subscription.send_if_view_empty)
        self.assertEqual("PORTRAIT", subscription.page_orientation)
        self.assertEqual("A5", subscription.page_size_option)
        self.assertEqual("Last 7 Days", subscription.subject)
        self.assertEqual("2e6b4e8f-22dd-4061-8f75-bf33703da7e5", subscription.target.id)
        self.assertEqual("Workbook", subscription.target.type)
        self.assertEqual("c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e", subscription.user_id)
        self.assertEqual("3407cd38-7b39-4983-86a6-67a1506a5e3f", subscription.schedule_id)

    def test_get_subscription_by_id(self) -> None:
        with open(GET_XML_BY_ID, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/382e9a6e-0c08-4a95-b6c1-c14df7bac3e4", text=response_xml)
            subscription = self.server.subscriptions.get_by_id("382e9a6e-0c08-4a95-b6c1-c14df7bac3e4")

        self.assertEqual("382e9a6e-0c08-4a95-b6c1-c14df7bac3e4", subscription.id)
        self.assertEqual("View", subscription.target.type)
        self.assertEqual("cdd716ca-5818-470e-8bec-086885dbadee", subscription.target.id)
        self.assertEqual("c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e", subscription.user_id)
        self.assertEqual("Not Found Alert", subscription.subject)
        self.assertEqual("7617c389-cdca-4940-a66e-69956fcebf3e", subscription.schedule_id)

    def test_create_subscription(self) -> None:
        with open(CREATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)

            target_item = TSC.Target("960e61f2-1838-40b2-bba2-340c9492f943", "workbook")
            new_subscription = TSC.SubscriptionItem(
                "subject", "4906c453-d5ec-4972-9ff4-789b629bdfa2", "8d30c8de-0a5f-4bee-b266-c621b4f3eed0", target_item
            )
            new_subscription = self.server.subscriptions.create(new_subscription)

        self.assertEqual("78e9318d-2d29-4d67-b60f-3f2f5fd89ecc", new_subscription.id)
        self.assertEqual("sub_name", new_subscription.subject)
        self.assertEqual("960e61f2-1838-40b2-bba2-340c9492f943", new_subscription.target.id)
        self.assertEqual("Workbook", new_subscription.target.type)
        self.assertEqual("4906c453-d5ec-4972-9ff4-789b629bdfa2", new_subscription.schedule_id)
        self.assertEqual("8d30c8de-0a5f-4bee-b266-c621b4f3eed0", new_subscription.user_id)

    def test_delete_subscription(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/78e9318d-2d29-4d67-b60f-3f2f5fd89ecc", status_code=204)
            self.server.subscriptions.delete("78e9318d-2d29-4d67-b60f-3f2f5fd89ecc")
