import pytest
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
            self.headers = {}
            self.encoding = None
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


def test_init_server_model_empty_throws():
    with pytest.raises(TypeError):
        server = TSC.Server()


def test_init_server_model_no_protocol_defaults_htt():
    server = TSC.Server("fake-url")


def test_init_server_model_valid_server_name_works():
    server = TSC.Server("http://fake-url")


def test_init_server_model_valid_https_server_name_works():
    # by default, it will just set the version to 2.3
    server = TSC.Server("https://fake-url")


def test_init_server_model_bad_server_name_not_version_check():
    server = TSC.Server("fake-url", use_server_version=False)


@mock.patch("requests.sessions.Session.get", side_effect=mocked_requests_get)
def test_init_server_model_bad_server_name_do_version_check(mock_get):
    server = TSC.Server("fake-url", use_server_version=True)


def test_init_server_model_bad_server_name_not_version_check_random_options():
    server = TSC.Server("fake-url", use_server_version=False, http_options={"foo": 1})


def test_init_server_model_bad_server_name_not_version_check_real_options():
    server = TSC.Server("fake-url", use_server_version=False, http_options={"verify": False})


def test_http_options_skip_ssl_works():
    http_options = {"verify": False}
    server = TSC.Server("http://fake-url")
    server.add_http_options(http_options)


def test_http_options_multiple_options_works():
    http_options = {"verify": False, "birdname": "Parrot"}
    server = TSC.Server("http://fake-url")
    server.add_http_options(http_options)


# ValueError: dictionary update sequence element #0 has length 1; 2 is required
def test_http_options_multiple_dicts_fails():
    http_options_1 = {"verify": False}
    http_options_2 = {"birdname": "Parrot"}
    server = TSC.Server("http://fake-url")
    with pytest.raises(ValueError):
        server.add_http_options([http_options_1, http_options_2])


# TypeError: cannot convert dictionary update sequence element #0 to a sequence
def test_http_options_not_sequence_fails():
    server = TSC.Server("http://fake-url")
    with pytest.raises(ValueError):
        server.add_http_options({1, 2, 3})


def test_validate_connection_http():
    url = "http://cookies.com"
    server = TSC.Server(url)
    server.validate_connection_settings()
    assert url == server.server_address


def test_validate_connection_https():
    url = "https://cookies.com"
    server = TSC.Server(url)
    server.validate_connection_settings()
    assert url == server.server_address


def test_validate_connection_no_protocol():
    url = "cookies.com"
    fixed_url = "http://cookies.com"
    server = TSC.Server(url)
    server.validate_connection_settings()
    assert fixed_url == server.server_address


test_header = {"x-test": "true"}


@pytest.fixture
def session_factory() -> requests.Session:
    session = requests.session()
    session.headers.update(test_header)
    return session


def test_session_factory_adds_headers(session_factory):
    test_request_bin = "http://capture-this-with-mock.com"
    with requests_mock.mock() as m:
        m.get(url="http://capture-this-with-mock.com/api/2.4/serverInfo", request_headers=test_header)
        server = TSC.Server(test_request_bin, use_server_version=True, session_factory=lambda: session_factory)
