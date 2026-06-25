from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server import RequestFactory
from tableauserverclient.models import WebhookItem

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "webhook_get.xml"
GET_NEW_EVENT_XML = TEST_ASSET_DIR / "webhook_get_new_event.xml"
CREATE_XML = TEST_ASSET_DIR / "webhook_create.xml"
CREATE_REQUEST_XML = TEST_ASSET_DIR / "webhook_create_request.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.6"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.webhooks.baseurl, text=response_xml)
        webhooks, _ = server.webhooks.get()
        assert len(webhooks) == 1
        webhook = webhooks[0]

        assert webhook.url == "url"
        assert webhook.event == "datasource-created"
        assert webhook.owner_id == "webhook_owner_luid"
        assert webhook.name == "webhook-name"
        assert webhook.id == "webhook-id"


def test_get_before_signin(server: TSC.Server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.webhooks.get()


def test_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.webhooks.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
        server.webhooks.delete("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")


def test_delete_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.webhooks.delete("")


def test_test(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.webhooks.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760/test", status_code=200)
        server.webhooks.test("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")


def test_create(server: TSC.Server) -> None:
    response_xml = CREATE_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.webhooks.baseurl, text=response_xml)
        webhook_model = TSC.WebhookItem()
        webhook_model.name = "Test Webhook"
        webhook_model.url = "https://ifttt.com/maker-url"
        webhook_model.event = "datasource-created"

        new_webhook = server.webhooks.create(webhook_model)

        assert new_webhook.id is not None


def test_request_factory():
    webhook_request_expected = CREATE_REQUEST_XML.read_text()

    webhook_item = WebhookItem()
    webhook_item._set_values("webhook-id", "webhook-name", "url", "api-event-name", None)
    webhook_request_actual = "{}\n".format(RequestFactory.Webhook.create_req(webhook_item).decode("utf-8"))
    # windows does /r/n for linebreaks, remove the extra char if it is there
    assert webhook_request_expected.replace("\r", "") == webhook_request_actual


def test_event_setter_none():
    """Setting event to None should store None without crashing."""
    item = WebhookItem()
    item.event = "datasource-updated"
    assert item.event == "datasource-updated"
    item.event = None
    assert item._event is None
    assert item.event is None


def test_event_setter_short_name():
    """Short event names should be stored with the webhook-source-event- prefix."""
    item = WebhookItem()
    item.event = "datasource-updated"
    assert item._event == "webhook-source-event-datasource-updated"
    assert item.event == "datasource-updated"


def test_event_setter_full_source_name():
    """Full webhook-source-event- names should be accepted and stored as-is."""
    item = WebhookItem()
    item.event = "webhook-source-event-datasource-updated"
    assert item._event == "webhook-source-event-datasource-updated"
    assert item.event == "datasource-updated"


def test_event_setter_new_style_event_name():
    """New-style event names (webhook-event-*) should be stored as-is and not mangled."""
    item = WebhookItem()
    item.event = "webhook-event-user-promoted-admin"
    assert item._event == "webhook-event-user-promoted-admin"
    assert item.event == "webhook-event-user-promoted-admin"


def test_get_new_style_event(server: TSC.Server) -> None:
    """Webhooks with new-style event names (webhook-event-*) should parse correctly."""
    response_xml = GET_NEW_EVENT_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.webhooks.baseurl, text=response_xml)
        webhooks, _ = server.webhooks.get()
        assert len(webhooks) == 1
        webhook = webhooks[0]

        assert webhook.id == "webhook-id-2"
        assert webhook.name == "webhook-name-2"
        assert webhook.url == "https://example.com/hook"
        # New-style event name should not have the webhook-source-event- prefix stripped
        assert webhook.event == "webhook-event-user-promoted-admin"
        assert webhook.owner_id == "webhook_owner_luid"


def test_create_with_short_event_name(server: TSC.Server) -> None:
    """Creating a webhook with a short event name (e.g. datasource-created) should work."""
    response_xml = CREATE_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.webhooks.baseurl, text=response_xml)
        webhook_model = TSC.WebhookItem()
        webhook_model.name = "Test Webhook"
        webhook_model.url = "https://ifttt.com/maker-url"
        webhook_model.event = "datasource-created"

        new_webhook = server.webhooks.create(webhook_model)
        assert new_webhook.id is not None


def test_create_with_source_event_name(server: TSC.Server) -> None:
    """Creating a webhook with a full webhook-source-event-* name should work."""
    response_xml = CREATE_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.webhooks.baseurl, text=response_xml)
        webhook_model = TSC.WebhookItem()
        webhook_model.name = "Test Webhook"
        webhook_model.url = "https://ifttt.com/maker-url"
        webhook_model.event = "webhook-source-event-datasource-created"

        new_webhook = server.webhooks.create(webhook_model)
        assert new_webhook.id is not None
