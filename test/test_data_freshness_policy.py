import os
import requests_mock
import unittest

import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

UPDATE_DFP_ALWAYS_LIVE_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_data_freshness_policy.xml")
UPDATE_DFP_SITE_DEFAULT_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_data_freshness_policy2.xml")
UPDATE_DFP_FRESH_EVERY_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_data_freshness_policy3.xml")
UPDATE_DFP_FRESH_AT_DAILY_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_data_freshness_policy4.xml")
UPDATE_DFP_FRESH_AT_WEEKLY_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_data_freshness_policy5.xml")
UPDATE_DFP_FRESH_AT_MONTHLY_XML = os.path.join(TEST_ASSET_DIR, "workbook_update_data_freshness_policy6.xml")


class WorkbookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.workbooks.baseurl

    def test_update_DFP_always_live(self) -> None:
        with open(UPDATE_DFP_ALWAYS_LIVE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.AlwaysLive
            )
            single_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual("AlwaysLive", single_workbook.data_freshness_policy.option)

    def test_update_DFP_site_default(self) -> None:
        with open(UPDATE_DFP_SITE_DEFAULT_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.SiteDefault
            )
            single_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual("SiteDefault", single_workbook.data_freshness_policy.option)

    def test_update_DFP_fresh_every(self) -> None:
        with open(UPDATE_DFP_FRESH_EVERY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshEvery
            )
            fresh_every_ten_hours = TSC.DataFreshnessPolicyItem.FreshEvery(
                TSC.DataFreshnessPolicyItem.FreshEvery.Frequency.Hours, 10
            )
            single_workbook.data_freshness_policy.fresh_every_schedule = fresh_every_ten_hours
            single_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual("FreshEvery", single_workbook.data_freshness_policy.option)
        self.assertEqual("Hours", single_workbook.data_freshness_policy.fresh_every_schedule.frequency)
        self.assertEqual(10, single_workbook.data_freshness_policy.fresh_every_schedule.value)

    def test_update_DFP_fresh_every_missing_attributes(self) -> None:
        with open(UPDATE_DFP_FRESH_EVERY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshEvery
            )

        self.assertRaises(ValueError, self.server.workbooks.update, single_workbook)

    def test_update_DFP_fresh_at_day(self) -> None:
        with open(UPDATE_DFP_FRESH_AT_DAILY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshAt
            )
            fresh_at_10pm_daily = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Day, "22:00:00", " Asia/Singapore"
            )
            single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_10pm_daily
            single_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual("FreshAt", single_workbook.data_freshness_policy.option)
        self.assertEqual("Day", single_workbook.data_freshness_policy.fresh_at_schedule.frequency)
        self.assertEqual("22:00:00", single_workbook.data_freshness_policy.fresh_at_schedule.time)
        self.assertEqual("Asia/Singapore", single_workbook.data_freshness_policy.fresh_at_schedule.timezone)

    def test_update_DFP_fresh_at_week(self) -> None:
        with open(UPDATE_DFP_FRESH_AT_WEEKLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshAt
            )
            fresh_at_10am_mon_wed = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Week,
                "10:00:00",
                "America/Los_Angeles",
                ["Monday", "Wednesday"],
            )
            single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_10am_mon_wed
            single_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual("FreshAt", single_workbook.data_freshness_policy.option)
        self.assertEqual("Week", single_workbook.data_freshness_policy.fresh_at_schedule.frequency)
        self.assertEqual("10:00:00", single_workbook.data_freshness_policy.fresh_at_schedule.time)
        self.assertEqual("Wednesday", single_workbook.data_freshness_policy.fresh_at_schedule.interval_item[0])
        self.assertEqual("Monday", single_workbook.data_freshness_policy.fresh_at_schedule.interval_item[1])

    def test_update_DFP_fresh_at_month(self) -> None:
        with open(UPDATE_DFP_FRESH_AT_MONTHLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshAt
            )
            fresh_at_00am_lastDayOfMonth = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Month, "00:00:00", "America/Los_Angeles", ["LastDay"]
            )
            single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_00am_lastDayOfMonth
            single_workbook = self.server.workbooks.update(single_workbook)

        self.assertEqual("1f951daf-4061-451a-9df1-69a8062664f2", single_workbook.id)
        self.assertEqual("FreshAt", single_workbook.data_freshness_policy.option)
        self.assertEqual("Month", single_workbook.data_freshness_policy.fresh_at_schedule.frequency)
        self.assertEqual("00:00:00", single_workbook.data_freshness_policy.fresh_at_schedule.time)
        self.assertEqual("LastDay", single_workbook.data_freshness_policy.fresh_at_schedule.interval_item[0])

    def test_update_DFP_fresh_at_missing_params(self) -> None:
        with open(UPDATE_DFP_FRESH_AT_DAILY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshAt
            )

        self.assertRaises(ValueError, self.server.workbooks.update, single_workbook)

    def test_update_DFP_fresh_at_missing_interval(self) -> None:
        with open(UPDATE_DFP_FRESH_AT_DAILY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
            single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
            single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
            single_workbook.data_freshness_policy = TSC.DataFreshnessPolicyItem(
                TSC.DataFreshnessPolicyItem.Option.FreshAt
            )
            fresh_at_month_no_interval = TSC.DataFreshnessPolicyItem.FreshAt(
                TSC.DataFreshnessPolicyItem.FreshAt.Frequency.Month, "00:00:00", "America/Los_Angeles"
            )
            single_workbook.data_freshness_policy.fresh_at_schedule = fresh_at_month_no_interval

        self.assertRaises(ValueError, self.server.workbooks.update, single_workbook)
