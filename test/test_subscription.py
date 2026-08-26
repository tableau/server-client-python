from datetime import timedelta
from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

CREATE_XML = TEST_ASSET_DIR / "subscription_create.xml"
GET_XML = TEST_ASSET_DIR / "subscription_get.xml"
GET_XML_BY_ID = TEST_ASSET_DIR / "subscription_get_by_id.xml"
GET_XML_CLOUD = TEST_ASSET_DIR / "subscription_get_cloud.xml"
GET_XML_CLOUD_NO_FREQ_DETAILS = TEST_ASSET_DIR / "subscription_get_cloud_no_frequency_details.xml"
GET_XML_CLOUD_EMPTY_INTERVALS = TEST_ASSET_DIR / "subscription_get_cloud_empty_intervals.xml"
GET_XML_CLOUD_BAD_HOURS = TEST_ASSET_DIR / "subscription_get_cloud_bad_hours.xml"


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
    # Server shape also populates the structured schedule attribute with id + name.
    assert subscription.schedule is not None
    assert "7617c389-cdca-4940-a66e-69956fcebf3e" == subscription.schedule.id
    assert "Subscribe daily [00:00 - 04:00, Pacific US] [migrated at 1490824351877]" == subscription.schedule.name
    assert subscription.schedule.frequency is None  # server referenced-schedule shape has no frequency

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
    # Server shape also populates the structured schedule attribute for the second subscription.
    assert subscription.schedule is not None
    assert "3407cd38-7b39-4983-86a6-67a1506a5e3f" == subscription.schedule.id
    assert "SSS_27212a85-6b28-41f6-8c69-29b02043d7a5" == subscription.schedule.name
    assert subscription.schedule.frequency is None  # server referenced-schedule shape has no frequency
    assert subscription.schedule.interval_item is None  # no <frequencyDetails> in a Server reference


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
    # get_by_id also parses the structured schedule attribute on the Server referenced-schedule shape.
    assert subscription.schedule is not None
    assert "7617c389-cdca-4940-a66e-69956fcebf3e" == subscription.schedule.id
    assert "Subscribe daily [00:00 - 04:00, Pacific US] [migrated at 1490824351877]" == subscription.schedule.name
    assert subscription.schedule.frequency is None
    assert subscription.schedule.interval_item is None


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


def test_get_subscriptions_cloud_inline_schedule(server: TSC.Server) -> None:
    """Tableau Cloud inlines the schedule into <subscription> without an id.

    See github.com/tableau/server-client-python/issues/1627 -- the previous
    parser silently dropped everything about the schedule on Cloud responses,
    so ``sub.schedule_id`` was always None and there was no structured way to
    read the inlined frequency / next-run / intervals. This test locks in that
    ``schedule_id`` remains None (unavoidable -- the API doesn't send one) but
    the structured ``schedule`` attribute is populated with the inlined data.
    """
    response_xml = GET_XML_CLOUD.read_text()
    with requests_mock.mock() as m:
        m.get(server.subscriptions.baseurl, text=response_xml)
        all_subscriptions, pagination_item = server.subscriptions.get()

    assert 1 == pagination_item.total_available
    subscription = all_subscriptions[0]
    assert "df1c0a85-1234-4b6f-a2c4-1234567890ab" == subscription.id
    assert "Cloud daily digest" == subscription.subject
    assert "bbbb1111-2222-3333-4444-555555555555" == subscription.user_id
    assert "View" == subscription.target.type

    # schedule_id is unavoidably None on Cloud -- the API does not send one for
    # inlined schedules. Callers filtering by schedule_id must switch to
    # subscription.schedule for Cloud parity.
    assert subscription.schedule_id is None

    assert subscription.schedule is not None
    assert subscription.schedule.id is None  # inlined -- no referenceable id
    assert "Daily" == subscription.schedule.frequency
    assert subscription.schedule.next_run_at is not None
    assert 2026 == subscription.schedule.next_run_at.year
    assert 8 == subscription.schedule.next_run_at.month
    assert 29 == subscription.schedule.next_run_at.day

    # The Cloud path deliberately preserves the ``-0700`` offset that came off
    # the wire rather than normalising to UTC. A future regression to
    # ``.replace(tzinfo=utc)`` after ``strptime`` would silently shift the
    # instant by seven hours -- lock the non-UTC offset in here.
    assert timedelta(hours=-7) == subscription.schedule.next_run_at.utcoffset()

    # <frequencyDetails> nested <intervals> parsed into a DailyInterval carrying
    # the (hours, weekDay) pairs from the XML.
    interval_item = subscription.schedule.interval_item
    assert interval_item is not None
    assert len(interval_item.interval) >= 1
    # The two <interval> children map to (24.0, 'Saturday'). ``24 == 24.0`` so
    # the numeric equality holds regardless of int/float representation.
    assert 24 in interval_item.interval
    assert "Saturday" in interval_item.interval


