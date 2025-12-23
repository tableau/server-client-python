from pathlib import Path
import unittest

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import NonXMLResponseError

TEST_ASSET_DIR = Path(__file__).parent / "assets"

SERVER_INFO_GET_XML = TEST_ASSET_DIR / "server_info_get.xml"
SERVER_INFO_25_XML = TEST_ASSET_DIR / "server_info_25.xml"
SERVER_INFO_404 = TEST_ASSET_DIR / "server_info_404.xml"
SERVER_INFO_AUTH_INFO_XML = TEST_ASSET_DIR / "server_info_auth_info.xml"
SERVER_INFO_WRONG_SITE = TEST_ASSET_DIR / "server_info_wrong_site.html"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "2.4"

    return server


def test_server_info_get(server: TSC.Server) -> None:
    response_xml = SERVER_INFO_GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.server_info.baseurl, text=response_xml)
        actual = server.server_info.get()

        assert actual is not None
        assert "10.1.0" == actual.product_version
        assert "10100.16.1024.2100" == actual.build_number
        assert "3.10" == actual.rest_api_version


def test_server_info_use_highest_version_downgrades(server: TSC.Server) -> None:
    # This is the auth.xml endpoint present back to 9.0 Servers
    auth_response_xml = SERVER_INFO_AUTH_INFO_XML.read_text()
    # 10.1 serverInfo response
    si_response_xml = SERVER_INFO_404.read_text()
    with requests_mock.mock() as m:
        # Return a 404 for serverInfo so we can pretend this is an old Server
        m.get(server.server_address + "/api/2.4/serverInfo", text=si_response_xml, status_code=404)
        m.get(server.server_address + "/auth?format=xml", text=auth_response_xml)
        server.use_server_version()
        # does server-version[9.2] lookup in PRODUCT_TO_REST_VERSION
        assert server.version == "2.2"


def test_server_info_use_highest_version_upgrades(server: TSC.Server) -> None:
    si_response_xml = SERVER_INFO_GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.server_address + "/api/2.8/serverInfo", text=si_response_xml)
        # Pretend we're old
        server.version = "2.8"
        server.use_server_version()
        # Did we upgrade to 3.10?
        assert server.version == "3.10"


def test_server_use_server_version_flag(server: TSC.Server) -> None:
    si_response_xml = SERVER_INFO_25_XML.read_text()
    with requests_mock.mock() as m:
        m.get("http://test/api/2.4/serverInfo", text=si_response_xml)
        server = TSC.Server("http://test", use_server_version=True)
        assert server.version == "2.5"


def test_server_wrong_site(server: TSC.Server) -> None:
    response = SERVER_INFO_WRONG_SITE.read_text()
    with requests_mock.mock() as m:
        m.get(server.server_info.baseurl, text=response, status_code=404)
        with pytest.raises(NonXMLResponseError):
            server.server_info.get()
