from defusedxml.ElementTree import fromstring


class AuthFederationConnectorItem:
    def __init__(self) -> None:
        self.luid: str | None = None
        self.connector_class: str | None = None
        self.audience: str | None = None

    def __str__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(luid={self.luid}, "
            f"connector_class={self.connector_class}, audience={self.audience})"
        )

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    @classmethod
    def from_element(cls, elem) -> "AuthFederationConnectorItem":
        connector = cls()
        connector.luid = elem.get("luid")
        connector.connector_class = elem.get("connectorClass")
        connector.audience = elem.get("audience")
        return connector

    @classmethod
    def from_response(cls, raw_xml: bytes, ns) -> "AuthFederationConnectorItem":
        root = fromstring(raw_xml)
        elem = root.find("t:authFederationConnector", namespaces=ns)
        if elem is None:
            raise ValueError("No authFederationConnector element found in the XML.")
        return cls.from_element(elem)

    @classmethod
    def list_from_response(cls, raw_xml: bytes, ns) -> list["AuthFederationConnectorItem"]:
        root = fromstring(raw_xml)
        list_elem = root.find("t:authFederationConnectors", namespaces=ns)
        if list_elem is None:
            return []
        return [cls.from_element(c) for c in list_elem.findall("t:connector", namespaces=ns)]


class AuthFederationKeyItem:
    def __init__(self) -> None:
        self.kid: str | None = None
        self.kty: str | None = None
        self.alg: str | None = None
        self.use: str | None = None
        self.n: str | None = None
        self.e: str | None = None

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}(kid={self.kid}, kty={self.kty}, " f"alg={self.alg}, use={self.use})"

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    @classmethod
    def from_element(cls, elem) -> "AuthFederationKeyItem":
        key = cls()
        key.kid = elem.get("kid")
        key.kty = elem.get("kty")
        key.alg = elem.get("alg")
        key.use = elem.get("use")
        key.n = elem.get("n")
        key.e = elem.get("e")
        return key

    @classmethod
    def from_response(cls, raw_xml: bytes, ns) -> "AuthFederationKeyItem":
        root = fromstring(raw_xml)
        elem = root.find("t:authFederationKey", namespaces=ns)
        if elem is None:
            raise ValueError("No authFederationKey element found in the XML.")
        return cls.from_element(elem)


class AuthFederationItem:
    def __init__(self) -> None:
        self.enabled: bool = False
        self.issuer_url: str | None = None
        self.active_key_id: str | None = None
        self.token_lifetime_seconds: int | None = None
        self.connectors: list[AuthFederationConnectorItem] = []

    def __str__(self) -> str:
        return (
            f"{self.__class__.__qualname__}(enabled={self.enabled}, "
            f"issuer_url={self.issuer_url}, active_key_id={self.active_key_id}, "
            f"token_lifetime_seconds={self.token_lifetime_seconds}, "
            f"connectors={len(self.connectors)})"
        )

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    @classmethod
    def from_response(cls, raw_xml: bytes, ns) -> "AuthFederationItem":
        root = fromstring(raw_xml)
        elem = root.find("t:authFederationAdmin", namespaces=ns)
        if elem is None:
            raise ValueError("No authFederationAdmin element found in the XML.")
        config = cls()
        config.enabled = _str_to_bool(elem.get("enabled", "false"))
        config.issuer_url = elem.get("issuerUrl")
        config.active_key_id = elem.get("activeKeyId")
        token_lifetime = elem.get("tokenLifetimeSeconds")
        if token_lifetime is not None:
            config.token_lifetime_seconds = int(token_lifetime)
        connectors_elem = elem.find("t:connectors", namespaces=ns)
        if connectors_elem is not None:
            config.connectors = [
                AuthFederationConnectorItem.from_element(c)
                for c in connectors_elem.findall("t:connector", namespaces=ns)
            ]
        return config


def _str_to_bool(s: str) -> bool:
    return s == "true"
