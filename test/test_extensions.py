from pathlib import Path

import requests_mock
import pytest

import tableauserverclient as TSC


TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_SERVER_EXT_SETTINGS = TEST_ASSET_DIR / "extensions_server_settings_true.xml"
GET_SERVER_EXT_SETTINGS_FALSE = TEST_ASSET_DIR / "extensions_server_settings_false.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    server = TSC.Server("http://test", False)

    # Fake sign in
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.21"

    return server


def test_get_server_extensions_settings(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.extensions._server_baseurl, text=GET_SERVER_EXT_SETTINGS.read_text())
        ext_settings = server.extensions.get_server_settings()

    assert ext_settings.enabled is True
    assert ext_settings.block_list is not None
    assert set(ext_settings.block_list) == {"https://test.com", "https://example.com"}


def test_get_server_extensions_settings_false(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.extensions._server_baseurl, text=GET_SERVER_EXT_SETTINGS_FALSE.read_text())
        ext_settings = server.extensions.get_server_settings()

    assert ext_settings.enabled is False
    assert ext_settings.block_list is not None
    assert len(ext_settings.block_list) == 0


def test_update_server_extensions_settings(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.put(server.extensions._server_baseurl, text=GET_SERVER_EXT_SETTINGS_FALSE.read_text())

        ext_settings = TSC.ExtensionsServer()
        ext_settings.enabled = False
        ext_settings.block_list = []

        updated_settings = server.extensions.update_server_settings(ext_settings)

    assert updated_settings.enabled is False
    assert updated_settings.block_list is not None
    assert len(updated_settings.block_list) == 0
