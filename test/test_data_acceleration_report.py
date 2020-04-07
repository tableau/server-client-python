import unittest
import os
import requests_mock
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
from ._utils import read_xml_asset, read_xml_assets, asset

GET_XML = 'data_acceleration_report.xml'


class DataAccelerationReportTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'
        self.server.version = "3.8"

        self.baseurl = self.server.data_acceleration_report.baseurl

    def test_get(self):
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            data_acceleration_report = self.server.data_acceleration_report.get()

        self.assertEqual(2, len(data_acceleration_report.comparison_records))

        self.assertEqual("site-1", data_acceleration_report.comparison_records[0].site)
        self.assertEqual("sheet-1", data_acceleration_report.comparison_records[0].sheet_uri)
        self.assertEqual("0", data_acceleration_report.comparison_records[0].unaccelerated_session_count)
        self.assertEqual("0.0", data_acceleration_report.comparison_records[0].avg_non_accelerated_plt)
        self.assertEqual("1", data_acceleration_report.comparison_records[0].accelerated_session_count)
        self.assertEqual("0.166", data_acceleration_report.comparison_records[0].avg_accelerated_plt)

        self.assertEqual("site-2", data_acceleration_report.comparison_records[1].site)
        self.assertEqual("sheet-2", data_acceleration_report.comparison_records[1].sheet_uri)
        self.assertEqual("2", data_acceleration_report.comparison_records[1].unaccelerated_session_count)
        self.assertEqual("1.29", data_acceleration_report.comparison_records[1].avg_non_accelerated_plt)
        self.assertEqual("3", data_acceleration_report.comparison_records[1].accelerated_session_count)
        self.assertEqual("0.372", data_acceleration_report.comparison_records[1].avg_accelerated_plt)
