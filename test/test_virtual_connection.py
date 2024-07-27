from pathlib import Path
import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.virtual_connection_item import VirtualConnectionItem

ASSET_DIR = Path(__file__).parent / "assets"

VIRTUAL_CONNECTION_GET_XML = ASSET_DIR / "virtual_connections_get.xml"
VIRTUAL_CONNECTION_POPULATE_CONNECTIONS = ASSET_DIR / "virtual_connection_populate_connections.xml"
VC_DB_CONN_UPDATE = ASSET_DIR / "virtual_connection_database_connection_update.xml"


class TestVirtualConnections(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test")

        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.server.version = "3.18"

        self.baseurl = f"{self.server.baseurl}/sites/{self.server.site_id}/virtualConnections"
        return super().setUp()

    def test_from_xml(self):
        items = VirtualConnectionItem.from_response(VIRTUAL_CONNECTION_GET_XML.read_bytes(), self.server.namespace)

        assert len(items) == 1
        virtual_connection = items[0]
        assert virtual_connection.created_at == parse_datetime("2024-05-30T09:00:00Z")
        assert not virtual_connection.has_extracts
        assert virtual_connection.id == "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        assert virtual_connection.is_certified
        assert virtual_connection.name == "vconn"
        assert virtual_connection.updated_at == parse_datetime("2024-06-18T09:00:00Z")
        assert virtual_connection.webpage_url == "https://test/#/site/site-name/virtualconnections/3"

    def test_virtual_connection_get(self):
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=VIRTUAL_CONNECTION_GET_XML.read_text())
            items, pagination_item = self.server.virtual_connections.get()

        assert len(items) == 1
        assert pagination_item.total_available == 1
        assert items[0].name == "vconn"

    def test_virtual_connection_populate_connections(self):
        vconn = VirtualConnectionItem("vconn")
        vconn.id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{vconn.id}/connections", text=VIRTUAL_CONNECTION_POPULATE_CONNECTIONS.read_text())
            vc_out = self.server.virtual_connections.populate_connections(vconn)
            connection_list = list(vconn.connections)

        assert vc_out is vconn
        assert vc_out._connections is not None

        assert len(connection_list) == 1
        connection = connection_list[0]
        assert connection.id == "37ca6ced-58d7-4dcf-99dc-f0a85223cbef"
        assert connection.connection_type == "postgres"
        assert connection.server_address == "localhost"
        assert connection.server_port == "5432"
        assert connection.username == "pgadmin"

    def test_virtual_connection_update_connection_db_connection(self):
        vconn = VirtualConnectionItem("vconn")
        vconn.id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        connection = TSC.ConnectionItem()
        connection._id = "37ca6ced-58d7-4dcf-99dc-f0a85223cbef"
        connection.server_address = "localhost"
        connection.server_port = "5432"
        connection.username = "pgadmin"
        connection.password = "password"
        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{vconn.id}/connections/{connection.id}/modify", text=VC_DB_CONN_UPDATE.read_text())
            updated_connection = self.server.virtual_connections.update_connection_db_connection(vconn, connection)

        assert updated_connection.id == "37ca6ced-58d7-4dcf-99dc-f0a85223cbef"
        assert updated_connection.server_address == "localhost"
        assert updated_connection.server_port == "5432"
        assert updated_connection.username == "pgadmin"
        assert updated_connection.password is None
