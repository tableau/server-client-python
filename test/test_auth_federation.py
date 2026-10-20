from pathlib import Path

import pytest
import requests_mock
from defusedxml.ElementTree import fromstring

import tableauserverclient as TSC
from tableauserverclient.server.exceptions import EndpointUnavailableError

assets = Path(__file__).parent / "assets"
GET = assets / "auth_federation_get.xml"
ENABLE = assets / "auth_federation_enable.xml"
UPDATE = assets / "auth_federation_update.xml"
CONNECTOR_CREATE = assets / "auth_federation_connector_create.xml"
CONNECTOR_GET = assets / "auth_federation_connector_get.xml"
CONNECTORS_LIST = assets / "auth_federation_connectors_list.xml"
CONNECTORS_LIST_EMPTY = assets / "auth_federation_connectors_list_empty.xml"
KEY_CREATE = assets / "auth_federation_key_create.xml"

NS = {"t": "http://tableau.com/api"}
CONNECTOR_LUID = "d3a8e5b2-7c01-4e13-9c82-6f45a9b4e8d1"
KEY_KID = "a4b9c2d7-ff81-45e8-9c3e-6b19d2a5c0ee"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    server = TSC.Server("http://test", False)
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.30"
    return server


def test_auth_federation_get(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.auth_federation.baseurl, text=GET.read_text())
        config = server.auth_federation.get()

    assert config.enabled is True
    assert config.issuer_url == "https://10ax.online.tableau.com/sites/mySite/auth-federation"
    assert config.active_key_id == "a4b9c2d7-ff81-45e8-9c3e-6b19d2a5c0ee"
    assert config.token_lifetime_seconds == 3600
    assert len(config.connectors) == 2
    assert {c.connector_class for c in config.connectors} == {"bigquery", "snowflake"}
    bigquery = next(c for c in config.connectors if c.connector_class == "bigquery")
    assert bigquery.luid == CONNECTOR_LUID
    assert bigquery.audience.startswith("//iam.googleapis.com/")


def test_auth_federation_get_defaults_when_never_enabled(server: TSC.Server) -> None:
    default_body = (
        '<tsResponse xmlns="http://tableau.com/api">' '<authFederationAdmin enabled="false"/>' "</tsResponse>"
    )
    with requests_mock.mock() as m:
        m.get(server.auth_federation.baseurl, text=default_body)
        config = server.auth_federation.get()

    assert config.enabled is False
    assert config.issuer_url is None
    assert config.active_key_id is None
    assert config.token_lifetime_seconds is None
    assert config.connectors == []


def test_auth_federation_enable(server: TSC.Server) -> None:
    config_in = TSC.AuthFederationItem()
    config_in.enabled = True
    config_in.token_lifetime_seconds = 3600

    with requests_mock.mock() as m:
        m.put(server.auth_federation.baseurl, text=ENABLE.read_text())
        config_out = server.auth_federation.enable(config_in)
        body = m.request_history[0].text

    sent = fromstring(body)
    elem = sent.find("authFederationAdmin")
    assert elem is not None
    assert elem.get("enabled") == "true"
    assert elem.get("tokenLifetimeSeconds") == "3600"
    assert elem.find("connectors") is None

    assert config_out.enabled is True
    assert config_out.active_key_id == "a4b9c2d7-ff81-45e8-9c3e-6b19d2a5c0ee"
    assert config_out.token_lifetime_seconds == 3600


def test_auth_federation_enable_without_token_lifetime(server: TSC.Server) -> None:
    config_in = TSC.AuthFederationItem()
    config_in.enabled = True

    with requests_mock.mock() as m:
        m.put(server.auth_federation.baseurl, text=ENABLE.read_text())
        server.auth_federation.enable(config_in)
        body = m.request_history[0].text

    elem = fromstring(body).find("authFederationAdmin")
    assert elem is not None
    assert elem.get("enabled") == "true"
    assert "tokenLifetimeSeconds" not in elem.attrib


def test_auth_federation_enable_rejects_disabled(server: TSC.Server) -> None:
    config_in = TSC.AuthFederationItem()
    config_in.enabled = False

    with pytest.raises(ValueError, match="enabled=True"):
        server.auth_federation.enable(config_in)


def test_auth_federation_update(server: TSC.Server) -> None:
    config_in = TSC.AuthFederationItem()
    config_in.token_lifetime_seconds = 7200
    config_in.issuer_url = "ignored-by-server"
    config_in.active_key_id = "ignored-by-server"

    with requests_mock.mock() as m:
        m.patch(server.auth_federation.baseurl, text=UPDATE.read_text())
        config_out = server.auth_federation.update(config_in)
        body = m.request_history[0].text

    elem = fromstring(body).find("authFederationAdmin")
    assert elem is not None
    assert elem.get("tokenLifetimeSeconds") == "7200"
    # Read-only fields must not be sent; the server would ignore them anyway,
    # but we don't want the client to pretend they're mutable.
    assert "issuerUrl" not in elem.attrib
    assert "activeKeyId" not in elem.attrib

    assert config_out.token_lifetime_seconds == 7200


def test_auth_federation_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.auth_federation.baseurl, status_code=204)
        server.auth_federation.delete()

    assert m.called_once


