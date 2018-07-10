import unittest
import os
from datetime import datetime
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import utc

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

GET_XML = os.path.join(TEST_ASSET_DIR, 'job_get.xml')


class JobTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.server.version = '3.1'

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.jobs.baseurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_jobs, pagination_item = self.server.jobs.get()
            job = all_jobs[0]
            created_at = datetime(2018, 5, 22, 13, 0, 29, tzinfo=utc)
            started_at = datetime(2018, 5, 22, 13, 0, 37, tzinfo=utc)
            ended_at = datetime(2018, 5, 22, 13, 0, 45, tzinfo=utc)

            self.assertEquals(1, pagination_item.total_available)
            self.assertEquals('2eef4225-aa0c-41c4-8662-a76d89ed7336', job.id)
            self.assertEquals('Success', job.status)
            self.assertEquals('50', job.priority)
            self.assertEquals('single_subscription_notify', job.type)
            self.assertEquals(created_at, job.created_at)
            self.assertEquals(started_at, job.started_at)
            self.assertEquals(ended_at, job.ended_at)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.jobs.get)

    def test_cancel(self):
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', status_code=204)
            self.server.jobs.cancel('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')
