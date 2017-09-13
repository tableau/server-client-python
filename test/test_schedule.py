from datetime import time
import unittest
import os
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = os.path.join(TEST_ASSET_DIR, "schedule_get.xml")
GET_EMPTY_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_empty.xml")
CREATE_HOURLY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_hourly.xml")
CREATE_DAILY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_daily.xml")
CREATE_WEEKLY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_weekly.xml")
CREATE_MONTHLY_XML = os.path.join(TEST_ASSET_DIR, "schedule_create_monthly.xml")
UPDATE_XML = os.path.join(TEST_ASSET_DIR, "schedule_update.xml")


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test")

        # Fake Signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.schedules.baseurl

    def test_get(self):
        with open(GET_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_schedules, pagination_item = self.server.schedules.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("c9cff7f9-309c-4361-99ff-d4ba8c9f5467", all_schedules[0].id)
        self.assertEqual("Weekday early mornings", all_schedules[0].name)
        self.assertEqual("Active", all_schedules[0].state)
        self.assertEqual(50, all_schedules[0].priority)
        self.assertEqual("2016-07-06T20:19:00Z", format_datetime(all_schedules[0].created_at))
        self.assertEqual("2016-09-13T11:00:32Z", format_datetime(all_schedules[0].updated_at))
        self.assertEqual("Extract", all_schedules[0].schedule_type)
        self.assertEqual("2016-09-14T11:00:00Z", format_datetime(all_schedules[0].next_run_at))

        self.assertEqual("bcb79d07-6e47-472f-8a65-d7f51f40c36c", all_schedules[1].id)
        self.assertEqual("Saturday night", all_schedules[1].name)
        self.assertEqual("Active", all_schedules[1].state)
        self.assertEqual(80, all_schedules[1].priority)
        self.assertEqual("2016-07-07T20:19:00Z", format_datetime(all_schedules[1].created_at))
        self.assertEqual("2016-09-12T16:39:38Z", format_datetime(all_schedules[1].updated_at))
        self.assertEqual("Subscription", all_schedules[1].schedule_type)
        self.assertEqual("2016-09-18T06:00:00Z", format_datetime(all_schedules[1].next_run_at))

    def test_get_empty(self):
        with open(GET_EMPTY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_schedules, pagination_item = self.server.schedules.get()

        self.assertEqual(0, pagination_item.total_available)
        self.assertEqual([], all_schedules)

    def test_delete(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/c9cff7f9-309c-4361-99ff-d4ba8c9f5467", status_code=204)
            self.server.schedules.delete("c9cff7f9-309c-4361-99ff-d4ba8c9f5467")

    def test_create_hourly(self):
        with open(CREATE_HOURLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            hourly_interval = TSC.HourlyInterval(start_time=time(2, 30),
                                                 end_time=time(23, 0),
                                                 interval_value=2)
            new_schedule = TSC.ScheduleItem("hourly-schedule-1", 50, TSC.ScheduleItem.Type.Extract,
                                            TSC.ScheduleItem.ExecutionOrder.Parallel, hourly_interval)
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
        self.assertEqual(time(23), new_schedule.interval_item.end_time)
        self.assertEqual("8", new_schedule.interval_item.interval)

    def test_create_daily(self):
        with open(CREATE_DAILY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            daily_interval = TSC.DailyInterval(time(4, 50))
            new_schedule = TSC.ScheduleItem("daily-schedule-1", 90, TSC.ScheduleItem.Type.Subscription,
                                            TSC.ScheduleItem.ExecutionOrder.Serial, daily_interval)
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

    def test_create_weekly(self):
        with open(CREATE_WEEKLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            weekly_interval = TSC.WeeklyInterval(time(9, 15), TSC.IntervalItem.Day.Monday,
                                                 TSC.IntervalItem.Day.Wednesday,
                                                 TSC.IntervalItem.Day.Friday)
            new_schedule = TSC.ScheduleItem("weekly-schedule-1", 80, TSC.ScheduleItem.Type.Extract,
                                            TSC.ScheduleItem.ExecutionOrder.Parallel, weekly_interval)
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
        self.assertEqual(("Monday", "Wednesday", "Friday"),
                         new_schedule.interval_item.interval)

    def test_create_monthly(self):
        with open(CREATE_MONTHLY_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            monthly_interval = TSC.MonthlyInterval(time(7), 12)
            new_schedule = TSC.ScheduleItem("monthly-schedule-1", 20, TSC.ScheduleItem.Type.Extract,
                                            TSC.ScheduleItem.ExecutionOrder.Serial, monthly_interval)
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
        self.assertEqual("12", new_schedule.interval_item.interval)

    def test_update(self):
        with open(UPDATE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/7bea1766-1543-4052-9753-9d224bc069b5', text=response_xml)
            new_interval = TSC.WeeklyInterval(time(7), TSC.IntervalItem.Day.Monday,
                                              TSC.IntervalItem.Day.Friday)
            single_schedule = TSC.ScheduleItem("weekly-schedule-1", 90, TSC.ScheduleItem.Type.Extract,
                                               TSC.ScheduleItem.ExecutionOrder.Parallel, new_interval)
            single_schedule._id = "7bea1766-1543-4052-9753-9d224bc069b5"
            single_schedule = self.server.schedules.update(single_schedule)

        self.assertEqual("7bea1766-1543-4052-9753-9d224bc069b5", single_schedule.id)
        self.assertEqual("weekly-schedule-1", single_schedule.name)
        self.assertEqual(90, single_schedule.priority)
        self.assertEqual("2016-09-15T23:50:02Z", format_datetime(single_schedule.updated_at))
        self.assertEqual(TSC.ScheduleItem.Type.Extract, single_schedule.schedule_type)
        self.assertEqual("2016-09-16T14:00:00Z", format_datetime(single_schedule.next_run_at))
        self.assertEqual(TSC.ScheduleItem.ExecutionOrder.Parallel, single_schedule.execution_order)
        self.assertEqual(time(7), single_schedule.interval_item.start_time)
        self.assertEqual(("Monday", "Friday"),
                         single_schedule.interval_item.interval)
