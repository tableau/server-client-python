import unittest
import os.path
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

GET_XML = os.path.join(TEST_ASSET_DIR, 'site_get.xml')
GET_BY_ID_XML = os.path.join(TEST_ASSET_DIR, 'site_get_by_id.xml')
GET_BY_NAME_XML = os.path.join(TEST_ASSET_DIR, 'site_get_by_name.xml')
UPDATE_XML = os.path.join(TEST_ASSET_DIR, 'site_update.xml')
CREATE_XML = os.path.join(TEST_ASSET_DIR, 'site_create.xml')


class SiteTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'
        self.server._site_id = '0626857c-1def-4503-a7d8-7907c3ff9d9f'
        self.baseurl = self.server.sites.baseurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_sites, pagination_item = self.server.sites.get()

        self.assertEqual(2, pagination_item.total_available)
        site1 = all_sites[0]
        site2 = all_sites[1]

        self.assertEqual('684a12a0-de63-413e-a711-0f31c60f7239', site1.id)
        self.assertEqual('Default', site1.name)
        self.assertEqual('', site1.content_url)
        self.assertEqual('ContentAndUsers', site1.admin_mode)
        self.assertEqual(6, site1.user_quota)
        self.assertEqual(False, site1.disable_subscriptions)
        self.assertEqual('Active', site1.state)
        self.assertEqual(True, site1.revision_history_enabled)
        self.assertEqual(25, site1.revision_limit)
        self.assertEqual(True, site1.subscribe_others_enabled)
        self.assertEqual(True, site1.guest_access_enabled)
        self.assertEqual(True, site1.cache_warmup_enabled)
        self.assertEqual(True, site1.commenting_enabled)
        self.assertEqual(True, site1.flows_enabled)
        self.assertEqual("disabled", site1.extract_encryption_mode)
        self.assertEqual("disable", site1.materialized_views_mode)

        self.assertEqual('d90660db-058f-4b1d-99f3-12c8217601f0', site2.id)
        self.assertEqual('site1', site2.name)
        self.assertEqual('site1', site2.content_url)
        self.assertEqual('ContentOnly', site2.admin_mode)
        self.assertEqual(25000, site2.storage_quota)
        self.assertEqual(True, site2.disable_subscriptions)
        self.assertEqual('Suspended', site2.state)
        self.assertEqual(False, site2.revision_history_enabled)
        self.assertEqual(2, site2.revision_limit)
        self.assertEqual(False, site2.subscribe_others_enabled)
        self.assertEqual(False, site2.guest_access_enabled)
        self.assertEqual(False, site2.cache_warmup_enabled)
        self.assertEqual(False, site2.commenting_enabled)
        self.assertEqual(False, site2.flows_enabled)
        self.assertEqual("enable_all", site2.materialized_views_mode)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.sites.get)

    def test_get_by_id(self):
        with open(GET_BY_ID_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/dad65087-b08b-4603-af4e-2887b8aafc67?includeUsage=True', text=response_xml)
            single_site = self.server.sites.get_by_id('dad65087-b08b-4603-af4e-2887b8aafc67', include_usage=True)

        self.assertEqual('d90660db-058f-4b1d-99f3-12c8217601f0', single_site.id)
        self.assertEqual('site1', single_site.name)
        self.assertEqual('site1', single_site.content_url)
        self.assertEqual('ContentAndUsers', single_site.admin_mode)
        self.assertEqual(6, single_site.user_quota)
        self.assertEqual(25000, single_site.storage_quota)
        self.assertEqual(False, single_site.disable_subscriptions)
        self.assertEqual('Active', single_site.state)
        self.assertEqual(True, single_site.revision_history_enabled)
        self.assertEqual(2, single_site.revision_limit)
        self.assertEqual(True, single_site.subscribe_others_enabled)
        self.assertEqual(True, single_site.guest_access_enabled)
        self.assertEqual(True, single_site.cache_warmup_enabled)
        self.assertEqual(True, single_site.commenting_enabled)
        self.assertEqual(True, single_site.flows_enabled)
        self.assertEqual('disabled', single_site.extract_encryption_mode)
        self.assertEqual('disable', single_site.materialized_views_mode)
        self.assertEqual(8, single_site.num_users)
        self.assertEqual(5, single_site.num_creators)
        self.assertEqual(1, single_site.num_explorers)
        self.assertEqual(2, single_site.num_viewers)
        self.assertEqual(9, single_site.storage)

    def test_get_by_id_missing_id(self):
        self.assertRaises(ValueError, self.server.sites.get_by_id, '')

    def test_get_by_name(self):
        with open(GET_BY_NAME_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/testsite?key=name', text=response_xml)
            single_site = self.server.sites.get_by_name('testsite')

        self.assertEqual('dad65087-b08b-4603-af4e-2887b8aafc67', single_site.id)
        self.assertEqual('Active', single_site.state)
        self.assertEqual('testsite', single_site.name)
        self.assertEqual('ContentOnly', single_site.admin_mode)
        self.assertEqual(False, single_site.revision_history_enabled)
        self.assertEqual(True, single_site.subscribe_others_enabled)
        self.assertEqual(False, single_site.disable_subscriptions)

    def test_get_by_name_missing_name(self):
        self.assertRaises(ValueError, self.server.sites.get_by_name, '')

    def test_update(self):
        with open(UPDATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/6b7179ba-b82b-4f0f-91ed-812074ac5da6', text=response_xml)
            single_site = TSC.SiteItem(name='Tableau', content_url='tableau',
                                       admin_mode=TSC.SiteItem.AdminMode.ContentAndUsers,
                                       user_quota=15, storage_quota=1000,
                                       disable_subscriptions=True, revision_history_enabled=False,
                                       materialized_views_mode='disable')
            single_site._id = '6b7179ba-b82b-4f0f-91ed-812074ac5da6'
            single_site = self.server.sites.update(single_site)

        self.assertEqual('6b7179ba-b82b-4f0f-91ed-812074ac5da6', single_site.id)
        self.assertEqual('tableau', single_site.content_url)
        self.assertEqual('Suspended', single_site.state)
        self.assertEqual('Tableau', single_site.name)
        self.assertEqual('ContentAndUsers', single_site.admin_mode)
        self.assertEqual(True, single_site.revision_history_enabled)
        self.assertEqual(13, single_site.revision_limit)
        self.assertEqual(True, single_site.disable_subscriptions)
        self.assertEqual(15, single_site.user_quota)
        self.assertEqual('disable', single_site.materialized_views_mode)

    def test_update_missing_id(self):
        single_site = TSC.SiteItem('test', 'test')
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.sites.update, single_site)

    def test_create(self):
        with open(CREATE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            new_site = TSC.SiteItem(name='Tableau', content_url='tableau',
                                    admin_mode=TSC.SiteItem.AdminMode.ContentAndUsers, user_quota=15,
                                    storage_quota=1000, disable_subscriptions=True)
            new_site = self.server.sites.create(new_site)

        self.assertEqual('0626857c-1def-4503-a7d8-7907c3ff9d9f', new_site.id)
        self.assertEqual('tableau', new_site.content_url)
        self.assertEqual('Tableau', new_site.name)
        self.assertEqual('Active', new_site.state)
        self.assertEqual('ContentAndUsers', new_site.admin_mode)
        self.assertEqual(False, new_site.revision_history_enabled)
        self.assertEqual(True, new_site.subscribe_others_enabled)
        self.assertEqual(True, new_site.disable_subscriptions)
        self.assertEqual(15, new_site.user_quota)

    def test_delete(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + '/0626857c-1def-4503-a7d8-7907c3ff9d9f', status_code=204)
            self.server.sites.delete('0626857c-1def-4503-a7d8-7907c3ff9d9f')

    def test_delete_missing_id(self):
        self.assertRaises(ValueError, self.server.sites.delete, '')
