import unittest
import os
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

ADD_TAGS_XML = os.path.join(TEST_ASSET_DIR, 'view_add_tags.xml')
GET_XML = os.path.join(TEST_ASSET_DIR, 'view_get.xml')
GET_XML_USAGE = os.path.join(TEST_ASSET_DIR, 'view_get_usage.xml')
POPULATE_PREVIEW_IMAGE = os.path.join(TEST_ASSET_DIR, 'Sample View Image.png')
POPULATE_PDF = os.path.join(TEST_ASSET_DIR, 'populate_pdf.pdf')
POPULATE_CSV = os.path.join(TEST_ASSET_DIR, 'populate_csv.csv')
UPDATE_XML = os.path.join(TEST_ASSET_DIR, 'workbook_update.xml')


class ViewTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.server.version = '2.7'

        # Fake sign in
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.views.baseurl
        self.siteurl = self.server.views.siteurl

    def test_get(self):
        with open(GET_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_views, pagination_item = self.server.views.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual('d79634e1-6063-4ec9-95ff-50acbf609ff5', all_views[0].id)
        self.assertEqual('ENDANGERED SAFARI', all_views[0].name)
        self.assertEqual('SafariSample/sheets/ENDANGEREDSAFARI', all_views[0].content_url)
        self.assertEqual('3cc6cd06-89ce-4fdc-b935-5294135d6d42', all_views[0].workbook_id)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', all_views[0].owner_id)
        self.assertEqual('5241e88d-d384-4fd7-9c2f-648b5247efc5', all_views[0].project_id)

        self.assertEqual('fd252f73-593c-4c4e-8584-c032b8022adc', all_views[1].id)
        self.assertEqual('Overview', all_views[1].name)
        self.assertEqual('Superstore/sheets/Overview', all_views[1].content_url)
        self.assertEqual('6d13b0ca-043d-4d42-8c9d-3f3313ea3a00', all_views[1].workbook_id)
        self.assertEqual('5de011f8-5aa9-4d5b-b991-f462c8dd6bb7', all_views[1].owner_id)
        self.assertEqual('5b534f74-3226-11e8-b47a-cb2e00f738a3', all_views[1].project_id)

    def test_get_with_usage(self):
        with open(GET_XML_USAGE, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + "?includeUsageStatistics=true", text=response_xml)
            all_views, pagination_item = self.server.views.get(usage=True)

        self.assertEqual('d79634e1-6063-4ec9-95ff-50acbf609ff5', all_views[0].id)
        self.assertEqual(7, all_views[0].total_views)
        self.assertEqual('fd252f73-593c-4c4e-8584-c032b8022adc', all_views[1].id)
        self.assertEqual(13, all_views[1].total_views)

    def test_get_with_usage_and_filter(self):
        with open(GET_XML_USAGE, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + "?includeUsageStatistics=true&filter=name:in:[foo,bar]", text=response_xml)
            options = TSC.RequestOptions()
            options.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.In,
                                          ["foo", "bar"]))
            all_views, pagination_item = self.server.views.get(req_options=options, usage=True)

        self.assertEqual("ENDANGERED SAFARI", all_views[0].name)
        self.assertEqual(7, all_views[0].total_views)
        self.assertEqual("Overview", all_views[1].name)
        self.assertEqual(13, all_views[1].total_views)

    def test_get_before_signin(self):
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.views.get)

    def test_populate_preview_image(self):
        with open(POPULATE_PREVIEW_IMAGE, 'rb') as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.siteurl + '/workbooks/3cc6cd06-89ce-4fdc-b935-5294135d6d42/'
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

    def test_populate_image(self):
        with open(POPULATE_PREVIEW_IMAGE, 'rb') as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5/image', content=response)
            single_view = TSC.ViewItem()
            single_view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
            self.server.views.populate_image(single_view)
            self.assertEqual(response, single_view.image)

    def test_populate_image_high_resolution(self):
        with open(POPULATE_PREVIEW_IMAGE, 'rb') as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5/image?resolution=high', content=response)
            single_view = TSC.ViewItem()
            single_view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
            req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High)
            self.server.views.populate_image(single_view, req_option)
            self.assertEqual(response, single_view.image)

    def test_populate_pdf(self):
        with open(POPULATE_PDF, 'rb') as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5/pdf?type=letter&orientation=portrait',
                  content=response)
            single_view = TSC.ViewItem()
            single_view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'

            size = TSC.PDFRequestOptions.PageType.Letter
            orientation = TSC.PDFRequestOptions.Orientation.Portrait
            req_option = TSC.PDFRequestOptions(size, orientation)

            self.server.views.populate_pdf(single_view, req_option)
            self.assertEqual(response, single_view.pdf)

    def test_populate_csv(self):
        with open(POPULATE_CSV, 'rb') as f:
            response = f.read()
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5/data', content=response)
            single_view = TSC.ViewItem()
            single_view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
            self.server.views.populate_csv(single_view)

            csv_file = b"".join(single_view.csv)
            self.assertEqual(response, csv_file)

    def test_populate_image_missing_id(self):
        single_view = TSC.ViewItem()
        single_view._id = None
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.views.populate_image, single_view)

    def test_update_tags(self):
        with open(ADD_TAGS_XML, 'rb') as f:
            add_tags_xml = f.read().decode('utf-8')
        with open(UPDATE_XML, 'rb') as f:
            update_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5/tags', text=add_tags_xml)
            m.delete(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5/tags/b', status_code=204)
            m.delete(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5/tags/d', status_code=204)
            m.put(self.baseurl + '/d79634e1-6063-4ec9-95ff-50acbf609ff5', text=update_xml)
            single_view = TSC.ViewItem()
            single_view._id = 'd79634e1-6063-4ec9-95ff-50acbf609ff5'
            single_view._initial_tags.update(['a', 'b', 'c', 'd'])
            single_view.tags.update(['a', 'c', 'e'])
            updated_view = self.server.views.update(single_view)

        self.assertEqual(single_view.tags, updated_view.tags)
        self.assertEqual(single_view._initial_tags, updated_view._initial_tags)
