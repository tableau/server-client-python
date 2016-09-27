import unittest
import os
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

GET_XML = os.path.join(TEST_ASSET_DIR, 'view_get.xml')
POPULATE_PREVIEW_IMAGE = os.path.join(TEST_ASSET_DIR, 'Sample View Image.png')


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake sign in
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.views.baseurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/views', text=response_xml)
            all_views, pagination_item = self.server.views.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual('d79634e1-6063-4ec9-95ff-50acbf609ff5', all_views[0].id)
        self.assertEqual('ENDANGERED SAFARI', all_views[0].name)
        self.assertEqual('SafariSample/sheets/ENDANGEREDSAFARI', all_views[0].content_url)
        self.assertEqual('3cc6cd06-89ce-4fdc-b935-5294135d6d42', all_views[0].workbook_id)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', all_views[0].owner_id)

        self.assertEqual('fd252f73-593c-4c4e-8584-c032b8022adc', all_views[1].id)
        self.assertEqual('Overview', all_views[1].name)
        self.assertEqual('Superstore/sheets/Overview', all_views[1].content_url)
        self.assertEqual('6d13b0ca-043d-4d42-8c9d-3f3313ea3a00', all_views[1].workbook_id)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', all_views[1].owner_id)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.views.get)

    def test_populate_preview_image(self):
        with open(POPULATE_PREVIEW_IMAGE, 'rb') as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/workbooks/3cc6cd06-89ce-4fdc-b935-5294135d6d42/'
                  'views/d79634e1-6063-4ec9-95ff-50acbf609ff5/previewImage', content=response)
            single_view = TSC.ViewItem()
            single_view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
            single_view._workbook_id = '3cc6cd06-89ce-4fdc-b935-5294135d6d42'
            self.server.views.populate_preview_image(single_view)
        self.assertEqual(response, single_view.preview_image)

    def test_populate_preview_image_missing_id(self):
        single_view = TSC.ViewItem()
        single_view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.views.populate_preview_image, single_view)

        single_view._id = None
        single_view._workbook_id = '3cc6cd06-89ce-4fdc-b935-5294135d6d42'
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.views.populate_preview_image, single_view)
