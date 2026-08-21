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


# -----------------------------------------------------------------
# refresh_extract_triggered (aka "On Extract Refresh" subscriptions)
# -----------------------------------------------------------------


def test_create_rejects_none_schedule_id(server: TSC.Server) -> None:
    """Regression for tableau/server-client-python#1658: users trying to create
    an 'On Extract Refresh' subscription would pass schedule_id=None. Point them
    at on_extract_refresh() instead of letting the failure surface deep in
    the wire layer as a ServerResponseError. The check lives in create() (not
    __init__) so parse can still build items from server responses that use
    the inline-schedule form (no schedule id on the wire).
    """
    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem("subject", None, "user-id", target)
    with pytest.raises(ValueError, match="on_extract_refresh"):
        server.subscriptions.create(sub)


def test_create_rejects_empty_schedule_id(server: TSC.Server) -> None:
    """Same failure mode as None: an empty-string schedule_id would serialize
    as <schedule id=""/> and hit a confusing server error.
    """
    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem("subject", "", "user-id", target)
    with pytest.raises(ValueError, match="on_extract_refresh"):
        server.subscriptions.create(sub)


def test_subscription_defaults_refresh_extract_triggered_false(server: TSC.Server) -> None:
    """A default SubscriptionItem does not opt into extract-refresh triggering."""
    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem("subject", "sched-id", "user-id", target)
    assert sub.refresh_extract_triggered is False


def test_on_extract_refresh_factory_sets_flag(server: TSC.Server) -> None:
    """The on_extract_refresh factory produces a subscription with the flag set
    and the extract-refresh schedule id in place -- server rejects a payload
    that has the flag without a schedule reference, so both must be set together.
    """
    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem.on_extract_refresh(
        subject="On refresh",
        extract_refresh_schedule_id="refresh-sched-id",
        user_id="user-id",
        target=target,
    )
    assert sub.refresh_extract_triggered is True
    assert sub.schedule_id == "refresh-sched-id"
    assert sub.subject == "On refresh"
    assert sub.user_id == "user-id"
    assert sub.target is target


def test_create_req_emits_refresh_extract_triggered_when_set(server: TSC.Server) -> None:
    """When the flag is set, the outbound XML should carry
    refreshExtractTriggered='true' on the <subscription> element.
    """
    from tableauserverclient.server.request_factory import RequestFactory

    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem.on_extract_refresh(
        subject="On refresh",
        extract_refresh_schedule_id="refresh-sched-id",
        user_id="user-id",
        target=target,
    )
    body = RequestFactory.Subscription.create_req(sub).decode("utf-8")
    assert 'refreshExtractTriggered="true"' in body


def test_create_req_omits_refresh_extract_triggered_when_false(server: TSC.Server) -> None:
    """A default subscription must not emit refreshExtractTriggered=false. Some
    servers treat absence and False differently; we send only when the caller
    has explicitly opted in.
    """
    from tableauserverclient.server.request_factory import RequestFactory

    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem("subject", "sched-id", "user-id", target)
    body = RequestFactory.Subscription.create_req(sub).decode("utf-8")
    assert "refreshExtractTriggered" not in body


def test_parse_response_reads_refresh_extract_triggered(server: TSC.Server) -> None:
    """A subscription XML element carrying refreshExtractTriggered='true'
    parses back into refresh_extract_triggered=True on the SubscriptionItem.
    """
    xml = (
        b'<tsResponse xmlns="http://tableau.com/api">'
        b"  <subscriptions>"
        b'    <subscription id="sub-1" subject="On refresh" attachImage="true" attachPdf="false"'
        b'                  suspended="false" refreshExtractTriggered="true">'
        b'      <content id="view-1" type="View" sendIfViewEmpty="false" />'
        b'      <schedule id="refresh-sched-1" name="Nightly refresh" />'
        b'      <user id="user-1" />'
        b"    </subscription>"
        b"  </subscriptions>"
        b"</tsResponse>"
    )
    subs = TSC.SubscriptionItem.from_response(xml, {"t": "http://tableau.com/api"})
    assert len(subs) == 1
    assert subs[0].refresh_extract_triggered is True
    assert subs[0].schedule_id == "refresh-sched-1"


