from pathlib import Path
import pytest
import requests

import tableauserverclient as TSC

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
    endpoint = TSC.server.Endpoint(server)
    with requests_mock.mock() as m:
        m.get(url)
        response = endpoint.get_request(url=url)
        assert response is not None


def test_user_friendly_request_returns(server: TSC.Server) -> None:
    url = "http://test/"
    endpoint = TSC.server.Endpoint(server)
    with requests_mock.mock() as m:
        m.get(url)
        response = endpoint.send_request_while_show_progress_threaded(
            endpoint.parent_srv.session.get, url=url, request_timeout=2
        )
        assert response is not None


def test_blocking_request_raises_request_error(server: TSC.Server) -> None:
    with pytest.raises(requests.exceptions.ConnectionError):
        url = "http://test/"
        endpoint = TSC.server.Endpoint(server)
        response = endpoint._blocking_request(endpoint.parent_srv.session.get, url=url)
        assert response is not None


def test_get_request_stream(server: TSC.Server) -> None:
    url = "http://test/"
    endpoint = TSC.server.Endpoint(server)
    with requests_mock.mock() as m:
        m.get(url, headers={"Content-Type": "application/octet-stream"})
        response = endpoint.get_request(url, parameters={"stream": True})

        assert response._content_consumed is False


def test_binary_log_truncated(server: TSC.Server) -> None:
    class FakeResponse:
        headers = {"Content-Type": "application/octet-stream"}
        content = b"\x1337" * 1000
        status_code = 200

    endpoint = TSC.server.Endpoint(server)
    server_response = FakeResponse()
    log = endpoint.log_response_safely(server_response)
    assert log.find("[Truncated File Contents]") > 0


def test_set_user_agent_from_options_headers(server: TSC.Server) -> None:
    params = {"User-Agent": "1", "headers": {"User-Agent": "2"}}
    result = TSC.server.Endpoint.set_user_agent(params)
    # it should use the value under 'headers' if more than one is given
    print(result)
    print(result["headers"]["User-Agent"])
    assert result["headers"]["User-Agent"] == "2"


def test_set_user_agent_from_options(server: TSC.Server) -> None:
    params = {"headers": {"User-Agent": "2"}}
    result = TSC.server.Endpoint.set_user_agent(params)
    assert result["headers"]["User-Agent"] == "2"


def test_set_user_agent_when_blank(server: TSC.Server) -> None:
    params = {"headers": {}}
    result = TSC.server.Endpoint.set_user_agent(params)
    assert result["headers"]["User-Agent"].startswith("Tableau Server Client")
