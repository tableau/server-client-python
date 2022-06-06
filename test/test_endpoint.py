from pathlib import Path
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

    def test_get_request_stream(self) -> None:
        url = "http://test/"
        endpoint = TSC.server.Endpoint(self.server)
        with requests_mock.mock() as m:
            m.get(url, headers={"Content-Type": "application/octet-stream"})
            response = endpoint.get_request(url, parameters={"stream": True})

            self.assertFalse(response._content_consumed)

    def test_binary_log_truncated(self):
        class FakeResponse(object):

            headers = {"Content-Type": "application/octet-stream"}
            content = b"\x1337" * 1000
            status_code = 200

        endpoint = TSC.server.Endpoint(self.server)
        server_response = FakeResponse()
        log = endpoint.log_response_safely(server_response)
        self.assertTrue(log.find("[Truncated File Contents]") > 0, log)
