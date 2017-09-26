import unittest
import os
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

GET_XML = os.path.join(TEST_ASSET_DIR, 'user_get.xml')
GET_EMPTY_XML = os.path.join(TEST_ASSET_DIR, 'user_get_empty.xml')
GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, 'user_get_by_id.xml')
UPDATE_XML = os.path.join(TEST_ASSET_DIR, 'user_update.xml')
ADD_XML = os.path.join(TEST_ASSET_DIR, 'user_add.xml')
POPULATE_WORKBOOKS_XML = os.path.join(TEST_ASSET_DIR, 'user_populate_workbooks.xml')
ADD_FAVORITE_XML = os.path.join(TEST_ASSET_DIR, 'user_add_favorite.xml')


class UserTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.users.baseurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_users, pagination_item = self.server.users.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual(2, len(all_users))

        self.assertTrue(any(user.id == 'dd2239f6-ddf1-4107-981a-4cf94e415794' for user in all_users))
        single_user = next(user for user in all_users if user.id == 'dd2239f6-ddf1-4107-981a-4cf94e415794')
        self.assertEqual('alice', single_user.name)
        self.assertEqual('Publisher', single_user.site_role)
        self.assertEqual('2016-08-16T23:17:06Z', format_datetime(single_user.last_login))

        self.assertTrue(any(user.id == '2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3' for user in all_users))
        single_user = next(user for user in all_users if user.id == '2a47bbf8-8900-4ebb-b0a4-2723bd7c46c3')
        self.assertEqual('Bob', single_user.name)
        self.assertEqual('Interactor', single_user.site_role)

    def test_get_empty(self):
        with open(GET_EMPTY_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_users, pagination_item = self.server.users.get()

        self.assertEqual(0, pagination_item.total_available)
        self.assertEqual([], all_users)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.users.get)

    def test_get_by_id(self):
        with open(GET_BY_ID_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/dd2239f6-ddf1-4107-981a-4cf94e415794', text=response_xml)
            single_user = self.server.users.get_by_id('dd2239f6-ddf1-4107-981a-4cf94e415794')

        self.assertEqual('dd2239f6-ddf1-4107-981a-4cf94e415794', single_user.id)
        self.assertEqual('alice', single_user.name)
        self.assertEqual('Alice', single_user.fullname)
        self.assertEqual('Publisher', single_user.site_role)
        self.assertEqual('ServerDefault', single_user.auth_setting)
        self.assertEqual('2016-08-16T23:17:06Z', format_datetime(single_user.last_login))
        self.assertEqual('local', single_user.domain_name)

    def test_get_by_id_missing_id(self):
        self.assertRaises(ValueError, self.server.users.get_by_id, '')

    def test_update(self):
        with open(UPDATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/dd2239f6-ddf1-4107-981a-4cf94e415794', text=response_xml)
            single_user = TSC.UserItem('test', 'Viewer')
            single_user._id = 'dd2239f6-ddf1-4107-981a-4cf94e415794'
            single_user.name = 'Cassie'
            single_user.fullname = 'Cassie'
            single_user.email = 'cassie@email.com'
            single_user = self.server.users.update(single_user)

        self.assertEqual('Cassie', single_user.name)
        self.assertEqual('Cassie', single_user.fullname)
        self.assertEqual('cassie@email.com', single_user.email)
        self.assertEqual('Viewer', single_user.site_role)

    def test_update_missing_id(self):
        single_user = TSC.UserItem('test', 'Interactor')
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.users.update, single_user)

    def test_remove(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + '/dd2239f6-ddf1-4107-981a-4cf94e415794', status_code=204)
            self.server.users.remove('dd2239f6-ddf1-4107-981a-4cf94e415794')

    def test_remove_missing_id(self):
        self.assertRaises(ValueError, self.server.users.remove, '')

    def test_add(self):
        with open(ADD_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl + '', text=response_xml)
            new_user = TSC.UserItem(name='Cassie', site_role='Viewer', auth_setting='ServerDefault')
            new_user = self.server.users.add(new_user)

        self.assertEqual('4cc4c17f-898a-4de4-abed-a1681c673ced', new_user.id)
        self.assertEqual('Cassie', new_user.name)
        self.assertEqual('Viewer', new_user.site_role)
        self.assertEqual('ServerDefault', new_user.auth_setting)

    def test_populate_workbooks(self):
        with open(POPULATE_WORKBOOKS_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/dd2239f6-ddf1-4107-981a-4cf94e415794/workbooks',
                  text=response_xml)
            single_user = TSC.UserItem('test', 'Interactor')
            single_user._id = 'dd2239f6-ddf1-4107-981a-4cf94e415794'
            self.server.users.populate_workbooks(single_user)

            workbook_list = list(single_user.workbooks)
            self.assertEqual('3cc6cd06-89ce-4fdc-b935-5294135d6d42', workbook_list[0].id)
            self.assertEqual('SafariSample', workbook_list[0].name)
            self.assertEqual('SafariSample', workbook_list[0].content_url)
            self.assertEqual(False, workbook_list[0].show_tabs)
            self.assertEqual(26, workbook_list[0].size)
            self.assertEqual('2016-07-26T20:34:56Z', format_datetime(workbook_list[0].created_at))
            self.assertEqual('2016-07-26T20:35:05Z', format_datetime(workbook_list[0].updated_at))
            self.assertEqual('ee8c6e70-43b6-11e6-af4f-f7b0d8e20760', workbook_list[0].project_id)
            self.assertEqual('default', workbook_list[0].project_name)
            self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', workbook_list[0].owner_id)
            self.assertEqual(set(['Safari', 'Sample']), workbook_list[0].tags)

    def test_populate_workbooks_missing_id(self):
        single_user = TSC.UserItem('test', 'Interactor')
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.users.populate_workbooks, single_user)
