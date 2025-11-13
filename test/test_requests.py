from urllib.parse import parse_qs

import pytest
import requests
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import InternalServerError, NonXMLResponseError


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_make_get_request(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
        opts = TSC.RequestOptions(pagesize=13, pagenumber=15)
        resp = server.workbooks.get_request(url, request_object=opts)

        query = parse_qs(resp.request.query)
        assert query.get("pagesize") == ["13"]
        assert query.get("pagenumber") == ["15"]


def test_make_post_request(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.post(requests_mock.ANY)
        url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
        resp = server.workbooks._make_request(
            requests.post,
            url,
            content=b"1337",
            auth_token="j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM",
            content_type="multipart/mixed",
        )
        assert resp.request.headers["x-tableau-auth"] == "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        assert resp.request.headers["content-type"] == "multipart/mixed"
        assert "Tableau Server Client" in resp.request.headers["user-agent"]
        assert resp.request.body == b"1337"


# Test that 500 server errors are handled properly
def test_internal_server_error(server: TSC.Server) -> None:
    server.version = "3.2"
    server_response = "500: Internal Server Error"
    with requests_mock.mock() as m:
        m.register_uri("GET", server.server_info.baseurl, status_code=500, text=server_response)
        with pytest.raises(InternalServerError, match=server_response):
            server.server_info.get()


# Test that non-xml server errors are handled properly
def test_non_xml_error(server: TSC.Server) -> None:
    server.version = "3.2"
    server_response = "this is not xml"
    with requests_mock.mock() as m:
        m.register_uri("GET", server.server_info.baseurl, status_code=499, text=server_response)
        with pytest.raises(NonXMLResponseError, match=server_response):
            server.server_info.get()
