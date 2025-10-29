from pathlib import Path

from defusedxml.ElementTree import fromstring
import requests_mock
import pytest

import tableauserverclient as TSC


TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_SERVER_EXT_SETTINGS = TEST_ASSET_DIR / "extensions_server_settings_true.xml"
GET_SERVER_EXT_SETTINGS_FALSE = TEST_ASSET_DIR / "extensions_server_settings_false.xml"
GET_SITE_SETTINGS = TEST_ASSET_DIR / "extensions_site_settings.xml"


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


def test_get_site_settings(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.extensions.baseurl, text=GET_SITE_SETTINGS.read_text())
        site_settings = server.extensions.get()

    assert isinstance(site_settings, TSC.ExtensionsSiteSettings)
    assert site_settings.enabled is True
    assert site_settings.use_default_setting is False
    assert site_settings.safe_list is not None
    assert site_settings.allow_trusted is True
    assert site_settings.include_partner_built is False
    assert site_settings.include_sandboxed is False
    assert site_settings.include_tableau_built is False
    assert len(site_settings.safe_list) == 1
    first_safe = site_settings.safe_list[0]
    assert first_safe.url == "http://localhost:9123/Dynamic.html"
    assert first_safe.full_data_allowed is True
    assert first_safe.prompt_needed is True


def test_update_site_settings(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.put(server.extensions.baseurl, text=GET_SITE_SETTINGS.read_text())

        site_settings = TSC.ExtensionsSiteSettings()
        site_settings.enabled = True
        site_settings.use_default_setting = False
        safe_extension = TSC.SafeExtension(
            url="http://localhost:9123/Dynamic.html",
            full_data_allowed=True,
            prompt_needed=True,
        )
        site_settings.safe_list = [safe_extension]

        updated_settings = server.extensions.update(site_settings)
        history = m.request_history

    assert isinstance(updated_settings, TSC.ExtensionsSiteSettings)
    assert updated_settings.enabled is True
    assert updated_settings.use_default_setting is False
    assert updated_settings.safe_list is not None
    assert len(updated_settings.safe_list) == 1
    first_safe = updated_settings.safe_list[0]
    assert first_safe.url == "http://localhost:9123/Dynamic.html"
    assert first_safe.full_data_allowed is True
    assert first_safe.prompt_needed is True

    # Verify that the request body was as expected
    assert len(history) == 1
    xml_payload = fromstring(history[0].body)
    extensions_site_settings_elem = xml_payload.find(".//extensionsSiteSettings")
    assert extensions_site_settings_elem is not None
    enabled_elem = extensions_site_settings_elem.find("extensionsEnabled")
    assert enabled_elem is not None
    assert enabled_elem.text == "true"
    use_default_elem = extensions_site_settings_elem.find("useDefaultSetting")
    assert use_default_elem is not None
    assert use_default_elem.text == "false"
    safe_list_elements = list(extensions_site_settings_elem.findall("safeList"))
    assert len(safe_list_elements) == 1
    safe_extension_elem = safe_list_elements[0]
    url_elem = safe_extension_elem.find("url")
    assert url_elem is not None
    assert url_elem.text == "http://localhost:9123/Dynamic.html"
    full_data_allowed_elem = safe_extension_elem.find("fullDataAllowed")
    assert full_data_allowed_elem is not None
    assert full_data_allowed_elem.text == "true"
    prompt_needed_elem = safe_extension_elem.find("promptNeeded")
    assert prompt_needed_elem is not None
    assert prompt_needed_elem.text == "true"
