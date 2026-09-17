from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

CREATE_XML = TEST_ASSET_DIR / "subscription_create.xml"
GET_XML = TEST_ASSET_DIR / "subscription_get.xml"
GET_XML_BY_ID = TEST_ASSET_DIR / "subscription_get_by_id.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "2.6"

    return server


def test_get_subscriptions(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.subscriptions.baseurl, text=response_xml)
        all_subscriptions, pagination_item = server.subscriptions.get()

    assert 2 == pagination_item.total_available
    subscription = all_subscriptions[0]
    assert "382e9a6e-0c08-4a95-b6c1-c14df7bac3e4" == subscription.id
    assert "NOT FOUND!" == subscription.message
    assert subscription.attach_image is True
    assert subscription.attach_pdf is False
    assert subscription.suspended is False
    assert subscription.send_if_view_empty is False
    assert subscription.page_orientation is None
    assert subscription.page_size_option is None
    assert "Not Found Alert" == subscription.subject
    assert "cdd716ca-5818-470e-8bec-086885dbadee" == subscription.target.id
    assert "View" == subscription.target.type
    assert "c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e" == subscription.user_id
    assert "7617c389-cdca-4940-a66e-69956fcebf3e" == subscription.schedule_id

    subscription = all_subscriptions[1]
    assert "23cb7630-afc8-4c8e-b6cd-83ae0322ec66" == subscription.id
    assert "overview" == subscription.message
    assert subscription.attach_image is False
    assert subscription.attach_pdf is True
    assert subscription.suspended is True
    assert subscription.send_if_view_empty is True
    assert "PORTRAIT" == subscription.page_orientation
    assert "A5" == subscription.page_size_option
    assert "Last 7 Days" == subscription.subject
    assert "2e6b4e8f-22dd-4061-8f75-bf33703da7e5" == subscription.target.id
    assert "Workbook" == subscription.target.type
    assert "c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e" == subscription.user_id
    assert "3407cd38-7b39-4983-86a6-67a1506a5e3f" == subscription.schedule_id


def test_get_subscription_by_id(server: TSC.Server) -> None:
    response_xml = GET_XML_BY_ID.read_text()
    with requests_mock.mock() as m:
        m.get(server.subscriptions.baseurl + "/382e9a6e-0c08-4a95-b6c1-c14df7bac3e4", text=response_xml)
        subscription = server.subscriptions.get_by_id("382e9a6e-0c08-4a95-b6c1-c14df7bac3e4")

    assert "382e9a6e-0c08-4a95-b6c1-c14df7bac3e4" == subscription.id
    assert "View" == subscription.target.type
    assert "cdd716ca-5818-470e-8bec-086885dbadee" == subscription.target.id
    assert "c0d5fc44-ad8c-4957-bec0-b70ed0f8df1e" == subscription.user_id
    assert "Not Found Alert" == subscription.subject
    assert "7617c389-cdca-4940-a66e-69956fcebf3e" == subscription.schedule_id


def test_create_subscription(server: TSC.Server) -> None:
    response_xml = CREATE_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.subscriptions.baseurl, text=response_xml)

        target_item = TSC.Target("960e61f2-1838-40b2-bba2-340c9492f943", "workbook")
        new_subscription = TSC.SubscriptionItem(
            "subject", "4906c453-d5ec-4972-9ff4-789b629bdfa2", "8d30c8de-0a5f-4bee-b266-c621b4f3eed0", target_item
        )
        new_subscription = server.subscriptions.create(new_subscription)

    assert "78e9318d-2d29-4d67-b60f-3f2f5fd89ecc" == new_subscription.id
    assert "sub_name" == new_subscription.subject
    assert "960e61f2-1838-40b2-bba2-340c9492f943" == new_subscription.target.id
    assert "Workbook" == new_subscription.target.type
    assert "4906c453-d5ec-4972-9ff4-789b629bdfa2" == new_subscription.schedule_id
    assert "8d30c8de-0a5f-4bee-b266-c621b4f3eed0" == new_subscription.user_id


def test_delete_subscription(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.subscriptions.baseurl + "/78e9318d-2d29-4d67-b60f-3f2f5fd89ecc", status_code=204)
        server.subscriptions.delete("78e9318d-2d29-4d67-b60f-3f2f5fd89ecc")
