import unittest
import os.path
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

SERVER_INFO_GET_XML = os.path.join(TEST_ASSET_DIR, 'server_info_get.xml')


class ServerInfoTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.server.version = '2.4'
        self.baseurl = self.server.server_info.baseurl

    def test_server_info_get(self):
        with open(SERVER_INFO_GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            actual = self.server.server_info.get()

            self.assertEqual('10.1.0', actual.product_version)
            self.assertEqual('10100.16.1024.2100', actual.build_number)
            self.assertEqual('2.4', actual.rest_api_version)
