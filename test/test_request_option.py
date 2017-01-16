import unittest
import os
import requests_mock
import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

PAGINATION_XML = os.path.join(TEST_ASSET_DIR, 'request_option_pagination.xml')
PAGE_NUMBER_XML = os.path.join(TEST_ASSET_DIR, 'request_option_page_number.xml')
PAGE_SIZE_XML = os.path.join(TEST_ASSET_DIR, 'request_option_page_size.xml')
FILTER_EQUALS = os.path.join(TEST_ASSET_DIR, 'request_option_filter_equals.xml')
FILTER_TAGS_IN = os.path.join(TEST_ASSET_DIR, 'request_option_filter_tags_in.xml')
FILTER_MULTIPLE = os.path.join(TEST_ASSET_DIR, 'request_option_filter_tags_in.xml')


class RequestOptionTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = '{0}/{1}'.format(self.server.sites.baseurl, self.server._site_id)

    def test_pagination(self):
        with open(PAGINATION_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/views?pageNumber=1&pageSize=10', text=response_xml)
            req_option = TSC.RequestOptions().page_size(10)
            all_views, pagination_item = self.server.views.get(req_option)

        self.assertEqual(1, pagination_item.page_number)
        self.assertEqual(10, pagination_item.page_size)
        self.assertEqual(33, pagination_item.total_available)
        self.assertEqual(10, len(all_views))

    def test_page_number(self):
        with open(PAGE_NUMBER_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/views?pageNumber=3', text=response_xml)
            req_option = TSC.RequestOptions().page_number(3)
            all_views, pagination_item = self.server.views.get(req_option)

        self.assertEqual(3, pagination_item.page_number)
        self.assertEqual(100, pagination_item.page_size)
        self.assertEqual(210, pagination_item.total_available)
        self.assertEqual(10, len(all_views))

    def test_page_size(self):
        with open(PAGE_SIZE_XML, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/views?pageSize=5', text=response_xml)
            req_option = TSC.RequestOptions().page_size(5)
            all_views, pagination_item = self.server.views.get(req_option)

        self.assertEqual(1, pagination_item.page_number)
        self.assertEqual(5, pagination_item.page_size)
        self.assertEqual(33, pagination_item.total_available)
        self.assertEqual(5, len(all_views))

    def test_filter_equals(self):
        with open(FILTER_EQUALS, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/workbooks?filter=name:eq:RESTAPISample', text=response_xml)
            req_option = TSC.RequestOptions()
            req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name,
                                             TSC.RequestOptions.Operator.Equals, 'RESTAPISample'))
            matching_workbooks, pagination_item = self.server.workbooks.get(req_option)

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual('RESTAPISample', matching_workbooks[0].name)
        self.assertEqual('RESTAPISample', matching_workbooks[1].name)

    def test_filter_tags_in(self):
        with open(FILTER_TAGS_IN, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/workbooks?filter=tags:in:[sample,safari,weather]', text=response_xml)
            req_option = TSC.RequestOptions()
            req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In,
                                             ['sample', 'safari', 'weather']))
            matching_workbooks, pagination_item = self.server.workbooks.get(req_option)

        self.assertEqual(3, pagination_item.total_available)
        self.assertEqual(set(['weather']), matching_workbooks[0].tags)
        self.assertEqual(set(['safari']), matching_workbooks[1].tags)
        self.assertEqual(set(['sample']), matching_workbooks[2].tags)

    def test_multiple_filter_options(self):
        with open(FILTER_MULTIPLE, 'rb') as f:
            response_xml = f.read().decode('utf-8')
        # To ensure that this is deterministic, run this a few times
        with requests_mock.mock() as m:
            # Sometimes pep8 requires you to do things you might not otherwise do
            url = ''.join((self.baseurl, '/workbooks?pageNumber=1&pageSize=100&',
                          'filter=name:eq:foo,tags:in:[sample,safari,weather]'))
            m.get(url, text=response_xml)
            req_option = TSC.RequestOptions()
            req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In,
                                             ['sample', 'safari', 'weather']))
            req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, 'foo'))
            for _ in range(100):
                matching_workbooks, pagination_item = self.server.workbooks.get(req_option)
                self.assertEqual(3, pagination_item.total_available)
