import unittest
import os
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML_NO_WORKBOOK = os.path.join(TEST_ASSET_DIR, "tasks_no_workbook_or_datasource.xml")
GET_XML_WITH_WORKBOOK = os.path.join(TEST_ASSET_DIR, "tasks_with_workbook.xml")
GET_XML_WITH_DATASOURCE = os.path.join(TEST_ASSET_DIR, "tasks_with_datasource.xml")
GET_XML_WITH_WORKBOOK_AND_DATASOURCE = os.path.join(TEST_ASSET_DIR, "tasks_with_workbook_and_datasource.xml")


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test")
        self.server.version = '2.6'

        # Fake Signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.tasks.baseurl

    def test_get_tasks_with_no_workbook(self):
        with open(GET_XML_NO_WORKBOOK, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_tasks, pagination_item = self.server.tasks.get()

        task = all_tasks[0]
        self.assertEqual(None, task.target)

    def test_get_tasks_with_workbook(self):
        with open(GET_XML_WITH_WORKBOOK, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_tasks, pagination_item = self.server.tasks.get()

        task = all_tasks[0]
        self.assertEqual('c7a9327e-1cda-4504-b026-ddb43b976d1d', task.target.id)
        self.assertEqual('workbook', task.target.type)

    def test_get_tasks_with_datasource(self):
        with open(GET_XML_WITH_DATASOURCE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_tasks, pagination_item = self.server.tasks.get()

        task = all_tasks[0]
        self.assertEqual('c7a9327e-1cda-4504-b026-ddb43b976d1d', task.target.id)
        self.assertEqual('datasource', task.target.type)

    def test_get_tasks_with_workbook_and_datasource(self):
        with open(GET_XML_WITH_WORKBOOK_AND_DATASOURCE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_tasks, pagination_item = self.server.tasks.get()

        self.assertEqual('workbook', all_tasks[0].target.type)
        self.assertEqual('datasource', all_tasks[1].target.type)
        self.assertEqual('workbook', all_tasks[2].target.type)

    def test_get_task_with_schedule(self):
        with open(GET_XML_WITH_WORKBOOK, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_tasks, pagination_item = self.server.tasks.get()

        task = all_tasks[0]
        self.assertEqual('c7a9327e-1cda-4504-b026-ddb43b976d1d', task.target.id)
        self.assertEqual('workbook', task.target.type)
        self.assertEqual('b60b4efd-a6f7-4599-beb3-cb677e7abac1', task.schedule_id)
