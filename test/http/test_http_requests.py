import tableauserverclient as TSC
import unittest
import requests
import requests_mock

from unittest import mock
from requests.exceptions import MissingSchema


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, status_code):
            self.content = (
                "<xml>"
                "<version version='0.31'>"
                "<api_version>0.31</api_version>"
                "<server_api_version>0.31</server_api_version>"
                "<product_version>2022.3</product_version>"
                "</version>"
                "</xml>"
            )
            self.status_code = status_code

    return MockResponse(200)


class ServerTests(unittest.TestCase):
    def test_init_server_model_empty_throws(self):
        with self.assertRaises(TypeError):
            server = TSC.Server()

    def test_init_server_model_no_protocol_defaults_htt(self):
        server = TSC.Server("fake-url")

    def test_init_server_model_valid_server_name_works(self):
        server = TSC.Server("http://fake-url")

    def test_init_server_model_valid_https_server_name_works(self):
        # by default, it will just set the version to 2.3
        server = TSC.Server("https://fake-url")

    def test_init_server_model_bad_server_name_not_version_check(self):
        server = TSC.Server("fake-url", use_server_version=False)

    def test_init_server_model_bad_server_name_do_version_check(self):
        with self.assertRaises(requests.exceptions.ConnectionError):
            server = TSC.Server("fake-url", use_server_version=True)

    def test_init_server_model_bad_server_name_not_version_check_random_options(self):
        # with self.assertRaises(MissingSchema):
        server = TSC.Server("fake-url", use_server_version=False, http_options={"foo": 1})

    def test_init_server_model_bad_server_name_not_version_check_real_options(self):
        # with self.assertRaises(ValueError):
        server = TSC.Server("fake-url", use_server_version=False, http_options={"verify": False})

    def test_http_options_skip_ssl_works(self):
        http_options = {"verify": False}
        server = TSC.Server("http://fake-url")
        server.add_http_options(http_options)

    def test_http_options_multiple_options_works(self):
        http_options = {"verify": False, "birdname": "Parrot"}
        server = TSC.Server("http://fake-url")
        server.add_http_options(http_options)

    # ValueError: dictionary update sequence element #0 has length 1; 2 is required
    def test_http_options_multiple_dicts_fails(self):
        http_options_1 = {"verify": False}
        http_options_2 = {"birdname": "Parrot"}
        server = TSC.Server("http://fake-url")
        with self.assertRaises(ValueError):
            server.add_http_options([http_options_1, http_options_2])

    # TypeError: cannot convert dictionary update sequence element #0 to a sequence
    def test_http_options_not_sequence_fails(self):
        server = TSC.Server("http://fake-url")
        with self.assertRaises(ValueError):
            server.add_http_options({1, 2, 3})

    def test_validate_connection_http(self):
        url = "http://cookies.com"
        server = TSC.Server(url)
        server.validate_server_connection()
        self.assertEqual(url, server.server_address)

    def test_validate_connection_https(self):
        url = "https://cookies.com"
        server = TSC.Server(url)
        server.validate_server_connection()
        self.assertEqual(url, server.server_address)

    def test_validate_connection_no_protocol(self):
        url = "cookies.com"
        fixed_url = "http://cookies.com"
        server = TSC.Server(url)
        server.validate_server_connection()
        self.assertEqual(fixed_url, server.server_address)


class SessionTests(unittest.TestCase):
    test_header = {"x-test": "true"}

    @staticmethod
    def session_factory():
        session = requests.session()
        session.headers.update(SessionTests.test_header)
        return session

    def test_session_factory_adds_headers(self):
        test_request_bin = "http://capture-this-with-mock.com"
        with requests_mock.mock() as m:
            m.get(url="http://capture-this-with-mock.com/api/2.4/serverInfo", request_headers=SessionTests.test_header)
            server = TSC.Server(test_request_bin, use_server_version=True, session_factory=SessionTests.session_factory)