def test_get_subscriptions_cloud_no_frequency_details(server: TSC.Server) -> None:
    """Cloud sometimes returns ``<schedule>`` without any ``<frequencyDetails>`` child.

    Before B2 landed this crashed the whole ``subscriptions.get()`` call with
    ``TypeError: strptime() argument 1 must be str, not None``. It should now
    degrade to ``interval_item = None`` while ``frequency`` and ``next_run_at``
    remain populated.
    """
    response_xml = GET_XML_CLOUD_NO_FREQ_DETAILS.read_text()
    with requests_mock.mock() as m:
        m.get(server.subscriptions.baseurl, text=response_xml)
        all_subscriptions, _ = server.subscriptions.get()

    subscription = all_subscriptions[0]
    assert subscription.schedule is not None
    assert "Daily" == subscription.schedule.frequency
    assert subscription.schedule.next_run_at is not None
    assert subscription.schedule.interval_item is None


def test_get_subscriptions_cloud_malformed_interval(server: TSC.Server) -> None:
    """A single malformed ``<interval hours="3"/>`` used to poison the whole page.

    ``IntervalItem`` validates against a fixed ``VALID_INTERVALS`` set that
    rejects ``3`` as an hourly interval; that ``ValueError`` used to escape
    ``_parse_element`` and abort the entire subscription list. B3 catches it
    per-schedule so the malformed subscription degrades to
    ``interval_item = None`` and its healthy siblings still parse.
    """
    response_xml = GET_XML_CLOUD_BAD_HOURS.read_text()
    with requests_mock.mock() as m:
        m.get(server.subscriptions.baseurl, text=response_xml)
        all_subscriptions, _ = server.subscriptions.get()

    assert 2 == len(all_subscriptions)
    malformed = all_subscriptions[0]
    healthy = all_subscriptions[1]

    assert malformed.schedule is not None
    assert "Daily" == malformed.schedule.frequency
    assert malformed.schedule.next_run_at is not None
    # ``hours="3"`` is not in DailyInterval.VALID_INTERVALS -- degrade to None.
    assert malformed.schedule.interval_item is None

    # Sibling with a valid ``hours="24"`` still parses.
    assert healthy.schedule is not None
    assert healthy.schedule.interval_item is not None
    assert 24 in healthy.schedule.interval_item.interval


def test_get_subscriptions_cloud_empty_intervals(server: TSC.Server) -> None:
    """An empty ``<intervals/>`` element parses to an interval item with no children.

    ``DailyInterval`` accepts an empty interval tuple (nothing to validate against
    ``VALID_INTERVALS``) -- so this stays populated with an ``interval_item``
    whose ``.interval`` is empty rather than degrading to ``None``.
    """
    response_xml = GET_XML_CLOUD_EMPTY_INTERVALS.read_text()
    with requests_mock.mock() as m:
        m.get(server.subscriptions.baseurl, text=response_xml)
        all_subscriptions, _ = server.subscriptions.get()

    subscription = all_subscriptions[0]
    assert subscription.schedule is not None
    assert "Daily" == subscription.schedule.frequency
    assert subscription.schedule.interval_item is not None
    assert () == tuple(subscription.schedule.interval_item.interval)