def test_update_rejects_missing_schedule_id(server: TSC.Server) -> None:
    """A subscription round-tripped from an inline-schedule response has
    schedule_id=None. Calling update() on it would send <schedule/> with no id
    and hit a confusing wire-layer error. Catch it at the endpoint instead.
    """
    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem("subject", "sched-id", "user-id", target)
    sub._id = "existing-sub-id"  # type: ignore[assignment]
    sub.schedule_id = None
    with pytest.raises(ValueError, match="schedule_id is required"):
        server.subscriptions.update(sub)


def test_update_req_emits_refresh_extract_triggered_when_true(server: TSC.Server) -> None:
    """When the flag is True, update_req must emit refreshExtractTriggered='true'."""
    from tableauserverclient.server.request_factory import RequestFactory

    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem.on_extract_refresh(
        subject="On refresh",
        extract_refresh_schedule_id="refresh-sched-id",
        user_id="user-id",
        target=target,
    )
    body = RequestFactory.Subscription.update_req(sub).decode("utf-8")
    assert 'refreshExtractTriggered="true"' in body


def test_update_req_emits_refresh_extract_triggered_when_false(server: TSC.Server) -> None:
    """update_req must emit refreshExtractTriggered='false' so callers can turn
    the flag off. The server retains the prior value when the attribute is
    absent, so omission would silently prevent True -> False transitions.
    """
    from tableauserverclient.server.request_factory import RequestFactory

    target = TSC.Target("view-id", "view")
    sub = TSC.SubscriptionItem("subject", "sched-id", "user-id", target)
    assert sub.refresh_extract_triggered is False
    body = RequestFactory.Subscription.update_req(sub).decode("utf-8")
    assert 'refreshExtractTriggered="false"' in body


def test_parse_response_with_inline_schedule_no_id(server: TSC.Server) -> None:
    """Regression: on Cloud/TOL the server may return a <schedule> element with
    no id attribute (the full schedule is inlined instead). Parse must handle
    this without raising -- the constructor cannot demand a schedule_id here.
    """
    xml = (
        b'<tsResponse xmlns="http://tableau.com/api">'
        b"  <subscriptions>"
        b'    <subscription id="sub-3" subject="TOL sub" attachImage="true" attachPdf="false" suspended="false">'
        b'      <content id="view-3" type="View" sendIfViewEmpty="false" />'
        b'      <schedule name="Nightly refresh" frequency="Daily">'
        b'        <frequencyDetails start="02:00:00" />'
        b"      </schedule>"
        b'      <user id="user-3" />'
        b"    </subscription>"
        b"  </subscriptions>"
        b"</tsResponse>"
    )
    subs = TSC.SubscriptionItem.from_response(xml, {"t": "http://tableau.com/api"})
    assert len(subs) == 1
    assert subs[0].schedule_id is None
    assert subs[0].schedule is not None


def test_parse_response_missing_refresh_extract_triggered_defaults_false(server: TSC.Server) -> None:
    """Backward compatibility: a subscription XML element without the attribute
    parses back to refresh_extract_triggered=False.
    """
    xml = (
        b'<tsResponse xmlns="http://tableau.com/api">'
        b"  <subscriptions>"
        b'    <subscription id="sub-2" subject="Weekly" attachImage="true" attachPdf="false" suspended="false">'
        b'      <content id="view-2" type="View" sendIfViewEmpty="false" />'
        b'      <schedule id="weekly-sched" name="Weekly Monday" />'
        b'      <user id="user-2" />'
        b"    </subscription>"
        b"  </subscriptions>"
        b"</tsResponse>"
    )
    subs = TSC.SubscriptionItem.from_response(xml, {"t": "http://tableau.com/api"})
    assert len(subs) == 1
    assert subs[0].refresh_extract_triggered is False
