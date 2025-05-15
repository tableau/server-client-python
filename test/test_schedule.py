import os
import unittest
from datetime import time

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = os.path.join(TEST_ASSET_DIR, "schedule_get.xml")
GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_by_id.xml")
GET_HOURLY_ID_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_hourly_id.xml")
GET_DAILY_ID_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_daily_id.xml")
GET_MONTHLY_ID_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_monthly_id.xml")
GET_MONTHLY_ID_2_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_monthly_id_2.xml")
GET_EMPTY_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_empty.xml")
CREATE_HOURLY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_hourly.xml")
CREATE_DAILY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_daily.xml")
CREATE_WEEKLY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_weekly.xml")
CREATE_MONTHLY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_monthly.xml")
UPDATE_XML = os.path.join(TEST_ASSET_DIR, "schedule_update.xml")
ADD_WORKBOOK_TO_SCHEDULE = os.path.join(TEST_ASSET_DIR, "schedule_add_workbook.xml")
ADD_WORKBOOK_TO_SCHEDULE_WITH_WARNINGS = os.path.join(TEST_ASSET_DIR, "schedule_add_workbook_with_warnings.xml")
ADD_DATASOURCE_TO_SCHEDULE = os.path.join(TEST_ASSET_DIR, "schedule_add_datasource.xml")
ADD_FLOW_TO_SCHEDULE = os.path.join(TEST_ASSET_DIR, "schedule_add_flow.xml")

WORKBOOK_GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, "workbook_get_by_id.xml")
DATASOURCE_GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, "datasource_get_by_id.xml")
FLOW_GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, "flow_get_by_id.xml")


class ScheduleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake Signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.schedules.baseurl

    def test_get(self) -> None:
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_schedules, pagination_item = self.server.schedules.get()

        extract = all_schedules[0]
        subscription = all_schedules[1]
        flow = all_schedules[2]
        system = all_schedules[3]

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("c9cff7f9-309c-4361-99ff-d4ba8c9f5467", extract.id)
        self.assertEqual("Weekday early mornings", extract.name)
        self.assertEqual("Active", extract.state)
        self.assertEqual(50, extract.priority)
        self.assertEqual("2016-07-06T20:19:00Z", format_datetime(extract.created_at))
        self.assertEqual("2016-09-13T11:00:32Z", format_datetime(extract.updated_at))
        self.assertEqual("Extract", extract.schedule_type)
        self.assertEqual("2016-09-14T11:00:00Z", format_datetime(extract.next_run_at))

        self.assertEqual("bcb79d07-6e47-472f-8a65-d7f51f40c36c", subscription.id)
        self.assertEqual("Saturday night", subscription.name)
        self.assertEqual("Active", subscription.state)
        self.assertEqual(80, subscription.priority)
        self.assertEqual("2016-07-07T20:19:00Z", format_datetime(subscription.created_at))
        self.assertEqual("2016-09-12T16:39:38Z", format_datetime(subscription.updated_at))
        self.assertEqual("Subscription", subscription.schedule_type)
        self.assertEqual("2016-09-18T06:00:00Z", format_datetime(subscription.next_run_at))

        self.assertEqual("f456e8f2-aeb2-4a8e-b823-00b6f08640f0", flow.id)
        self.assertEqual("First of the month 1:00AM", flow.name)
        self.assertEqual("Active", flow.state)
        self.assertEqual(50, flow.priority)
        self.assertEqual("2019-02-19T18:52:19Z", format_datetime(flow.created_at))
        self.assertEqual("2019-02-19T18:55:51Z", format_datetime(flow.updated_at))
        self.assertEqual("Flow", flow.schedule_type)
        self.assertEqual("2019-03-01T09:00:00Z", format_datetime(flow.next_run_at))

        self.assertEqual("3cfa4713-ce7c-4fa7-aa2e-f752bfc8dd04", system.id)
        self.assertEqual("First of the month 2:00AM", system.name)
        self.assertEqual("Active", system.state)
        self.assertEqual(30, system.priority)
        self.assertEqual("2019-02-19T18:52:19Z", format_datetime(system.created_at))
        self.assertEqual("2019-02-19T18:55:51Z", format_datetime(system.updated_at))
        self.assertEqual("System", system.schedule_type)
        self.assertEqual("2019-03-01T09:00:00Z", format_datetime(system.next_run_at))

    def test_get_empty(self) -> None:
        with open(GET_EMPTY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_schedules, pagination_item = self.server.schedules.get()

        self.assertEqual(0, pagination_item.total_available)
        self.assertEqual([], all_schedules)

    def test_get_by_id(self) -> None:
        self.server.version = "3.8"
        with open(GET_BY_ID_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
            baseurl = f"{self.server.baseurl}/schedules/{schedule_id}"
            m.get(baseurl, text=response_xml)
            schedule = self.server.schedules.get_by_id(schedule_id)
            self.assertIsNotNone(schedule)
            self.assertEqual(schedule_id, schedule.id)
            self.assertEqual("Weekday early mornings", schedule.name)
            self.assertEqual("Active", schedule.state)

    def test_get_hourly_by_id(self) -> None:
        self.server.version = "3.8"
        with open(GET_HOURLY_ID_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
            baseurl = f"{self.server.baseurl}/schedules/{schedule_id}"
            m.get(baseurl, text=response_xml)
            schedule = self.server.schedules.get_by_id(schedule_id)
            self.assertIsNotNone(schedule)
            self.assertEqual(schedule_id, schedule.id)
            self.assertEqual("Hourly schedule", schedule.name)
            self.assertEqual("Active", schedule.state)
            self.assertEqual(("Monday", 0.5), schedule.interval_item.interval)

    def test_get_daily_by_id(self) -> None:
        self.server.version = "3.8"
        with open(GET_DAILY_ID_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
            baseurl = f"{self.server.baseurl}/schedules/{schedule_id}"
            m.get(baseurl, text=response_xml)
            schedule = self.server.schedules.get_by_id(schedule_id)
            self.assertIsNotNone(schedule)
            self.assertEqual(schedule_id, schedule.id)
            self.assertEqual("Daily schedule", schedule.name)
            self.assertEqual("Active", schedule.state)
            self.assertEqual(("Monday", 2.0), schedule.interval_item.interval)

    def test_get_monthly_by_id(self) -> None:
        self.server.version = "3.8"
        with open(GET_MONTHLY_ID_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
            baseurl = f"{self.server.baseurl}/schedules/{schedule_id}"
            m.get(baseurl, text=response_xml)
            schedule = self.server.schedules.get_by_id(schedule_id)
            self.assertIsNotNone(schedule)
            self.assertEqual(schedule_id, schedule.id)
            self.assertEqual("Monthly multiple days", schedule.name)
            self.assertEqual("Active", schedule.state)
            self.assertEqual(("1", "2"), schedule.interval_item.interval)

    def test_get_monthly_by_id_2(self) -> None:
        self.server.version = "3.15"
        with open(GET_MONTHLY_ID_2_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            schedule_id = "8c5caf33-6223-4724-83c3-ccdc1e730a07"
            baseurl = f"{self.server.baseurl}/schedules/{schedule_id}"
            m.get(baseurl, text=response_xml)
            schedule = self.server.schedules.get_by_id(schedule_id)
            self.assertIsNotNone(schedule)
            self.assertEqual(schedule_id, schedule.id)
            self.assertEqual("Monthly First Monday!", schedule.name)
            self.assertEqual("Active", schedule.state)
            self.assertEqual(("Monday", "First"), schedule.interval_item.interval)

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/c9cff7f9-309c-4361-99ff-d4ba8c9f5467", status_code=204)
            self.server.schedules.delete("c9cff7f9-309c-4361-99ff-d4ba8c9f5467")

    def test_create_hourly(self) -> None:
        with open(CREATE_HOURLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            hourly_interval = TSC.HourlyInterval(start_time=time(2, 30), end_time=time(23, 0), interval_value=2)
            new_schedule = TSC.ScheduleItem(
                "hourly-schedule-1",
                50,
                TSC.ScheduleItem.Type.Extract,
                TSC.ScheduleItem.ExecutionOrder.Parallel,
                hourly_interval,
            )
            new_schedule = self.server.schedules.create(new_schedule)

        self.assertEqual("5f42be25-8a43-47ba-971a-63f2d4e7029c", new_schedule.id)
        self.assertEqual("hourly-schedule-1", new_schedule.name)
        self.assertEqual("Active", new_schedule.state)
        self.assertEqual(50, new_schedule.priority)
        self.assertEqual("2016-09-15T20:47:33Z", format_datetime(new_schedule.created_at))
        self.assertEqual("2016-09-15T20:47:33Z", format_datetime(new_schedule.updated_at))
        self.assertEqual(TSC.ScheduleItem.Type.Extract, new_schedule.schedule_type)
        self.assertEqual("2016-09-16T01:30:00Z", format_datetime(new_schedule.next_run_at))
        self.assertEqual(TSC.ScheduleItem.ExecutionOrder.Parallel, new_schedule.execution_order)
        self.assertEqual(time(2, 30), new_schedule.interval_item.start_time)
        self.assertEqual(time(23), new_schedule.interval_item.end_time)  # type: ignore[union-attr]
        self.assertEqual(("8",), new_schedule.interval_item.interval)  # type: ignore[union-attr]

    def test_create_daily(self) -> None:
        with open(CREATE_DAILY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            daily_interval = TSC.DailyInterval(time(4, 50))
            new_schedule = TSC.ScheduleItem(
                "daily-schedule-1",
                90,
                TSC.ScheduleItem.Type.Subscription,
                TSC.ScheduleItem.ExecutionOrder.Serial,
                daily_interval,
            )
            new_schedule = self.server.schedules.create(new_schedule)

        self.assertEqual("907cae38-72fd-417c-892a-95540c4664cd", new_schedule.id)
        self.assertEqual("daily-schedule-1", new_schedule.name)
        self.assertEqual("Active", new_schedule.state)
        self.assertEqual(90, new_schedule.priority)
        self.assertEqual("2016-09-15T21:01:09Z", format_datetime(new_schedule.created_at))
        self.assertEqual("2016-09-15T21:01:09Z", format_datetime(new_schedule.updated_at))
        self.assertEqual(TSC.ScheduleItem.Type.Subscription, new_schedule.schedule_type)
        self.assertEqual("2016-09-16T11:45:00Z", format_datetime(new_schedule.next_run_at))
        self.assertEqual(TSC.ScheduleItem.ExecutionOrder.Serial, new_schedule.execution_order)
        self.assertEqual(time(4, 45), new_schedule.interval_item.start_time)

    def test_create_weekly(self) -> None:
        with open(CREATE_WEEKLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            weekly_interval = TSC.WeeklyInterval(
                time(9, 15), TSC.IntervalItem.Day.Monday, TSC.IntervalItem.Day.Wednesday, TSC.IntervalItem.Day.Friday
            )
            new_schedule = TSC.ScheduleItem(
                "weekly-schedule-1",
                80,
                TSC.ScheduleItem.Type.Extract,
                TSC.ScheduleItem.ExecutionOrder.Parallel,
                weekly_interval,
            )
            new_schedule = self.server.schedules.create(new_schedule)

        self.assertEqual("1adff386-6be0-4958-9f81-a35e676932bf", new_schedule.id)
        self.assertEqual("weekly-schedule-1", new_schedule.name)
        self.assertEqual("Active", new_schedule.state)
        self.assertEqual(80, new_schedule.priority)
        self.assertEqual("2016-09-15T21:12:50Z", format_datetime(new_schedule.created_at))
        self.assertEqual("2016-09-15T21:12:50Z", format_datetime(new_schedule.updated_at))
        self.assertEqual(TSC.ScheduleItem.Type.Extract, new_schedule.schedule_type)
        self.assertEqual("2016-09-16T16:15:00Z", format_datetime(new_schedule.next_run_at))
        self.assertEqual(TSC.ScheduleItem.ExecutionOrder.Parallel, new_schedule.execution_order)
        self.assertEqual(time(9, 15), new_schedule.interval_item.start_time)
        self.assertEqual(("Monday", "Wednesday", "Friday"), new_schedule.interval_item.interval)
        self.assertEqual(2, len(new_schedule.warnings))
        self.assertEqual("warning 1", new_schedule.warnings[0])
        self.assertEqual("warning 2", new_schedule.warnings[1])

    def test_create_monthly(self) -> None:
        with open(CREATE_MONTHLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            monthly_interval = TSC.MonthlyInterval(time(7), 12)
            new_schedule = TSC.ScheduleItem(
                "monthly-schedule-1",
                20,
                TSC.ScheduleItem.Type.Extract,
                TSC.ScheduleItem.ExecutionOrder.Serial,
                monthly_interval,
            )
            new_schedule = self.server.schedules.create(new_schedule)

        self.assertEqual("e06a7c75-5576-4f68-882d-8909d0219326", new_schedule.id)
        self.assertEqual("monthly-schedule-1", new_schedule.name)
        self.assertEqual("Active", new_schedule.state)
        self.assertEqual(20, new_schedule.priority)
        self.assertEqual("2016-09-15T21:16:56Z", format_datetime(new_schedule.created_at))
        self.assertEqual("2016-09-15T21:16:56Z", format_datetime(new_schedule.updated_at))
        self.assertEqual(TSC.ScheduleItem.Type.Extract, new_schedule.schedule_type)
        self.assertEqual("2016-10-12T14:00:00Z", format_datetime(new_schedule.next_run_at))
        self.assertEqual(TSC.ScheduleItem.ExecutionOrder.Serial, new_schedule.execution_order)
        self.assertEqual(time(7), new_schedule.interval_item.start_time)
        self.assertEqual(("12",), new_schedule.interval_item.interval)  # type: ignore[union-attr]

    def test_update(self) -> None:
        with open(UPDATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/7bea1766-1543-4052-9753-9d224bc069b5", text=response_xml)
            new_interval = TSC.WeeklyInterval(time(7), TSC.IntervalItem.Day.Monday, TSC.IntervalItem.Day.Friday)
            single_schedule = TSC.ScheduleItem(
                "weekly-schedule-1",
                90,
                TSC.ScheduleItem.Type.Extract,
                TSC.ScheduleItem.ExecutionOrder.Parallel,
                new_interval,
            )
            single_schedule._id = "7bea1766-1543-4052-9753-9d224bc069b5"
            single_schedule.state = TSC.ScheduleItem.State.Suspended
            single_schedule = self.server.schedules.update(single_schedule)

        self.assertEqual("7bea1766-1543-4052-9753-9d224bc069b5", single_schedule.id)
        self.assertEqual("weekly-schedule-1", single_schedule.name)
        self.assertEqual(90, single_schedule.priority)
        self.assertEqual("2016-09-15T23:50:02Z", format_datetime(single_schedule.updated_at))
        self.assertEqual(TSC.ScheduleItem.Type.Extract, single_schedule.schedule_type)
        self.assertEqual("2016-09-16T14:00:00Z", format_datetime(single_schedule.next_run_at))
        self.assertEqual(TSC.ScheduleItem.ExecutionOrder.Parallel, single_schedule.execution_order)
        self.assertEqual(time(7), single_schedule.interval_item.start_time)
        self.assertEqual(("Monday", "Friday"), single_schedule.interval_item.interval)  # type: ignore[union-attr]
        self.assertEqual(TSC.ScheduleItem.State.Suspended, single_schedule.state)

    # Tests calling update with a schedule item returned from the server
    def test_update_after_get(self) -> None:
        with open(GET_XML, "rb") as f:
            get_response_xml = f.read().decode("utf-8")
        with open(UPDATE_XML, "rb") as f:
            update_response_xml = f.read().decode("utf-8")

        # Get a schedule
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=get_response_xml)
            all_schedules, pagination_item = self.server.schedules.get()
        schedule_item = all_schedules[0]
        self.assertEqual(TSC.ScheduleItem.State.Active, schedule_item.state)
        self.assertEqual("Weekday early mornings", schedule_item.name)

        # Update the schedule
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/c9cff7f9-309c-4361-99ff-d4ba8c9f5467", text=update_response_xml)
            schedule_item.state = TSC.ScheduleItem.State.Suspended
            schedule_item.name = "newName"
            schedule_item = self.server.schedules.update(schedule_item)

        self.assertEqual(TSC.ScheduleItem.State.Suspended, schedule_item.state)
        self.assertEqual("weekly-schedule-1", schedule_item.name)

    def test_add_workbook(self) -> None:
        self.server.version = "2.8"
        baseurl = f"{self.server.baseurl}/sites/{self.server.site_id}/schedules"

        with open(WORKBOOK_GET_BY_ID_XML, "rb") as f:
            workbook_response = f.read().decode("utf-8")
        with open(ADD_WORKBOOK_TO_SCHEDULE, "rb") as f:
            add_workbook_response = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.server.workbooks.baseurl + "/bar", text=workbook_response)
            m.put(baseurl + "/foo/workbooks", text=add_workbook_response)
            workbook = self.server.workbooks.get_by_id("bar")
            result = self.server.schedules.add_to_schedule("foo", workbook=workbook)
        self.assertEqual(0, len(result), "Added properly")

    def test_add_workbook_with_warnings(self) -> None:
        self.server.version = "2.8"
        baseurl = f"{self.server.baseurl}/sites/{self.server.site_id}/schedules"

        with open(WORKBOOK_GET_BY_ID_XML, "rb") as f:
            workbook_response = f.read().decode("utf-8")
        with open(ADD_WORKBOOK_TO_SCHEDULE_WITH_WARNINGS, "rb") as f:
            add_workbook_response = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.server.workbooks.baseurl + "/bar", text=workbook_response)
            m.put(baseurl + "/foo/workbooks", text=add_workbook_response)
            workbook = self.server.workbooks.get_by_id("bar")
            result = self.server.schedules.add_to_schedule("foo", workbook=workbook)
        self.assertEqual(1, len(result), "Not added properly")
        self.assertEqual(2, len(result[0].warnings))

    def test_add_datasource(self) -> None:
        self.server.version = "2.8"
        baseurl = f"{self.server.baseurl}/sites/{self.server.site_id}/schedules"

        with open(DATASOURCE_GET_BY_ID_XML, "rb") as f:
            datasource_response = f.read().decode("utf-8")
        with open(ADD_DATASOURCE_TO_SCHEDULE, "rb") as f:
            add_datasource_response = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.server.datasources.baseurl + "/bar", text=datasource_response)
            m.put(baseurl + "/foo/datasources", text=add_datasource_response)
            datasource = self.server.datasources.get_by_id("bar")
            result = self.server.schedules.add_to_schedule("foo", datasource=datasource)
        self.assertEqual(0, len(result), "Added properly")

    def test_add_flow(self) -> None:
        self.server.version = "3.3"
        baseurl = f"{self.server.baseurl}/sites/{self.server.site_id}/schedules"

        with open(FLOW_GET_BY_ID_XML, "rb") as f:
            flow_response = f.read().decode("utf-8")
        with open(ADD_FLOW_TO_SCHEDULE, "rb") as f:
            add_flow_response = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.server.flows.baseurl + "/bar", text=flow_response)
            m.put(baseurl + "/foo/flows", text=flow_response)
            flow = self.server.flows.get_by_id("bar")
            result = self.server.schedules.add_to_schedule("foo", flow=flow)
        self.assertEqual(0, len(result), "Added properly")
