import os
import unittest
from datetime import datetime

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import utc
from tableauserverclient.server.endpoint.exceptions import JobFailedException
from ._utils import read_xml_asset, mocked_time

GET_XML = "job_get.xml"
GET_BY_ID_XML = "job_get_by_id.xml"
GET_BY_ID_FAILED_XML = "job_get_by_id_failed.xml"
GET_BY_ID_CANCELLED_XML = "job_get_by_id_cancelled.xml"
GET_BY_ID_INPROGRESS_XML = "job_get_by_id_inprogress.xml"
GET_BY_ID_WORKBOOK = "job_get_by_id_failed_workbook.xml"


class JobTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.1"

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.jobs.baseurl

    def test_get(self) -> None:
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_jobs, pagination_item = self.server.jobs.get()
            job = all_jobs[0]
            created_at = datetime(2018, 5, 22, 13, 0, 29, tzinfo=utc)
            started_at = datetime(2018, 5, 22, 13, 0, 37, tzinfo=utc)
            ended_at = datetime(2018, 5, 22, 13, 0, 45, tzinfo=utc)

            self.assertEqual(1, pagination_item.total_available)
            self.assertEqual("2eef4225-aa0c-41c4-8662-a76d89ed7336", job.id)
            self.assertEqual("Success", job.status)
            self.assertEqual("50", job.priority)
            self.assertEqual("single_subscription_notify", job.type)
            self.assertEqual(created_at, job.created_at)
            self.assertEqual(started_at, job.started_at)
            self.assertEqual(ended_at, job.ended_at)

    def test_get_by_id(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_XML)
        job_id = "2eef4225-aa0c-41c4-8662-a76d89ed7336"
        with requests_mock.mock() as m:
            m.get("{0}/{1}".format(self.baseurl, job_id), text=response_xml)
            job = self.server.jobs.get_by_id(job_id)
            updated_at = datetime(2020, 5, 13, 20, 25, 18, tzinfo=utc)

            self.assertEqual(job_id, job.id)
            self.assertEqual(updated_at, job.updated_at)
            self.assertListEqual(job.notes, ["Job detail notes"])

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.jobs.get)

    def test_cancel_id(self) -> None:
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
            self.server.jobs.cancel("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

    def test_cancel_item(self) -> None:
        created_at = datetime(2018, 5, 22, 13, 0, 29, tzinfo=utc)
        started_at = datetime(2018, 5, 22, 13, 0, 37, tzinfo=utc)
        job = TSC.JobItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "backgroundJob", "0", created_at, started_at, None, 0)
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
            self.server.jobs.cancel(job)

    def test_wait_for_job_finished(self) -> None:
        # Waiting for an already finished job, directly returns that job's info
        response_xml = read_xml_asset(GET_BY_ID_XML)
        job_id = "2eef4225-aa0c-41c4-8662-a76d89ed7336"
        with mocked_time(), requests_mock.mock() as m:
            m.get("{0}/{1}".format(self.baseurl, job_id), text=response_xml)
            job = self.server.jobs.wait_for_job(job_id)

            self.assertEqual(job_id, job.id)
            self.assertListEqual(job.notes, ["Job detail notes"])

    def test_wait_for_job_failed(self) -> None:
        # Waiting for a failed job raises an exception
        response_xml = read_xml_asset(GET_BY_ID_FAILED_XML)
        job_id = "77d5e57a-2517-479f-9a3c-a32025f2b64d"
        with mocked_time(), requests_mock.mock() as m:
            m.get("{0}/{1}".format(self.baseurl, job_id), text=response_xml)
            with self.assertRaises(JobFailedException):
                self.server.jobs.wait_for_job(job_id)

    def test_wait_for_job_timeout(self) -> None:
        # Waiting for a job which doesn't terminate will throw an exception
        response_xml = read_xml_asset(GET_BY_ID_INPROGRESS_XML)
        job_id = "77d5e57a-2517-479f-9a3c-a32025f2b64d"
        with mocked_time(), requests_mock.mock() as m:
            m.get("{0}/{1}".format(self.baseurl, job_id), text=response_xml)
            with self.assertRaises(TimeoutError):
                self.server.jobs.wait_for_job(job_id, timeout=30)

    def test_get_job_datasource_id(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_FAILED_XML)
        job_id = "777bf7c4-421d-4b2c-a518-11b90187c545"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{job_id}", text=response_xml)
            job = self.server.jobs.get_by_id(job_id)
        self.assertEqual(job.datasource_id, "03b9fbec-81f6-4160-ae49-5f9f6d412758")

    def test_get_job_workbook_id(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_WORKBOOK)
        job_id = "bb1aab79-db54-4e96-9dd3-461d8f081d08"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{job_id}", text=response_xml)
            job = self.server.jobs.get_by_id(job_id)
        self.assertEqual(job.workbook_id, "5998aaaf-1abe-4d38-b4d9-bc53e85bdd13")

    def test_get_job_workbook_name(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_WORKBOOK)
        job_id = "bb1aab79-db54-4e96-9dd3-461d8f081d08"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{job_id}", text=response_xml)
            job = self.server.jobs.get_by_id(job_id)
        self.assertEqual(job.workbook_name, "Superstore")

    def test_get_job_datasource_name(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_FAILED_XML)
        job_id = "777bf7c4-421d-4b2c-a518-11b90187c545"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{job_id}", text=response_xml)
            job = self.server.jobs.get_by_id(job_id)
        self.assertEqual(job.datasource_name, "World Indicators")

    def test_background_job_str(self) -> None:
        job = TSC.BackgroundJobItem(
            "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", datetime.now(), 1, "extractRefresh", "Failed"
        )
        assert not str(job).startswith("<<property")
        assert not repr(job).startswith("<<property")
        assert "BackgroundJobItem" in str(job)
