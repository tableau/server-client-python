from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

SIGN_IN_XML = TEST_ASSET_DIR / "auth_sign_in.xml"
SIGN_IN_IMPERSONATE_XML = TEST_ASSET_DIR / "auth_sign_in_impersonate.xml"
SIGN_IN_ERROR_XML = TEST_ASSET_DIR / "auth_sign_in_error.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    """Fixture to create a Tableau Server instance for testing."""
    server_instance = TSC.Server("http://test", False)
    return server_instance


def test_sign_in_switches_to_https_when_the_probe_redirects() -> None:
    server = TSC.Server("http://tableau.example", False)
    response_xml = SIGN_IN_XML.read_text()
    with requests_mock.mock() as m:
        m.get(
            "http://tableau.example/api/2.4/serverInfo",
            status_code=301,
            headers={"Location": "https://tableau.example/api/2.4/serverInfo"},
        )
        m.post("https://tableau.example/api/2.4/auth/signin", text=response_xml)
        server.auth.sign_in(TSC.TableauAuth("testuser", "password", site_id="Samples"))

    assert server.server_address == "https://tableau.example"
    assert [call.method for call in m.request_history] == ["GET", "POST"]
    assert m.request_history[1].url.startswith("https://tableau.example/")


def test_sign_in_stays_on_http_when_the_server_accepts_it() -> None:
    server = TSC.Server("http://plain.example", False)
    response_xml = SIGN_IN_XML.read_text()
    info_xml = """<?xml version='1.0' encoding='utf-8'?>
        <tsResponse xmlns="http://tableau.com/api">
          <serverInfo>
            <productVersion build="1">10.0.0</productVersion>
            <restApiVersion>2.4</restApiVersion>
          </serverInfo>
        </tsResponse>"""
    with requests_mock.mock() as m:
        m.get("http://plain.example/api/2.4/serverInfo", text=info_xml)
        m.post("http://plain.example/api/2.4/auth/signin", text=response_xml)
        server.auth.sign_in(TSC.TableauAuth("testuser", "password"))

    assert server.server_address == "http://plain.example"
    assert m.request_history[1].url.startswith("http://plain.example/")


def test_sign_in_switches_to_https_when_http_is_rejected() -> None:
    server = TSC.Server("http://secure.example", False)
    response_xml = SIGN_IN_XML.read_text()
    info_xml = """<?xml version='1.0' encoding='utf-8'?>
        <tsResponse xmlns="http://tableau.com/api">
          <serverInfo>
            <productVersion build="1">2024.1.0</productVersion>
            <restApiVersion>3.22</restApiVersion>
          </serverInfo>
        </tsResponse>"""
    with requests_mock.mock() as m:
        m.get("http://secure.example/api/2.4/serverInfo", status_code=405)
        m.get("https://secure.example/api/2.4/serverInfo", text=info_xml)
        m.post("https://secure.example/api/2.4/auth/signin", text=response_xml)
        server.auth.sign_in(TSC.TableauAuth("testuser", "password"))

    assert server.server_address == "https://secure.example"
    assert m.request_history[0].method == "GET"
    assert m.request_history[-1].url.startswith("https://secure.example/")


def test_sign_in(server: TSC.Server) -> None:
    with open(SIGN_IN_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml)
        tableau_auth = TSC.TableauAuth("testuser", "password", site_id="Samples")
        server.auth.sign_in(tableau_auth)

    assert "eIX6mvFsqyansa4KqEI1UwOpS8ggRs2l" == server.auth_token
    assert "6b7179ba-b82b-4f0f-91ed-812074ac5da6" == server.site_id
    assert "Samples" == server.site_url
    assert "1a96d216-e9b8-497b-a82a-0b899a965e01" == server.user_id


def test_sign_in_with_personal_access_tokens(server: TSC.Server) -> None:
    with open(SIGN_IN_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml)
        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name="mytoken", personal_access_token="Random123Generated", site_id="Samples"
        )
        server.auth.sign_in(tableau_auth)

    assert "eIX6mvFsqyansa4KqEI1UwOpS8ggRs2l" == server.auth_token
    assert "6b7179ba-b82b-4f0f-91ed-812074ac5da6" == server.site_id
    assert "Samples" == server.site_url
    assert "1a96d216-e9b8-497b-a82a-0b899a965e01" == server.user_id


def test_sign_in_impersonate(server: TSC.Server) -> None:
    with open(SIGN_IN_IMPERSONATE_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml)
        tableau_auth = TSC.TableauAuth(
            "testuser", "password", user_id_to_impersonate="dd2239f6-ddf1-4107-981a-4cf94e415794"
        )
        server.auth.sign_in(tableau_auth)

    assert "MJonFA6HDyy2C3oqR13fRGqE6cmgzwq3" == server.auth_token
    assert "dad65087-b08b-4603-af4e-2887b8aafc67" == server.site_id
    assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == server.user_id


def test_sign_in_error(server: TSC.Server) -> None:
    with open(SIGN_IN_ERROR_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml, status_code=401)
        tableau_auth = TSC.TableauAuth("testuser", "wrongpassword")
        with pytest.raises(TSC.FailedSignInError):
            server.auth.sign_in(tableau_auth)


def test_sign_in_invalid_token(server: TSC.Server) -> None:
    with open(SIGN_IN_ERROR_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml, status_code=401)
        tableau_auth = TSC.PersonalAccessTokenAuth(token_name="mytoken", personal_access_token="invalid")
        with pytest.raises(TSC.FailedSignInError):
            server.auth.sign_in(tableau_auth)


def test_sign_in_without_auth(server: TSC.Server) -> None:
    with open(SIGN_IN_ERROR_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml, status_code=401)
        tableau_auth = TSC.TableauAuth("", "")
        with pytest.raises(TSC.FailedSignInError):
            server.auth.sign_in(tableau_auth)


def test_sign_out(server: TSC.Server) -> None:
    with open(SIGN_IN_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(server.auth.baseurl + "/signin", text=response_xml)
        m.post(server.auth.baseurl + "/signout", text="")
        tableau_auth = TSC.TableauAuth("testuser", "password")
        server.auth.sign_in(tableau_auth)
        server.auth.sign_out()

    assert server._auth_token is None
    assert server._site_id is None
    assert server._site_url is None
    assert server._user_id is None


def test_switch_site(server: TSC.Server) -> None:
    server.version = "2.6"
    baseurl = server.auth.baseurl
    site_id, user_id, auth_token = list("123")
    server._set_auth(site_id, user_id, auth_token)
    with open(SIGN_IN_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(baseurl + "/switchSite", text=response_xml)
        site = TSC.SiteItem("Samples", "Samples")
        server.auth.switch_site(site)

    assert "eIX6mvFsqyansa4KqEI1UwOpS8ggRs2l" == server.auth_token
    assert "6b7179ba-b82b-4f0f-91ed-812074ac5da6" == server.site_id
    assert "Samples" == server.site_url
    assert "1a96d216-e9b8-497b-a82a-0b899a965e01" == server.user_id


def test_revoke_all_server_admin_tokens(server: TSC.Server) -> None:
    server.version = "3.10"
    baseurl = server.auth.baseurl
    with open(SIGN_IN_XML, "rb") as f:
        response_xml = f.read().decode("utf-8")
    with requests_mock.mock() as m:
        m.post(baseurl + "/signin", text=response_xml)
        m.post(baseurl + "/revokeAllServerAdminTokens", text="")
        tableau_auth = TSC.TableauAuth("testuser", "password")
        server.auth.sign_in(tableau_auth)
        server.auth.revoke_all_server_admin_tokens()

    assert "eIX6mvFsqyansa4KqEI1UwOpS8ggRs2l" == server.auth_token
    assert "6b7179ba-b82b-4f0f-91ed-812074ac5da6" == server.site_id
    assert "Samples" == server.site_url
    assert "1a96d216-e9b8-497b-a82a-0b899a965e01" == server.user_id
