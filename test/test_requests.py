import unittest

import requests
import requests_mock

import tableauserverclient as TSC

from tableauserverclient.server.endpoint.exceptions import InternalServerError


class RequestTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake sign in
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

        self.baseurl = self.server.workbooks.baseurl

    def test_make_get_request(self):
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            opts = TSC.RequestOptions(pagesize=13, pagenumber=13)
            resp = self.server.workbooks._make_request(requests.get,
                                                       url,
                                                       content=None,
                                                       request_object=opts,
                                                       auth_token='j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM',
                                                       content_type='text/xml')

            self.assertEqual(resp.request.query, 'pagenumber=13&pagesize=13')
            self.assertEqual(resp.request.headers['x-tableau-auth'], 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM')
            self.assertEqual(resp.request.headers['content-type'], 'text/xml')

    def test_make_post_request(self):
        with requests_mock.mock() as m:
            m.post(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            resp = self.server.workbooks._make_request(requests.post,
                                                       url,
                                                       content=b'1337',
                                                       request_object=None,
                                                       auth_token='j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM',
                                                       content_type='multipart/mixed')
            self.assertEqual(resp.request.headers['x-tableau-auth'], 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM')
            self.assertEqual(resp.request.headers['content-type'], 'multipart/mixed')
            self.assertEqual(resp.request.body, b'1337')

    # Test that 500 server errors are handled properly
    def test_internal_server_error(self):
        self.server.version = "3.2"
        server_response = "500: Internal Server Error"
        with requests_mock.mock() as m:
            m.register_uri('GET', self.server.server_info.baseurl, status_code=500, text=server_response)
            self.assertRaisesRegexp(InternalServerError, server_response, self.server.server_info.get)