def test_auth_federation_create_connector(server: TSC.Server) -> None:
    connector_in = TSC.AuthFederationConnectorItem()
    connector_in.connector_class = "bigquery"
    connector_in.audience = (
        "//iam.googleapis.com/projects/123456789/locations/global/"
        "workloadIdentityPools/tableau-pool/providers/tableau-provider"
    )

    with requests_mock.mock() as m:
        m.post(f"{server.auth_federation.baseurl}/connectors", text=CONNECTOR_CREATE.read_text())
        connector_out = server.auth_federation.create_connector(connector_in)
        body = m.request_history[0].text

    elem = fromstring(body).find("authFederationConnector")
    assert elem is not None
    assert elem.get("connectorClass") == "bigquery"
    assert elem.get("audience") == connector_in.audience
    assert "luid" not in elem.attrib

    assert connector_out.luid == CONNECTOR_LUID
    assert connector_out.connector_class == "bigquery"


def test_auth_federation_create_connector_requires_class(server: TSC.Server) -> None:
    connector_in = TSC.AuthFederationConnectorItem()
    connector_in.audience = "snowflakecomputing.com"

    with pytest.raises(ValueError, match="connector_class"):
        server.auth_federation.create_connector(connector_in)


def test_auth_federation_create_connector_requires_audience(server: TSC.Server) -> None:
    connector_in = TSC.AuthFederationConnectorItem()
    connector_in.connector_class = "snowflake"

    with pytest.raises(ValueError, match="audience"):
        server.auth_federation.create_connector(connector_in)


def test_auth_federation_list_connectors(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(f"{server.auth_federation.baseurl}/connectors", text=CONNECTORS_LIST.read_text())
        connectors = server.auth_federation.list_connectors()

    assert len(connectors) == 2
    classes = {c.connector_class for c in connectors}
    assert classes == {"bigquery", "snowflake"}


def test_auth_federation_list_connectors_empty(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(f"{server.auth_federation.baseurl}/connectors", text=CONNECTORS_LIST_EMPTY.read_text())
        connectors = server.auth_federation.list_connectors()

    assert connectors == []


def test_auth_federation_get_connector_by_luid(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(
            f"{server.auth_federation.baseurl}/connectors/{CONNECTOR_LUID}",
            text=CONNECTOR_GET.read_text(),
        )
        connector = server.auth_federation.get_connector(CONNECTOR_LUID)

    assert connector.luid == CONNECTOR_LUID
    assert connector.connector_class == "bigquery"


def test_auth_federation_get_connector_by_item(server: TSC.Server) -> None:
    stub = TSC.AuthFederationConnectorItem()
    stub.luid = CONNECTOR_LUID

    with requests_mock.mock() as m:
        m.get(
            f"{server.auth_federation.baseurl}/connectors/{CONNECTOR_LUID}",
            text=CONNECTOR_GET.read_text(),
        )
        connector = server.auth_federation.get_connector(stub)

    assert connector.luid == CONNECTOR_LUID


def test_auth_federation_delete_connector_by_luid(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(f"{server.auth_federation.baseurl}/connectors/{CONNECTOR_LUID}", status_code=204)
        server.auth_federation.delete_connector(CONNECTOR_LUID)

    assert m.called_once


def test_auth_federation_delete_connector_by_item(server: TSC.Server) -> None:
    stub = TSC.AuthFederationConnectorItem()
    stub.luid = CONNECTOR_LUID

    with requests_mock.mock() as m:
        m.delete(f"{server.auth_federation.baseurl}/connectors/{CONNECTOR_LUID}", status_code=204)
        server.auth_federation.delete_connector(stub)

    assert m.called_once


def test_auth_federation_create_key(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.post(f"{server.auth_federation.baseurl}/keys", text=KEY_CREATE.read_text())
        key = server.auth_federation.create_key()
        body = m.request_history[0].text

    # POST /keys takes no body besides the empty tsRequest envelope.
    envelope = fromstring(body)
    assert envelope.tag == "tsRequest"
    assert len(envelope) == 0

    assert key.kid == KEY_KID
    assert key.kty == "RSA"
    assert key.alg == "RS256"
    assert key.use == "sig"
    assert key.e == "AQAB"
    assert key.n is not None and len(key.n) > 0


def test_auth_federation_activate_key(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.put(f"{server.auth_federation.baseurl}/keys/{KEY_KID}/activate", status_code=204)
        server.auth_federation.activate_key(KEY_KID)

    assert m.called_once


def test_auth_federation_activate_key_by_item(server: TSC.Server) -> None:
    stub = TSC.AuthFederationKeyItem()
    stub.kid = KEY_KID

    with requests_mock.mock() as m:
        m.put(f"{server.auth_federation.baseurl}/keys/{KEY_KID}/activate", status_code=204)
        server.auth_federation.activate_key(stub)

    assert m.called_once


def test_auth_federation_deactivate_key(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.put(f"{server.auth_federation.baseurl}/keys/{KEY_KID}/deactivate", status_code=204)
        server.auth_federation.deactivate_key(KEY_KID)

    assert m.called_once


def test_auth_federation_delete_key(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(f"{server.auth_federation.baseurl}/keys/{KEY_KID}", status_code=204)
        server.auth_federation.delete_key(KEY_KID)

    assert m.called_once


def test_auth_federation_requires_server_version_3_30(server: TSC.Server) -> None:
    server.version = "3.29"
    with pytest.raises(EndpointUnavailableError):
        server.auth_federation.get()
