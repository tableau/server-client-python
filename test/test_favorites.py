import unittest
import os
import requests_mock
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import read_xml_asset, read_xml_assets, asset

GET_FAVORITES_XML = 'favorites_get.xml'

class FavoritesTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.server.version = '2.5'

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.favorites.baseurl
        self.user = TSC.UserItem('alice', TSC.UserItem.Roles.Viewer)
        self.user._id = 'dd2239f6-ddf1-4107-981a-4cf94e415794'

    def test_get(self):
        response_xml = read_xml_asset(GET_FAVORITES_XML)
        with requests_mock.mock() as m:
            m.get('{0}/{1}'.format(self.baseurl, self.user.id), 
                  text=response_xml)
            self.server.favorites.get(self.user)
        self.assertIsNotNone(self.user._favorites)  
        self.assertEqual(len(self.user.favorites['workbooks']), 1)
        self.assertEqual(len(self.user.favorites['views']), 1)
        self.assertEqual(len(self.user.favorites['projects']), 1)
        self.assertEqual(len(self.user.favorites['datasources']), 1)
