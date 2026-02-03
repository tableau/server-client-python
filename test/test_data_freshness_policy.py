from pathlib import Path
import requests_mock

import pytest

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

UPDATE_DFP_ALWAYS_LIVE_XML = TEST_ASSET_DIR / "workbook_update_data_freshness_policy.xml"
UPDATE_DFP_SITE_DEFAULT_XML = TEST_ASSET_DIR / "workbook_update_data_freshness_policy2.xml"
UPDATE_DFP_FRESH_EVERY_XML = TEST_ASSET_DIR / "workbook_update_data_freshness_policy3.xml"
UPDATE_DFP_FRESH_AT_DAILY_XML = TEST_ASSET_DIR / "workbook_update_data_freshness_policy4.xml"
UPDATE_DFP_FRESH_AT_WEEKLY_XML = TEST_ASSET_DIR / "workbook_update_data_freshness_policy5.xml"
UPDATE_DFP_FRESH_AT_MONTHLY_XML = TEST_ASSET_DIR / "workbook_update_data_freshness_policy6.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    server = TSC.Server("http://test", False)
    # Fake sign in
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_update_DFP_always_live(server) -> None:
    response_xml = UPDATE_DFP_ALWAYS_LIVE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
            TSC.DataFreshnessPolicyItem.Option.AlwaysLive
        )
        single_workbook = server.workbooks.update(single_workbook)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert "AlwaysLive" == single_workbook.data_freshness_policy.option


def test_update_DFP_site_default(server) -> None:
    response_xml = UPDATE_DFP_SITE_DEFAULT_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
            TSC.DataFreshnessPolicyItem.Option.SiteDefault
        )
        single_workbook = server.workbooks.update(single_workbook)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert "SiteDefault" == single_workbook.data_freshness_policy.option


def test_update_DFP_fresh_every(server) -> None:
    response_xml = UPDATE_DFP_FRESH_EVERY_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
            TSC.DataFreshnessPolicyItem.Option.FreshEvery
        )
        fresh_every_ten_hours = TSC.DataFreshnessPolicyItem.FreshEvery(
            TSC.DataFreshnessPolicyItem.FreshEvery.Frequency.Hours, 10
        )
        single_workbook.data_freshness_policy.fresh_every_schedule = fresh_every_ten_hours
        single_workbook = server.workbooks.update(single_workbook)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert "FreshEvery" == single_workbook.data_freshness_policy.option
    assert "Hours" == single_workbook.data_freshness_policy.fresh_every_schedule.frequency
    assert 10 == single_workbook.data_freshness_policy.fresh_every_schedule.value


def test_update_DFP_fresh_every_missing_attributes(server) -> None:
    response_xml = UPDATE_DFP_FRESH_EVERY_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
            TSC.DataFreshnessPolicyItem.Option.FreshEvery
        )

    with pytest.raises(ValueError):
        server.workbooks.update(single_workbook)


def test_update_DFP_fresh_at_day(server) -> None:
    response_xml = UPDATE_DFP_FRESH_AT_DAILY_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.FreshAt)
        fresh_at_10pm_daily = TSC.DataFreshnessPolicyItem.FreshAt(
            TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Day, "22:00:00", " Asia/Singapore"
        )
        single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_10pm_daily
        single_workbook = server.workbooks.update(single_workbook)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert "FreshAt" == single_workbook.data_freshness_policy.option
    assert "Day" == single_workbook.data_freshness_policy.fresh_at_schedule.frequency
    assert "22:00:00" == single_workbook.data_freshness_policy.fresh_at_schedule.time
    assert "Asia/Singapore" == single_workbook.data_freshness_policy.fresh_at_schedule.timezone


def test_update_DFP_fresh_at_week(server) -> None:
    response_xml = UPDATE_DFP_FRESH_AT_WEEKLY_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.FreshAt)
        fresh_at_10am_mon_wed = TSC.DataFreshnessPolicyItem.FreshAt(
            TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Week,
            "10:00:00",
            "America/Los_Angeles",
            ["Monday", "Wednesday"],
        )
        single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_10am_mon_wed
        single_workbook = server.workbooks.update(single_workbook)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert "FreshAt" == single_workbook.data_freshness_policy.option
    assert "Week" == single_workbook.data_freshness_policy.fresh_at_schedule.frequency
    assert "10:00:00" == single_workbook.data_freshness_policy.fresh_at_schedule.time
    assert "Wednesday" == single_workbook.data_freshness_policy.fresh_at_schedule.interval_item[0]
    assert "Monday" == single_workbook.data_freshness_policy.fresh_at_schedule.interval_item[1]


def test_update_DFP_fresh_at_month(server) -> None:
    response_xml = UPDATE_DFP_FRESH_AT_MONTHLY_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.FreshAt)
        fresh_at_00am_lastDayOfMonth = TSC.DataFreshnessPolicyItem.FreshAt(
            TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Month, "00:00:00", "America/Los_Angeles", ["LastDay"]
        )
        single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_00am_lastDayOfMonth
        single_workbook = server.workbooks.update(single_workbook)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert "FreshAt" == single_workbook.data_freshness_policy.option
    assert "Month" == single_workbook.data_freshness_policy.fresh_at_schedule.frequency
    assert "00:00:00" == single_workbook.data_freshness_policy.fresh_at_schedule.time
    assert "LastDay" == single_workbook.data_freshness_policy.fresh_at_schedule.interval_item[0]


def test_update_DFP_fresh_at_missing_params(server) -> None:
    response_xml = UPDATE_DFP_FRESH_AT_DAILY_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.FreshAt)

    with pytest.raises(ValueError):
        server.workbooks.update(single_workbook)


def test_update_DFP_fresh_at_missing_interval(server) -> None:
    response_xml = UPDATE_DFP_FRESH_AT_DAILY_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(TSC.DataFreshnessPolicyItem.Option.FreshAt)
        fresh_at_month_no_interval = TSC.DataFreshnessPolicyItem.FreshAt(
            TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Month, "00:00:00", "America/Los_Angeles"
        )
        single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_month_no_interval

    with pytest.raises(ValueError):
        server.workbooks.update(single_workbook)
