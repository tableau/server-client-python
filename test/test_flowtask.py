import os
import unittest
from datetime import time
from pathlib import Path

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.task_item import TaskItem

TEST_ASSET_DIR = Path(__file__).parent / "assets"
GET_XML_CREATE_FLOW_TASK_RESPONSE = os.path.join(TEST_ASSET_DIR, "tasks_create_flow_task.xml")


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.22"

        # Fake Signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.flow_tasks.baseurl

    def test_create_flow_task(self):
        monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30), interval_value=15)
        monthly_schedule = TSC.ScheduleItem(
            "Monthly Schedule",
            50,
            TSC.ScheduleItem.Type.Flow,
            TSC.ScheduleItem.ExecutionOrder.Parallel,
            monthly_interval,
        )
        target_item = TSC.Target("flow_id", "flow")

        task = TaskItem(None, "RunFlow", None, schedule_item=monthly_schedule, target=target_item)

        with open(GET_XML_CREATE_FLOW_TASK_RESPONSE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post("{}".format(self.baseurl), text=response_xml)
            create_response_content = self.server.flow_tasks.create(task).decode("utf-8")

        self.assertTrue("schedule_id" in create_response_content)
        self.assertTrue("flow_id" in create_response_content)
