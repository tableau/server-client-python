import unittest
import os
import requests_mock
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import read_xml_asset, read_xml_assets, asset

GET_XML = 'flowruns_get.xml'
GET_BY_ID_XML = 'flowruns_get_by_id.xml'


class FlowRunTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'
        self.server.version = "3.10"

        self.baseurl = self.server.flowruns.baseurl

    def test_get(self):
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_flowruns, pagination_item = self.server.flowruns.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual('cc2e652d-4a9b-4476-8c93-b238c45db968', all_flowruns[0].id)
        self.assertEqual('2021-02-11T01:42:55Z', format_datetime(all_flowruns[0].started_at))
        self.assertEqual('2021-02-11T01:57:38Z', format_datetime(all_flowruns[0].completed_at))
        self.assertEqual('Success', all_flowruns[0].status)
        self.assertEqual('100', all_flowruns[0].progress)
        self.assertEqual('aa23f4ac-906f-11e9-86fb-3f0f71412e77', all_flowruns[0].background_job_id)

        self.assertEqual('a3104526-c0c6-4ea5-8362-e03fc7cbd7ee', all_flowruns[1].id)
        self.assertEqual('2021-02-13T04:05:30Z', format_datetime(all_flowruns[1].started_at))
        self.assertEqual('2021-02-13T04:05:35Z', format_datetime(all_flowruns[1].completed_at))
        self.assertEqual('Failed', all_flowruns[1].status)
        self.assertEqual('100', all_flowruns[1].progress)
        self.assertEqual('1ad21a9d-2530-4fbf-9064-efd3c736e023', all_flowruns[1].background_job_id)

    def test_get_by_id(self):
        response_xml = read_xml_asset(GET_BY_ID_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/cc2e652d-4a9b-4476-8c93-b238c45db968", text=response_xml)
            flowrun = self.server.flowruns.get_by_id("cc2e652d-4a9b-4476-8c93-b238c45db968")
        
        self.assertEqual('cc2e652d-4a9b-4476-8c93-b238c45db968', flowrun.id)
        self.assertEqual('2021-02-11T01:42:55Z', format_datetime(flowrun.started_at))
        self.assertEqual('2021-02-11T01:57:38Z', format_datetime(flowrun.completed_at))
        self.assertEqual('Success', flowrun.status)
        self.assertEqual('100', flowrun.progress)
        self.assertEqual('1ad21a9d-2530-4fbf-9064-efd3c736e023', flowrun.background_job_id)

    def test_cancel_id(self):
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', status_code=204)
            self.server.flowruns.cancel('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760')

    def test_cancel_item(self):
        run = TSC.FlowRunItem()
        run._id = 'ee8c6e70-43b6-11e6-af4f-f7b0d8e20760'
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', status_code=204)
            self.server.flowruns.cancel(run)
