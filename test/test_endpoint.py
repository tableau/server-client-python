from pathlib import Path
import pytest
import requests
import unittest

import tableauserverclient as TSC

import requests_mock

ASSETS = Path(__file__).parent / "assets"


class TestEndpoint(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test/", use_server_version=False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        return super().setUp()

    def test_fallback_request_logic(self) -> None:
        url = "http://test/"
        endpoint = TSC.server.Endpoint(self.server)
        with requests_mock.mock() as m:
            m.get(url)
            response = endpoint.get_request(url=url)
            self.assertIsNotNone(response)

    def test_user_friendly_request_returns(self) -> None:
        url = "http://test/"
        endpoint = TSC.server.Endpoint(self.server)
        with requests_mock.mock() as m:
            m.get(url)
            response = endpoint.send_request_while_show_progress_threaded(
                endpoint.parent_srv.session.get, url=url, request_timeout=2
            )
            self.assertIsNotNone(response)

    def test_blocking_request_raises_request_error(self) -> None:
        with pytest.raises(requests.exceptions.ConnectionError):
            url = "http://test/"
            endpoint = TSC.server.Endpoint(self.server)
            response = endpoint._blocking_request(endpoint.parent_srv.session.get, url=url)
            self.assertIsNotNone(response)

    def test_get_request_stream(self) -> None:
        url = "http://test/"
        endpoint = TSC.server.Endpoint(self.server)
        with requests_mock.mock() as m:
            m.get(url, headers={"Content-Type": "application/octet-stream"})
            response = endpoint.get_request(url, parameters={"stream": True})

            self.assertFalse(response._content_consumed)

    def test_binary_log_truncated(self):
        class FakeResponse:
            headers = {"Content-Type": "application/octet-stream"}
            content = b"\x1337" * 1000
            status_code = 200

        endpoint = TSC.server.Endpoint(self.server)
        server_response = FakeResponse()
        log = endpoint.log_response_safely(server_response)
        self.assertTrue(log.find("[Truncated File Contents]") > 0, log)

    def test_set_user_agent_from_options_headers(self):
        params = {"User-Agent": "1", "headers": {"User-Agent": "2"}}
        result = TSC.server.Endpoint.set_user_agent(params)
        # it should use the value under 'headers' if more than one is given
        print(result)
        print(result["headers"]["User-Agent"])
        self.assertTrue(result["headers"]["User-Agent"] == "2")

    def test_set_user_agent_from_options(self):
        params = {"headers": {"User-Agent": "2"}}
        result = TSC.server.Endpoint.set_user_agent(params)
        self.assertTrue(result["headers"]["User-Agent"] == "2")

    def test_set_user_agent_when_blank(self):
        params = {"headers": {}}
        result = TSC.server.Endpoint.set_user_agent(params)
        self.assertTrue(result["headers"]["User-Agent"].startswith("Tableau Server Client"))
