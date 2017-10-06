import unittest
import os
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = os.path.join(TEST_ASSET_DIR, "subscription_get.xml")
GET_XML_BY_ID = os.path.join(TEST_ASSET_DIR, "subscription_get_by_id.xml")


class SubscriptionTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test")
        self.server.version = '2.6'

        # Fake Signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.subscriptions.baseurl

    def test_get_subscriptions(self):
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_subscriptions, pagination_item = self.server.subscriptions.get()

        subscription = all_subscriptions[0]
        self.assertEqual('382e9a6e-0c08-4a95-b6c1-c14df7bac3e4', subscription.id)
        self.assertEqual('View', subscription.target.type)
        self.assertEqual('cdd716ca-5818-470e-8bec-086885dbadee', subscription.target.id)
        self.assertEqual('c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e', subscription.user_id)
        self.assertEqual('Not Found Alert', subscription.subject)
        self.assertEqual('7617c389-cdca-4940-a66e-69956fcebf3e', subscription.schedule_id)

    def test_get_subscription_by_id(self):
        with open(GET_XML_BY_ID, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/382e9a6e-0c08-4a95-b6c1-c14df7bac3e4', text=response_xml)
            subscription = self.server.subscriptions.get_by_id('382e9a6e-0c08-4a95-b6c1-c14df7bac3e4')

        self.assertEqual('382e9a6e-0c08-4a95-b6c1-c14df7bac3e4', subscription.id)
        self.assertEqual('View', subscription.target.type)
        self.assertEqual('cdd716ca-5818-470e-8bec-086885dbadee', subscription.target.id)
        self.assertEqual('c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e', subscription.user_id)
        self.assertEqual('Not Found Alert', subscription.subject)
        self.assertEqual('7617c389-cdca-4940-a66e-69956fcebf3e', subscription.schedule_id)
