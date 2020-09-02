import unittest
import os
from datetime import datetime
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import utc
from ._utils import read_xml_asset

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

GET_XML = 'job_get.xml'
GET_BY_ID_XML = 'job_get_by_id.xml'


class JobTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.server.version = '3.1'

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.jobs.baseurl

    def test_get(self):
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_jobs, pagination_item = self.server.jobs.get()
            job = all_jobs[0]
            created_at = datetime(2018, 5, 22, 13, 0, 29, tzinfo=utc)
            started_at = datetime(2018, 5, 22, 13, 0, 37, tzinfo=utc)
            ended_at = datetime(2018, 5, 22, 13, 0, 45, tzinfo=utc)

            self.assertEqual(1, pagination_item.total_available)
            self.assertEqual('2eef4225-aa0c-41c4-8662-a76d89ed7336', job.id)
            self.assertEqual('Success', job.status)
            self.assertEqual('50', job.priority)
            self.assertEqual('single_subscription_notify', job.type)
            self.assertEqual(created_at, job.created_at)
            self.assertEqual(started_at, job.started_at)
            self.assertEqual(ended_at, job.ended_at)

    def test_get_by_id(self):
        response_xml = read_xml_asset(GET_BY_ID_XML)
        job_id = '2eef4225-aa0c-41c4-8662-a76d89ed7336'
        with requests_mock.mock() as m:
            m.get('{0}/{1}'.format(self.baseurl, job_id), text=response_xml)
            job = self.server.jobs.get_by_id(job_id)

            created_at = datetime(2020, 5, 13, 20, 23, 45, tzinfo=utc)
            updated_at = datetime(2020, 5, 13, 20, 25, 18, tzinfo=utc)
            ended_at = datetime(2020, 5, 13, 20, 25, 18, tzinfo=utc)
            self.assertEqual(job_id, job.id)
            self.assertListEqual(job.notes, ['Job detail notes'])

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.jobs.get)

    def test_cancel_id(self):
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', status_code=204)
            self.server.jobs.cancel('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')

    def test_cancel_item(self):
        created_at = datetime(2018, 5, 22, 13, 0, 29, tzinfo=utc)
        started_at = datetime(2018, 5, 22, 13, 0, 37, tzinfo=utc)
        job = TSC.JobItem('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', 'backgroundJob',
                          0, created_at, started_at, None, 0)
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', status_code=204)
            self.server.jobs.cancel(job)
