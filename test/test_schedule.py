import unittest
import os
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML = os.path.join(TEST_ASSET_DIR, "schedule_get.xml")
GET_EMPTY_XML = os.path.join(TEST_ASSET_DIR, "schedule_get_empty.xml")


class ScheduleTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test")

        # Fake Signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.schedules._construct_url()

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
        self.assertEqual("2016-07-06T20:19:00Z", all_schedules[0].created_at)
        self.assertEqual("2016-09-13T11:00:32Z", all_schedules[0].updated_at)
        self.assertEqual("Extract", all_schedules[0].type)
        self.assertEqual("Weekly", all_schedules[0].frequency)
        self.assertEqual("2016-09-14T11:00:00Z", all_schedules[0].next_run_at)

        self.assertEqual("bcb79d07-6e47-472f-8a65-d7f51f40c36c", all_schedules[1].id)
        self.assertEqual("Saturday night", all_schedules[1].name)
        self.assertEqual("Active", all_schedules[1].state)
        self.assertEqual(80, all_schedules[1].priority)
        self.assertEqual("2016-07-07T20:19:00Z", all_schedules[1].created_at)
        self.assertEqual("2016-09-12T16:39:38Z", all_schedules[1].updated_at)
        self.assertEqual("Subscription", all_schedules[1].type)
        self.assertEqual("Weekly", all_schedules[1].frequency)
        self.assertEqual("2016-09-18T06:00:00Z", all_schedules[1].next_run_at)

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
