# encoding=utf-8
import unittest
import os
import requests_mock
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

GET_XML = os.path.join(TEST_ASSET_DIR, 'group_get.xml')
POPULATE_USERS = os.path.join(TEST_ASSET_DIR, 'group_populate_users.xml')
POPULATE_USERS_EMPTY = os.path.join(TEST_ASSET_DIR, 'group_populate_users_empty.xml')
ADD_USER = os.path.join(TEST_ASSET_DIR, 'group_add_user.xml')
ADD_USER_POPULATE = os.path.join(TEST_ASSET_DIR, 'group_users_added.xml')
CREATE_GROUP = os.path.join(TEST_ASSET_DIR, 'group_create.xml')
CREATE_GROUP_ASYNC = os.path.join(TEST_ASSET_DIR, 'group_create_async.xml')


class GroupTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.groups.baseurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_groups, pagination_item = self.server.groups.get()

        self.assertEqual(3, pagination_item.total_available)
        self.assertEqual('ef8b19c0-43b6-11e6-af50-63f5805dbe3c', all_groups[0].id)
        self.assertEqual('All Users', all_groups[0].name)
        self.assertEqual('local', all_groups[0].domain_name)

        self.assertEqual('e7833b48-c6f7-47b5-a2a7-36e7dd232758', all_groups[1].id)
        self.assertEqual('Another group', all_groups[1].name)
        self.assertEqual('local', all_groups[1].domain_name)

        self.assertEqual('86a66d40-f289-472a-83d0-927b0f954dc8', all_groups[2].id)
        self.assertEqual('TableauExample', all_groups[2].name)
        self.assertEqual('local', all_groups[2].domain_name)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.groups.get)

    def test_populate_users(self):
        with open(POPULATE_USERS, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users?pageNumber=1&pageSize=100',
                  text=response_xml, complete_qs=True)
            single_group = TSC.GroupItem(name='Test Group')
            single_group._id = 'e7833b48-c6f7-47b5-a2a7-36e7dd232758'
            self.server.groups.populate_users(single_group)

            self.assertEqual(1, len(list(single_group.users)))
            user = list(single_group.users).pop()
            self.assertEqual('dd2239f6-ddf1-4107-981a-4cf94e415794', user.id)
            self.assertEqual('alice', user.name)
            self.assertEqual('Publisher', user.site_role)
            self.assertEqual('2016-08-16T23:17:06Z', format_datetime(user.last_login))

    def test_delete(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758', status_code=204)
            self.server.groups.delete('e7833b48-c6f7-47b5-a2a7-36e7dd232758')

    def test_remove_user(self):
        with open(POPULATE_USERS, 'rb') as f:
            response_xml_populate = f.read().decode('utf-8')

        with open(POPULATE_USERS_EMPTY, 'rb') as f:
            response_xml_empty = f.read().decode('utf-8')

        with requests_mock.mock() as m:
            url = self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users' \
                                 '/dd2239f6-ddf1-4107-981a-4cf94e415794'

            m.delete(url, status_code=204)
            #  We register the get endpoint twice. The first time we have 1 user, the second we have 'removed' them.
            m.get(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users', text=response_xml_populate)

            single_group = TSC.GroupItem('test')
            single_group._id = 'e7833b48-c6f7-47b5-a2a7-36e7dd232758'
            self.server.groups.populate_users(single_group)
            self.assertEqual(1, len(list(single_group.users)))
            self.server.groups.remove_user(single_group, 'dd2239f6-ddf1-4107-981a-4cf94e415794')

            m.get(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users', text=response_xml_empty)
            self.assertEqual(0, len(list(single_group.users)))

    def test_add_user(self):
        with open(ADD_USER, 'rb') as f:
            response_xml_add = f.read().decode('utf-8')
        with open(ADD_USER_POPULATE, 'rb') as f:
            response_xml_populate = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users', text=response_xml_add)
            m.get(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users', text=response_xml_populate)
            single_group = TSC.GroupItem('test')
            single_group._id = 'e7833b48-c6f7-47b5-a2a7-36e7dd232758'

            self.server.groups.add_user(single_group, '5de011f8-5aa9-4d5b-b991-f462c8dd6bb7')
            self.server.groups.populate_users(single_group)
            self.assertEqual(1, len(list(single_group.users)))
            user = list(single_group.users).pop()
            self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', user.id)
            self.assertEqual('testuser', user.name)
            self.assertEqual('ServerAdministrator', user.site_role)

    def test_add_user_before_populating(self):
        with open(GET_XML, 'rb') as f:
            get_xml_response = f.read().decode('utf-8')
        with open(ADD_USER, 'rb') as f:
            add_user_response = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=get_xml_response)
            m.post('http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/groups/ef8b19c0-43b6-11e6-af50'
                   '-63f5805dbe3c/users', text=add_user_response)
            all_groups, pagination_item = self.server.groups.get()
            single_group = all_groups[0]
            self.server.groups.add_user(single_group, '5de011f8-5aa9-4d5b-b991-f462c8dd6bb7')

    def test_add_user_missing_user_id(self):
        with open(POPULATE_USERS, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users', text=response_xml)
            single_group = TSC.GroupItem(name='Test Group')
            single_group._id = 'e7833b48-c6f7-47b5-a2a7-36e7dd232758'
            self.server.groups.populate_users(single_group)

        self.assertRaises(ValueError, self.server.groups.add_user, single_group, '')

    def test_add_user_missing_group_id(self):
        single_group = TSC.GroupItem('test')
        single_group._users = []
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.groups.add_user, single_group,
                          '5de011f8-5aa9-4d5b-b991-f462c8dd6bb7')

    def test_remove_user_before_populating(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            m.delete('http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/groups/ef8b19c0-43b6-11e6-af50'
                     '-63f5805dbe3c/users/5de011f8-5aa9-4d5b-b991-f462c8dd6bb7',
                     text='ok')
            all_groups, pagination_item = self.server.groups.get()
            single_group = all_groups[0]
            self.server.groups.remove_user(single_group, '5de011f8-5aa9-4d5b-b991-f462c8dd6bb7')

    def test_remove_user_missing_user_id(self):
        with open(POPULATE_USERS, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/e7833b48-c6f7-47b5-a2a7-36e7dd232758/users', text=response_xml)
            single_group = TSC.GroupItem(name='Test Group')
            single_group._id = 'e7833b48-c6f7-47b5-a2a7-36e7dd232758'
            self.server.groups.populate_users(single_group)

        self.assertRaises(ValueError, self.server.groups.remove_user, single_group, '')

    def test_remove_user_missing_group_id(self):
        single_group = TSC.GroupItem('test')
        single_group._users = []
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.groups.remove_user, single_group,
                          '5de011f8-5aa9-4d5b-b991-f462c8dd6bb7')

    def test_create_group(self):
        with open(CREATE_GROUP, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            group_to_create = TSC.GroupItem(u'試供品')
            group = self.server.groups.create(group_to_create)
            self.assertEqual(group.name, u'試供品')
            self.assertEqual(group.id, '3e4a9ea0-a07a-4fe6-b50f-c345c8c81034')
