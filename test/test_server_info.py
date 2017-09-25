import unittest
import os.path
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

SERVER_INFO_GET_XML = os.path.join(TEST_ASSET_DIR, 'server_info_get.xml')
SERVER_INFO_25_XML = os.path.join(TEST_ASSET_DIR, 'server_info_25.xml')
SERVER_INFO_404 = os.path.join(TEST_ASSET_DIR, 'server_info_404.xml')
SERVER_INFO_AUTH_INFO_XML = os.path.join(TEST_ASSET_DIR, 'server_info_auth_info.xml')


class ServerInfoTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.baseurl = self.server.server_info.baseurl
        self.server.version = "2.4"

    def test_server_info_get(self):
        with open(SERVER_INFO_GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.server.server_info.baseurl, text=response_xml)
            actual = self.server.server_info.get()

            self.assertEqual('10.1.0', actual.product_version)
            self.assertEqual('10100.16.1024.2100', actual.build_number)
            self.assertEqual('2.4', actual.rest_api_version)

    def test_server_info_use_highest_version_downgrades(self):
        with open(SERVER_INFO_AUTH_INFO_XML, 'rb') as f:
            # This is the auth.xml endpoint present back to 9.0 Servers
            auth_response_xml = f.read().decode('utf-8')
        with open(SERVER_INFO_404, 'rb') as f:
            # 10.1 serverInfo response
            si_response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            # Return a 404 for serverInfo so we can pretend this is an old Server
            m.get(self.server.server_address + "/api/2.4/serverInfo", text=si_response_xml, status_code=404)
            m.get(self.server.server_address + "/auth?format=xml", text=auth_response_xml)
            self.server.use_server_version()
            self.assertEqual(self.server.version, '2.2')

    def test_server_info_use_highest_version_upgrades(self):
        with open(SERVER_INFO_GET_XML, 'rb') as f:
            si_response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.server.server_address + "/api/2.4/serverInfo", text=si_response_xml)
            # Pretend we're old
            self.server.version = '2.0'
            self.server.use_server_version()
            # Did we upgrade to 2.4?
            self.assertEqual(self.server.version, '2.4')

    def test_server_use_server_version_flag(self):
        with open(SERVER_INFO_25_XML, 'rb') as f:
            si_response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get('http://test/api/2.4/serverInfo', text=si_response_xml)
            server = TSC.Server('http://test', use_server_version=True)
            self.assertEqual(server.version, '2.5')
