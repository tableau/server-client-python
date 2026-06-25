from defusedxml.ElementTree import fromstring


class SiteOIDCConfiguration:
    def __init__(self) -> None:
        self.enabled: bool = False
        self.test_login_url: str | None = None
        self.known_provider_alias: str | None = None
        self.allow_embedded_authentication: bool = False
        self.use_full_name: bool = False
        self.idp_configuration_name: str | None = None
        self.idp_configuration_id: str | None = None
        self.client_id: str | None = None
        self.client_secret: str | None = None
        self.authorization_endpoint: str | None = None
        self.token_endpoint: str | None = None
        self.userinfo_endpoint: str | None = None
        self.jwks_uri: str | None = None
        self.end_session_endpoint: str | None = None
        self.custom_scope: str | None = None
        self.essential_acr_values: str | None = None
        self.email_mapping: str | None = None
        self.first_name_mapping: str | None = None
        self.last_name_mapping: str | None = None
        self.full_name_mapping: str | None = None
        self.prompt: str | None = None
        self.client_authentication: str | None = None
        self.voluntary_acr_values: str | None = None

    def __str__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(enabled={self.enabled}, "
            f"test_login_url={self.test_login_url}, "
            f"idp_configuration_name={self.idp_configuration_name}, "
            f"idp_configuration_id={self.idp_configuration_id}, "
            f"client_id={self.client_id})"
        )

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    @classmethod
    def from_response(cls, raw_xml: bytes, ns) -> "SiteOIDCConfiguration":
        """
        Parses the raw XML bytes and returns a SiteOIDCConfiguration object.
        """
        root = fromstring(raw_xml)
        elem = root.find("t:siteOIDCConfiguration", namespaces=ns)
        if elem is None:
            raise ValueError("No siteOIDCConfiguration element found in the XML.")
        config = cls()

        config.enabled = str_to_bool(elem.get("enabled", "false"))
        config.test_login_url = elem.get("testLoginUrl")
        config.known_provider_alias = elem.get("knownProviderAlias")
        config.allow_embedded_authentication = str_to_bool(elem.get("allowEmbeddedAuthentication", "false").lower())
        config.use_full_name = str_to_bool(elem.get("useFullName", "false").lower())
        config.idp_configuration_name = elem.get("idpConfigurationName")
        config.idp_configuration_id = elem.get("idpConfigurationId")
        config.client_id = elem.get("clientId")
        config.client_secret = elem.get("clientSecret")
        config.authorization_endpoint = elem.get("authorizationEndpoint")
        config.token_endpoint = elem.get("tokenEndpoint")
        config.userinfo_endpoint = elem.get("userinfoEndpoint")
        config.jwks_uri = elem.get("jwksUri")
        config.end_session_endpoint = elem.get("endSessionEndpoint")
        config.custom_scope = elem.get("customScope")
        config.essential_acr_values = elem.get("essentialAcrValues")
        config.email_mapping = elem.get("emailMapping")
        config.first_name_mapping = elem.get("firstNameMapping")
        config.last_name_mapping = elem.get("lastNameMapping")
        config.full_name_mapping = elem.get("fullNameMapping")
        config.prompt = elem.get("prompt")
        config.client_authentication = elem.get("clientAuthentication")
        config.voluntary_acr_values = elem.get("voluntaryAcrValues")

        return config


def str_to_bool(s: str) -> bool:
    return s == "true"
