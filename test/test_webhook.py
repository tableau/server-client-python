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
UPDATE_XML = TEST_ASSET_DIR / "webhook_update.xml"


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


def test_event_setter_none() -> None:
    """Setting event to None should store None without crashing."""
    item = WebhookItem()
    item.event = "datasource-updated"
    assert item.event == "datasource-updated"
    item.event = None
    assert item._event is None
    assert item.event is None


def test_event_setter_short_name() -> None:
    """Short event names should be stored with the webhook-source-event- prefix."""
    item = WebhookItem()
    item.event = "datasource-updated"
    assert item._event == "webhook-source-event-datasource-updated"
    assert item.event == "datasource-updated"


def test_event_setter_full_source_name() -> None:
    """Full webhook-source-event- names should be accepted and stored as-is."""
    item = WebhookItem()
    item.event = "webhook-source-event-datasource-updated"
    assert item._event == "webhook-source-event-datasource-updated"
    assert item.event == "datasource-updated"


def test_event_setter_new_style_event_name() -> None:
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


def test_get_parses_is_enabled_and_status_change_reason(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.webhooks.baseurl + "/webhook-id", text=response_xml)
        webhook = server.webhooks.get_by_id("webhook-id")

        assert webhook.is_enabled is True
        assert webhook.status_change_reason == ""
        assert webhook.name == "webhook-name-updated"
        assert webhook.url == "https://updated-url.example.com/hook"


def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.webhooks.baseurl + "/webhook-id", text=response_xml)
        webhook_item = WebhookItem()
        webhook_item._set_values(
            "webhook-id", "webhook-name-updated", "https://updated-url.example.com/hook", "datasource-created", None
        )
        webhook_item.is_enabled = True

        updated_webhook = server.webhooks.update(webhook_item)

        assert updated_webhook.id == "webhook-id"
        assert updated_webhook.name == "webhook-name-updated"
        assert updated_webhook.url == "https://updated-url.example.com/hook"
        assert updated_webhook.is_enabled is True


def test_update_missing_id(server: TSC.Server) -> None:
    webhook_item = WebhookItem()
    webhook_item.name = "some-webhook"
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.webhooks.update(webhook_item)


def test_update_preserves_locally_set_fields_omitted_by_server(server: TSC.Server) -> None:
    """update should preserve locally-set fields that the server response omits.

    Matches the pattern used by users_endpoint.update and datasources_endpoint.update:
    fields set on the input item should survive when the server returns a partial
    response.
    """
    # Server response omits is_enabled, owner, and url; only id and name are returned.
    partial_response = (
        "<?xml version='1.0' encoding='UTF-8'?>"
        '<tsResponse xmlns="http://tableau.com/api">'
        '  <webhook id="webhook-id" name="webhook-name-updated">'
        "    <webhook-source>"
        "      <webhook-source-event-datasource-created />"
        "    </webhook-source>"
        "  </webhook>"
        "</tsResponse>"
    )
    with requests_mock.mock() as m:
        m.put(server.webhooks.baseurl + "/webhook-id", text=partial_response)
        webhook_item = WebhookItem()
        webhook_item._set_values(
            "webhook-id",
            "webhook-name-original",
            "https://local-url.example.com/hook",
            "datasource-created",
            "local-owner-luid",
        )
        webhook_item.is_enabled = False

        updated_webhook = server.webhooks.update(webhook_item)

        # Fields returned by the server should be updated.
        assert updated_webhook.name == "webhook-name-updated"
        # Fields omitted by the server should retain their locally-set values.
        assert updated_webhook.url == "https://local-url.example.com/hook"
        assert updated_webhook.owner_id == "local-owner-luid"
        assert updated_webhook.is_enabled is False


def test_update_request_factory_is_enabled() -> None:
    webhook_item = WebhookItem()
    webhook_item._set_values(
        "webhook-id", "webhook-name", "https://example.com/hook", "datasource-created", None, is_enabled=False
    )

    request_bytes = RequestFactory.Webhook.update_req(webhook_item)
    request_str = request_bytes.decode("utf-8")

    assert 'isEnabled="false"' in request_str
    assert "webhook-name" in request_str


def test_update_request_factory_url_and_event() -> None:
    """update_req should serialize url and event into the request body."""
    webhook_item = WebhookItem()
    webhook_item._set_values("webhook-id", "webhook-name", "https://example.com/hook", "datasource-created", None)

    request_bytes = RequestFactory.Webhook.update_req(webhook_item)
    request_str = request_bytes.decode("utf-8")

    assert "https://example.com/hook" in request_str
    assert "webhook-source-event-datasource-created" in request_str
    assert 'method="POST"' in request_str


def test_update_request_factory_partial_update_name_only() -> None:
    """update_req with only name set should omit url, event, and isEnabled."""
    webhook_item = WebhookItem()
    webhook_item.name = "new-name"

    request_bytes = RequestFactory.Webhook.update_req(webhook_item)
    request_str = request_bytes.decode("utf-8")

    assert "new-name" in request_str
    assert "isEnabled" not in request_str
    assert "webhook-source" not in request_str
    assert "webhook-destination" not in request_str


def test_update_request_factory_omits_is_enabled_when_none() -> None:
    """update_req should not emit isEnabled when is_enabled is None."""
    webhook_item = WebhookItem()
    webhook_item._set_values("webhook-id", "webhook-name", "https://example.com/hook", "datasource-created", None)
    # is_enabled is None by default

    request_bytes = RequestFactory.Webhook.update_req(webhook_item)
    request_str = request_bytes.decode("utf-8")

    assert "isEnabled" not in request_str


def test_parse_is_enabled_false() -> None:
    """isEnabled='false' in XML should parse to boolean False."""
    xml = (
        b"<?xml version='1.0' encoding='UTF-8'?>"
        b'<tsResponse xmlns="http://tableau.com/api">'
        b'  <webhook id="wh-1" name="wh" isEnabled="false">'
        b"    <webhook-source><webhook-source-event-datasource-created /></webhook-source>"
        b'    <webhook-destination><webhook-destination-http method="POST" url="https://x.example.com/h"/>'
        b"    </webhook-destination>"
        b"  </webhook>"
        b"</tsResponse>"
    )
    ns = {"t": "http://tableau.com/api"}
    webhooks = WebhookItem.from_response(xml, ns)
    assert len(webhooks) == 1
    assert webhooks[0].is_enabled is False
