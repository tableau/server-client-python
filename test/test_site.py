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
        self.server.version = "3.10"

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
        self.assertEqual('dad65087-b08b-4603-af4e-2887b8aafc67', all_sites[0].id)
        self.assertEqual('Active', all_sites[0].state)
        self.assertEqual('Default', all_sites[0].name)
        self.assertEqual('ContentOnly', all_sites[0].admin_mode)
        self.assertEqual(False, all_sites[0].revision_history_enabled)
        self.assertEqual(True, all_sites[0].subscribe_others_enabled)
        self.assertEqual(25, all_sites[0].revision_limit)
        self.assertEqual(None, all_sites[0].num_users)
        self.assertEqual(None, all_sites[0].storage)
        self.assertEqual(True, all_sites[0].cataloging_enabled)
        self.assertEqual(False, all_sites[0].editing_flows_enabled)
        self.assertEqual(False, all_sites[0].scheduling_flows_enabled)
        self.assertEqual(True, all_sites[0].allow_subscription_attachments)
        self.assertEqual('6b7179ba-b82b-4f0f-91ed-812074ac5da6', all_sites[1].id)
        self.assertEqual('Active', all_sites[1].state)
        self.assertEqual('Samples', all_sites[1].name)
        self.assertEqual('ContentOnly', all_sites[1].admin_mode)
        self.assertEqual(False, all_sites[1].revision_history_enabled)
        self.assertEqual(True, all_sites[1].subscribe_others_enabled)
        self.assertEqual(False, all_sites[1].guest_access_enabled)
        self.assertEqual(True, all_sites[1].cache_warmup_enabled)
        self.assertEqual(True, all_sites[1].commenting_enabled)
        self.assertEqual(True, all_sites[1].cache_warmup_enabled)
        self.assertEqual(False, all_sites[1].request_access_enabled)
        self.assertEqual(True, all_sites[1].run_now_enabled)
        self.assertEqual(1, all_sites[1].tier_explorer_capacity)
        self.assertEqual(2, all_sites[1].tier_creator_capacity)
        self.assertEqual(1, all_sites[1].tier_viewer_capacity)
        self.assertEqual(False, all_sites[1].flows_enabled)
        self.assertEqual(None, all_sites[1].data_acceleration_mode)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.sites.get)

    def test_get_by_id(self):
        with open(GET_BY_ID_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/dad65087-b08b-4603-af4e-2887b8aafc67', text=response_xml)
            single_site = self.server.sites.get_by_id('dad65087-b08b-4603-af4e-2887b8aafc67')

        self.assertEqual('dad65087-b08b-4603-af4e-2887b8aafc67', single_site.id)
        self.assertEqual('Active', single_site.state)
        self.assertEqual('Default', single_site.name)
        self.assertEqual('ContentOnly', single_site.admin_mode)
        self.assertEqual(False, single_site.revision_history_enabled)
        self.assertEqual(True, single_site.subscribe_others_enabled)
        self.assertEqual(False, single_site.disable_subscriptions)
        self.assertEqual(False, single_site.data_alerts_enabled)
        self.assertEqual(False, single_site.commenting_mentions_enabled)
        self.assertEqual(True, single_site.catalog_obfuscation_enabled)

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
                                       data_acceleration_mode='disable', flow_auto_save_enabled=True,
                                       web_extraction_enabled=False, metrics_content_type_enabled=True,
                                       notify_site_admins_on_throttle=False, authoring_enabled=True,
                                       custom_subscription_email_enabled=True,
                                       custom_subscription_email='test@test.com',
                                       custom_subscription_footer_enabled=True,
                                       custom_subscription_footer='example_footer', ask_data_mode='EnabledByDefault',
                                       named_sharing_enabled=False, mobile_biometrics_enabled=True,
                                       sheet_image_enabled=False, derived_permissions_enabled=True,
                                       user_visibility_mode='FULL', use_default_time_zone=False,
                                       time_zone='America/Los_Angeles', auto_suspend_refresh_enabled=True,
                                       auto_suspend_refresh_inactivity_window=55)
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
        self.assertEqual('disable', single_site.data_acceleration_mode)
        self.assertEqual(True, single_site.flows_enabled)
        self.assertEqual(True, single_site.cataloging_enabled)
        self.assertEqual(True, single_site.flow_auto_save_enabled)
        self.assertEqual(False, single_site.web_extraction_enabled)
        self.assertEqual(True, single_site.metrics_content_type_enabled)
        self.assertEqual(False, single_site.notify_site_admins_on_throttle)
        self.assertEqual(True, single_site.authoring_enabled)
        self.assertEqual(True, single_site.custom_subscription_email_enabled)
        self.assertEqual('test@test.com', single_site.custom_subscription_email)
        self.assertEqual(True, single_site.custom_subscription_footer_enabled)
        self.assertEqual('example_footer', single_site.custom_subscription_footer)
        self.assertEqual('EnabledByDefault', single_site.ask_data_mode)
        self.assertEqual(False, single_site.named_sharing_enabled)
        self.assertEqual(True, single_site.mobile_biometrics_enabled)
        self.assertEqual(False, single_site.sheet_image_enabled)
        self.assertEqual(True, single_site.derived_permissions_enabled)
        self.assertEqual('FULL', single_site.user_visibility_mode)
        self.assertEqual(False, single_site.use_default_time_zone)
        self.assertEqual('America/Los_Angeles', single_site.time_zone)
        self.assertEqual(True, single_site.auto_suspend_refresh_enabled)
        self.assertEqual(55, single_site.auto_suspend_refresh_inactivity_window)

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

    def test_encrypt(self):
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/0626857c-1def-4503-a7d8-7907c3ff9d9f/encrypt-extracts', status_code=200)
            self.server.sites.encrypt_extracts('0626857c-1def-4503-a7d8-7907c3ff9d9f')

    def test_recrypt(self):
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/0626857c-1def-4503-a7d8-7907c3ff9d9f/reencrypt-extracts', status_code=200)
            self.server.sites.re_encrypt_extracts('0626857c-1def-4503-a7d8-7907c3ff9d9f')

    def test_decrypt(self):
        with requests_mock.mock() as m:
            m.post(self.baseurl + '/0626857c-1def-4503-a7d8-7907c3ff9d9f/decrypt-extracts', status_code=200)
            self.server.sites.decrypt_extracts('0626857c-1def-4503-a7d8-7907c3ff9d9f')
