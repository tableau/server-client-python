import datetime as dt
from pathlib import Path
import unittest

from defusedxml.ElementTree import fromstring

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.virtual_connection_item import VirtualConnectionItem

ASSET_DIR = Path(__file__).parent / "assets"

VIRTUAL_CONNECTION_GET_XML = ASSET_DIR / "virtual_connections_get.xml"


class TestVirtualConnections(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test")
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
