import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import FlowRunFailedException
from ._utils import read_xml_asset, mocked_time

GET_XML = "flow_runs_get.xml"
GET_BY_ID_XML = "flow_runs_get_by_id.xml"
GET_BY_ID_FAILED_XML = "flow_runs_get_by_id_failed.xml"
GET_BY_ID_INPROGRESS_XML = "flow_runs_get_by_id_inprogress.xml"


class FlowRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.server.version = "3.10"

        self.baseurl = self.server.flow_runs.baseurl

    def test_get(self) -> None:
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_flow_runs, pagination_item = self.server.flow_runs.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("cc2e652d-4a9b-4476-8c93-b238c45db968", all_flow_runs[0].id)
        self.assertEqual("2021-02-11T01:42:55Z", format_datetime(all_flow_runs[0].started_at))
        self.assertEqual("2021-02-11T01:57:38Z", format_datetime(all_flow_runs[0].completed_at))
        self.assertEqual("Success", all_flow_runs[0].status)
        self.assertEqual("100", all_flow_runs[0].progress)
        self.assertEqual("aa23f4ac-906f-11e9-86fb-3f0f71412e77", all_flow_runs[0].background_job_id)

        self.assertEqual("a3104526-c0c6-4ea5-8362-e03fc7cbd7ee", all_flow_runs[1].id)
        self.assertEqual("2021-02-13T04:05:30Z", format_datetime(all_flow_runs[1].started_at))
        self.assertEqual("2021-02-13T04:05:35Z", format_datetime(all_flow_runs[1].completed_at))
        self.assertEqual("Failed", all_flow_runs[1].status)
        self.assertEqual("100", all_flow_runs[1].progress)
        self.assertEqual("1ad21a9d-2530-4fbf-9064-efd3c736e023", all_flow_runs[1].background_job_id)

    def test_get_by_id(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/cc2e652d-4a9b-4476-8c93-b238c45db968", text=response_xml)
            flow_run = self.server.flow_runs.get_by_id("cc2e652d-4a9b-4476-8c93-b238c45db968")

        self.assertEqual("cc2e652d-4a9b-4476-8c93-b238c45db968", flow_run.id)
        self.assertEqual("2021-02-11T01:42:55Z", format_datetime(flow_run.started_at))
        self.assertEqual("2021-02-11T01:57:38Z", format_datetime(flow_run.completed_at))
        self.assertEqual("Success", flow_run.status)
        self.assertEqual("100", flow_run.progress)
        self.assertEqual("1ad21a9d-2530-4fbf-9064-efd3c736e023", flow_run.background_job_id)

    def test_cancel_id(self) -> None:
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
            self.server.flow_runs.cancel("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

    def test_cancel_item(self) -> None:
        run = TSC.FlowRunItem()
        run._id = "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
            self.server.flow_runs.cancel(run)

    def test_wait_for_job_finished(self) -> None:
        # Waiting for an already finished job, directly returns that job's info
        response_xml = read_xml_asset(GET_BY_ID_XML)
        flow_run_id = "cc2e652d-4a9b-4476-8c93-b238c45db968"
        with mocked_time(), requests_mock.mock() as m:
            m.get("{0}/{1}".format(self.baseurl, flow_run_id), text=response_xml)
            flow_run = self.server.flow_runs.wait_for_job(flow_run_id)

            self.assertEqual(flow_run_id, flow_run.id)
            self.assertEqual(flow_run.progress, "100")

    def test_wait_for_job_failed(self) -> None:
        # Waiting for a failed job raises an exception
        response_xml = read_xml_asset(GET_BY_ID_FAILED_XML)
        flow_run_id = "c2b35d5a-e130-471a-aec8-7bc5435fe0e7"
        with mocked_time(), requests_mock.mock() as m:
            m.get("{0}/{1}".format(self.baseurl, flow_run_id), text=response_xml)
            with self.assertRaises(FlowRunFailedException):
                self.server.flow_runs.wait_for_job(flow_run_id)

    def test_wait_for_job_timeout(self) -> None:
        # Waiting for a job which doesn't terminate will throw an exception
        response_xml = read_xml_asset(GET_BY_ID_INPROGRESS_XML)
        flow_run_id = "71afc22c-9c06-40be-8d0f-4c4166d29e6c"
        with mocked_time(), requests_mock.mock() as m:
            m.get("{0}/{1}".format(self.baseurl, flow_run_id), text=response_xml)
            with self.assertRaises(TimeoutError):
                self.server.flow_runs.wait_for_job(flow_run_id, timeout=30)
