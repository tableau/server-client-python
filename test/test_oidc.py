import unittest
import requests_mock
from pathlib import Path

import tableauserverclient as TSC

assets = Path(__file__).parent / "assets"
OIDC_GET = assets / "oidc_get.xml"
OIDC_GET_BY_ID = assets / "oidc_get_by_id.xml"
OIDC_UPDATE = assets / "oidc_update.xml"
OIDC_CREATE = assets / "oidc_create.xml"


class Testoidc(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.server.version = "3.24"

        self.baseurl = self.server.oidc.baseurl

    def test_oidc_get_by_id(self) -> None:
        luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{luid}", text=OIDC_GET.read_text())
            oidc = self.server.oidc.get_by_id(luid)

        assert oidc.enabled is True
        assert (
            oidc.test_login_url
            == "https://sso.online.tableau.com/public/testLogin?alias=8a04d825-e5d4-408f-bbc2-1042b8bb4818&authSetting=OIDC&idpConfigurationId=78c985b4-5494-4436-bcee-f595e287ba4a"
        )
        assert oidc.known_provider_alias == "Google"
        assert oidc.allow_embedded_authentication is False
        assert oidc.use_full_name is False
        assert oidc.idp_configuration_name == "GoogleOIDC"
        assert oidc.idp_configuration_id == "78c985b4-5494-4436-bcee-f595e287ba4a"
        assert oidc.client_id == "ICcGeDt3XHwzZ1D0nCZt"
        assert oidc.client_secret == "omit"
        assert oidc.authorization_endpoint == "https://myidp.com/oauth2/v1/authorize"
        assert oidc.token_endpoint == "https://myidp.com/oauth2/v1/token"
        assert oidc.userinfo_endpoint == "https://myidp.com/oauth2/v1/userinfo"
        assert oidc.jwks_uri == "https://myidp.com/oauth2/v1/keys"
        assert oidc.end_session_endpoint == "https://myidp.com/oauth2/v1/logout"
        assert oidc.custom_scope == "openid, email, profile"
        assert oidc.prompt == "login,consent"
        assert oidc.client_authentication == "client_secret_basic"
        assert oidc.essential_acr_values == "phr"
        assert oidc.email_mapping == "email"
        assert oidc.first_name_mapping == "given_name"
        assert oidc.last_name_mapping == "family_name"
        assert oidc.full_name_mapping == "name"

    def test_oidc_delete(self) -> None:
        luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
        with requests_mock.mock() as m:
            m.put(f"{self.server.baseurl}/sites/{self.server.site_id}/disable-site-oidc-configuration")
            self.server.oidc.delete_configuration(luid)
            history = m.request_history[0]

        assert "idpconfigurationid" in history.qs
        assert history.qs["idpconfigurationid"][0] == luid

    def test_oidc_update(self) -> None:
        luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
        oidc = TSC.SiteOIDCConfiguration()
        oidc.idp_configuration_id = luid

        # Only include the required fields for updates
        oidc.enabled = True
        oidc.idp_configuration_name = "GoogleOIDC"
        oidc.client_id = "ICcGeDt3XHwzZ1D0nCZt"
        oidc.client_secret = "omit"
        oidc.authorization_endpoint = "https://myidp.com/oauth2/v1/authorize"
        oidc.token_endpoint = "https://myidp.com/oauth2/v1/token"
        oidc.userinfo_endpoint = "https://myidp.com/oauth2/v1/userinfo"
        oidc.jwks_uri = "https://myidp.com/oauth2/v1/keys"

        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{luid}", text=OIDC_UPDATE.read_text())
            oidc = self.server.oidc.update(oidc)

        assert oidc.enabled is True
        assert (
            oidc.test_login_url
            == "https://sso.online.tableau.com/public/testLogin?alias=8a04d825-e5d4-408f-bbc2-1042b8bb4818&authSetting=OIDC&idpConfigurationId=78c985b4-5494-4436-bcee-f595e287ba4a"
        )
        assert oidc.known_provider_alias == "Google"
        assert oidc.allow_embedded_authentication is False
        assert oidc.use_full_name is False
        assert oidc.idp_configuration_name == "GoogleOIDC"
        assert oidc.idp_configuration_id == "78c985b4-5494-4436-bcee-f595e287ba4a"
        assert oidc.client_id == "ICcGeDt3XHwzZ1D0nCZt"
        assert oidc.client_secret == "omit"
        assert oidc.authorization_endpoint == "https://myidp.com/oauth2/v1/authorize"
        assert oidc.token_endpoint == "https://myidp.com/oauth2/v1/token"
        assert oidc.userinfo_endpoint == "https://myidp.com/oauth2/v1/userinfo"
        assert oidc.jwks_uri == "https://myidp.com/oauth2/v1/keys"
        assert oidc.end_session_endpoint == "https://myidp.com/oauth2/v1/logout"
        assert oidc.custom_scope == "openid, email, profile"
        assert oidc.prompt == "login,consent"
        assert oidc.client_authentication == "client_secret_basic"
        assert oidc.essential_acr_values == "phr"
        assert oidc.email_mapping == "email"
        assert oidc.first_name_mapping == "given_name"
        assert oidc.last_name_mapping == "family_name"
        assert oidc.full_name_mapping == "name"

    def test_oidc_create(self) -> None:
        oidc = TSC.SiteOIDCConfiguration()

        # Only include the required fields for creation
        oidc.enabled = True
        oidc.idp_configuration_name = "GoogleOIDC"
        oidc.client_id = "ICcGeDt3XHwzZ1D0nCZt"
        oidc.client_secret = "omit"
        oidc.authorization_endpoint = "https://myidp.com/oauth2/v1/authorize"
        oidc.token_endpoint = "https://myidp.com/oauth2/v1/token"
        oidc.userinfo_endpoint = "https://myidp.com/oauth2/v1/userinfo"
        oidc.jwks_uri = "https://myidp.com/oauth2/v1/keys"

        with requests_mock.mock() as m:
            m.put(self.baseurl, text=OIDC_CREATE.read_text())
            oidc = self.server.oidc.create(oidc)

        assert oidc.enabled is True
        assert (
            oidc.test_login_url
            == "https://sso.online.tableau.com/public/testLogin?alias=8a04d825-e5d4-408f-bbc2-1042b8bb4818&authSetting=OIDC&idpConfigurationId=78c985b4-5494-4436-bcee-f595e287ba4a"
        )
        assert oidc.known_provider_alias == "Google"
        assert oidc.allow_embedded_authentication is False
        assert oidc.use_full_name is False
        assert oidc.idp_configuration_name == "GoogleOIDC"
        assert oidc.idp_configuration_id == "78c985b4-5494-4436-bcee-f595e287ba4a"
        assert oidc.client_id == "ICcGeDt3XHwzZ1D0nCZt"
        assert oidc.client_secret == "omit"
        assert oidc.authorization_endpoint == "https://myidp.com/oauth2/v1/authorize"
        assert oidc.token_endpoint == "https://myidp.com/oauth2/v1/token"
        assert oidc.userinfo_endpoint == "https://myidp.com/oauth2/v1/userinfo"
        assert oidc.jwks_uri == "https://myidp.com/oauth2/v1/keys"
        assert oidc.end_session_endpoint == "https://myidp.com/oauth2/v1/logout"
        assert oidc.custom_scope == "openid, email, profile"
        assert oidc.prompt == "login,consent"
        assert oidc.client_authentication == "client_secret_basic"
        assert oidc.essential_acr_values == "phr"
        assert oidc.email_mapping == "email"
        assert oidc.first_name_mapping == "given_name"
        assert oidc.last_name_mapping == "family_name"
        assert oidc.full_name_mapping == "name"
