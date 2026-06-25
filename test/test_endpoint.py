from pathlib import Path
import pytest
import requests

import tableauserverclient as TSC
from tableauserverclient.server.endpoint import Endpoint
from tableauserverclient.server.endpoint.exceptions import (
    FailedSignInError,
    NonXMLResponseError,
    ServerResponseError,
)

import requests_mock

ASSETS = Path(__file__).parent / "assets"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvS"

    return server


def test_fallback_request_logic(server: TSC.Server) -> None:
    url = "http://test/"
    endpoint = Endpoint(server)
    with requests_mock.mock() as m:
        m.get(url)
        response = endpoint.get_request(url=url)
        assert response is not None


def test_user_friendly_request_returns(server: TSC.Server) -> None:
    url = "http://test/"
    endpoint = Endpoint(server)
    with requests_mock.mock() as m:
        m.get(url)
        response = endpoint.send_request_while_show_progress_threaded(
            endpoint.parent_srv.session.get, url=url, request_timeout=2
        )
        assert response is not None


def test_blocking_request_raises_request_error(server: TSC.Server) -> None:
    with pytest.raises(requests.exceptions.ConnectionError):
        url = "http://test/"
        endpoint = Endpoint(server)
        response = endpoint._blocking_request(endpoint.parent_srv.session.get, url=url)
        assert response is not None


def test_get_request_stream(server: TSC.Server) -> None:
    url = "http://test/"
    endpoint = Endpoint(server)
    with requests_mock.mock() as m:
        m.get(url, headers={"Content-Type": "application/octet-stream"})
        response = endpoint.get_request(url, parameters={"stream": True})

        assert response._content_consumed is False


def test_binary_log_truncated(server: TSC.Server) -> None:
    class FakeResponse:
        headers = {"Content-Type": "application/octet-stream"}
        content = b"\x1337" * 1000
        status_code = 200

    endpoint = Endpoint(server)
    server_response = FakeResponse()
    log = endpoint.log_response_safely(server_response)  # type: ignore
    assert log.find("[Truncated File Contents]") > 0


def test_set_user_agent_from_options_headers(server: TSC.Server) -> None:
    params = {"User-Agent": "1", "headers": {"User-Agent": "2"}}
    result = Endpoint.set_user_agent(params)
    # it should use the value under 'headers' if more than one is given
    print(result)
    print(result["headers"]["User-Agent"])
    assert result["headers"]["User-Agent"] == "2"


def test_set_user_agent_from_options(server: TSC.Server) -> None:
    params = {"headers": {"User-Agent": "2"}}
    result = Endpoint.set_user_agent(params)
    assert result["headers"]["User-Agent"] == "2"


def test_set_user_agent_when_blank(server: TSC.Server) -> None:
    params = {"headers": {}}  # type: ignore
    result = Endpoint.set_user_agent(params)
    assert result["headers"]["User-Agent"].startswith("Tableau Server Client")


# --- ServerResponseError / FailedSignInError exception parsing (issue #1083) ---

NS = {"t": "http://tableau.com/api"}

STANDARD_ERROR_XML = b"""<?xml version='1.0' encoding='UTF-8'?>
<tsResponse xmlns="http://tableau.com/api">
  <error code="401002">
    <summary>Unauthorized Access</summary>
    <detail>Invalid credentials were provided.</detail>
  </error>
</tsResponse>"""

NO_ERROR_ELEMENT_XML = b"""<?xml version='1.0' encoding='UTF-8'?>
<tsResponse xmlns="http://tableau.com/api">
  <message>Something went wrong but with no error element</message>
</tsResponse>"""

NOT_XML_CONTENT = b"Internal Server Error (not XML at all)"


def test_server_response_error_standard_xml():
    """Standard XML with a t:error element parses code/summary/detail correctly."""
    err = ServerResponseError.from_response(STANDARD_ERROR_XML, NS, "http://test/")
    assert err.code == "401002"
    assert "Unauthorized" in err.summary
    assert "Invalid credentials" in err.detail


def test_server_response_error_no_error_element_does_not_raise():
    """XML without a t:error element must not raise AttributeError (issue #1083)."""
    err = ServerResponseError.from_response(NO_ERROR_ELEMENT_XML, NS, "http://test/")
    assert err.code == ""
    # The raw XML content should appear in summary/detail as the fallback
    assert "Something went wrong" in err.summary or len(err.summary) > 0


def test_server_response_error_not_xml_raises_parse_error():
    """Non-XML content causes fromstring to raise a ParseError (not AttributeError)."""
    import xml.etree.ElementTree as ET

    with pytest.raises(ET.ParseError):
        ServerResponseError.from_response(NOT_XML_CONTENT, NS, "http://test/")


def test_failed_sign_in_error_no_error_element_does_not_raise():
    """FailedSignInError shares from_response — same None guard must apply."""
    err = FailedSignInError.from_response(NO_ERROR_ELEMENT_XML, NS, "http://test/")
    assert err.code == ""
    assert isinstance(err, FailedSignInError)


def test_server_response_error_missing_summary_and_detail():
    """XML with t:error but missing summary/detail children falls back gracefully."""
    xml = b"""<?xml version='1.0' encoding='UTF-8'?>
<tsResponse xmlns="http://tableau.com/api">
  <error code="500001"></error>
</tsResponse>"""
    err = ServerResponseError.from_response(xml, NS, "http://test/")
    assert err.code == "500001"
    assert err.summary == ""
    assert err.detail == ""
