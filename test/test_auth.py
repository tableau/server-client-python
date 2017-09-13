import unittest
import os.path
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

SIGN_IN_XML = os.path.join(TEST_ASSET_DIR, 'auth_sign_in.xml')
SIGN_IN_IMPERSONATE_XML = os.path.join(TEST_ASSET_DIR, 'auth_sign_in_impersonate.xml')
SIGN_IN_ERROR_XML = os.path.join(TEST_ASSET_DIR, 'auth_sign_in_error.xml')


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.baseurl = self.server.auth.baseurl

    def test_sign_in(self):
        with open(SIGN_IN_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/signin', text=response_xml)
            tableau_auth = TSC.TableauAuth('testuser', 'password', site_id='Samples')
            self.server.auth.sign_in(tableau_auth)

        self.assertEqual('eIX6mvFsqyansa4KqEI1UwOpS8ggRs2l', self.server.auth_token)
        self.assertEqual('6b7179ba-b82b-4f0f-91ed-812074ac5da6', self.server.site_id)
        self.assertEqual('1a96d216-e9b8-497b-a82a-0b899a965e01', self.server.user_id)

    def test_sign_in_impersonate(self):
        with open(SIGN_IN_IMPERSONATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/signin', text=response_xml)
            tableau_auth = TSC.TableauAuth('testuser', 'password',
                                           user_id_to_impersonate='dd2239f6-ddf1-4107-981a-4cf94e415794')
            self.server.auth.sign_in(tableau_auth)

        self.assertEqual('MJonFA6HDyy2C3oqR13fRGqE6cmgzwq3', self.server.auth_token)
        self.assertEqual('dad65087-b08b-4603-af4e-2887b8aafc67', self.server.site_id)
        self.assertEqual('dd2239f6-ddf1-4107-981a-4cf94e415794', self.server.user_id)

    def test_sign_in_error(self):
        with open(SIGN_IN_ERROR_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/signin', text=response_xml, status_code=401)
            tableau_auth = TSC.TableauAuth('testuser', 'wrongpassword')
            self.assertRaises(TSC.ServerResponseError, self.server.auth.sign_in, tableau_auth)

    def test_sign_in_without_auth(self):
        with open(SIGN_IN_ERROR_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/signin', text=response_xml, status_code=401)
            tableau_auth = TSC.TableauAuth('', '')
            self.assertRaises(TSC.ServerResponseError, self.server.auth.sign_in, tableau_auth)

    def test_sign_out(self):
        with open(SIGN_IN_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/signin', text=response_xml)
            m.post(self.baseurl + '/signout', text='')
            tableau_auth = TSC.TableauAuth('testuser', 'password')
            self.server.auth.sign_in(tableau_auth)
            self.server.auth.sign_out()

        self.assertIsNone(self.server._auth_token)
        self.assertIsNone(self.server._site_id)
        self.assertIsNone(self.server._user_id)
