import os
import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server import RequestFactory
from tableauserverclient.models import WebhookItem
from ._utils import asset

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = asset("webhook_get.xml")
CREATE_XML = asset("webhook_create.xml")
CREATE_REQUEST_XML = asset("webhook_create_request.xml")


class WebhookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.6"

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.webhooks.baseurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            webhooks, _ = self.server.webhooks.get()
            self.assertEqual(len(webhooks), 1)
            webhook = webhooks[0]

            self.assertEqual(webhook.url, "url")
            self.assertEqual(webhook.event, "datasource-created")
            self.assertEqual(webhook.owner_id, "webhook_owner_luid")
            self.assertEqual(webhook.name, "webhook-name")
            self.assertEqual(webhook.id, "webhook-id")

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.webhooks.get)

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
            self.server.webhooks.delete("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

    def test_delete_missing_id(self) -> None:
        self.assertRaises(ValueError, self.server.webhooks.delete, "")

    def test_test(self) -> None:
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760/test", status_code=200)
            self.server.webhooks.test("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

    def test_create(self) -> None:
        with open(CREATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            webhook_model = TSC.WebhookItem()
            webhook_model.name = "Test Webhook"
            webhook_model.url = "https://ifttt.com/maker-url"
            webhook_model.event = "datasource-created"

            new_webhook = self.server.webhooks.create(webhook_model)

            self.assertNotEqual(new_webhook.id, None)

    def test_request_factory(self):
        with open(CREATE_REQUEST_XML, "rb") as f:
            webhook_request_expected = f.read().decode("utf-8")

        webhook_item = WebhookItem()
        webhook_item._set_values("webhook-id", "webhook-name", "url", "api-event-name", None)
        webhook_request_actual = "{}\n".format(RequestFactory.Webhook.create_req(webhook_item).decode("utf-8"))
        self.maxDiff = None
        # windows does /r/n for linebreaks, remove the extra char if it is there
        self.assertEqual(webhook_request_expected.replace("\r", ""), webhook_request_actual)
