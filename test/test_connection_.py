import xml.etree.ElementTree as ET
from pathlib import Path

import tableauserverclient as TSC

import pytest

ASSETS_DIR = Path(__file__).parent / "assets"
NS = {"t": "http://tableau.com/api"}


def test_require_boolean_query_tag_fails() -> None:
    conn = TSC.ConnectionItem()
    conn._connection_type = "postgres"
    with pytest.raises(ValueError):
        conn.query_tagging = "no"  # type: ignore[assignment]


def test_set_query_tag_normal_conn() -> None:
    conn = TSC.ConnectionItem()
    conn._connection_type = "postgres"
    conn.query_tagging = True
    assert conn.query_tagging


@pytest.mark.parametrize("conn_type", ["hyper", "teradata", "snowflake"])
def test_ignore_query_tag(conn_type: str) -> None:
    conn = TSC.ConnectionItem()
    conn._connection_type = conn_type
    conn.query_tagging = True
    assert conn.query_tagging is None


def test_database_name_default_none() -> None:
    conn = TSC.ConnectionItem()
    assert conn.database_name is None


def test_database_name_getter_setter() -> None:
    conn = TSC.ConnectionItem()
    conn.database_name = "my_database"
    assert conn.database_name == "my_database"


def test_database_name_from_response_parses_db_name() -> None:
    xml = """<?xml version='1.0' encoding='UTF-8'?>
<tsResponse xmlns="http://tableau.com/api">
    <connections>
        <connection id="abc-123" type="sqlserver" serverAddress="db.example.com"
                    userName="user" embedPassword="false" dbName="SalesDB"/>
    </connections>
</tsResponse>"""
    connections = TSC.ConnectionItem.from_response(xml, NS)
    assert len(connections) == 1
    assert connections[0].database_name == "SalesDB"


def test_database_name_from_response_none_when_absent() -> None:
    xml = """<?xml version='1.0' encoding='UTF-8'?>
<tsResponse xmlns="http://tableau.com/api">
    <connections>
        <connection id="abc-123" type="sqlserver" serverAddress="db.example.com"
                    userName="user" embedPassword="false"/>
    </connections>
</tsResponse>"""
    connections = TSC.ConnectionItem.from_response(xml, NS)
    assert len(connections) == 1
    assert connections[0].database_name is None


def test_database_name_parsed_from_xml_asset() -> None:
    response_xml = (ASSETS_DIR / "datasource_populate_connections.xml").read_text()
    connections = TSC.ConnectionItem.from_response(response_xml, NS)
    assert len(connections) == 2
    conn_with_db = next(c for c in connections if c.id == "be786ae0-d2bf-4a4b-9b34-e2de8d2d4488")
    conn_without_db = next(c for c in connections if c.id == "970e24bc-e200-4841-a3e9-66e7d122d77e")
    assert conn_with_db.database_name == "SalesDB"
    assert conn_without_db.database_name is None


def test_database_name_round_trip() -> None:
    """database_name parsed from GET response (dbName) round-trips through
    _add_connections_element which emits databaseName in the publish request."""
    import xml.etree.ElementTree as ET
    from tableauserverclient.server.request_factory import _add_connections_element

    # Parse from a GET-style response (attribute name: dbName)
    xml = """<?xml version='1.0' encoding='UTF-8'?>
<tsResponse xmlns="http://tableau.com/api">
    <connections>
        <connection id="abc-123" type="sqlserver" serverAddress="db.example.com"
                    userName="user" embedPassword="false" dbName="Northwind"/>
    </connections>
</tsResponse>"""
    connections = TSC.ConnectionItem.from_response(xml, NS)
    assert len(connections) == 1
    conn = connections[0]
    assert conn.database_name == "Northwind"

    # Now emit as a publish request element and confirm databaseName is used
    conn.server_address = "db.example.com"  # already set, but make it explicit
    parent_elem = ET.Element("connections")
    _add_connections_element(parent_elem, conn)
    connection_elem = parent_elem.find("connection")
    assert connection_elem is not None
    assert connection_elem.attrib.get("databaseName") == "Northwind"
    assert "dbName" not in connection_elem.attrib
