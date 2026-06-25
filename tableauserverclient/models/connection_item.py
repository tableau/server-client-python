import logging

from defusedxml.ElementTree import fromstring

from .connection_credentials import ConnectionCredentials
from .property_decorators import property_is_boolean
from tableauserverclient.helpers.logging import logger


class ConnectionItem:
    """
    Corresponds to workbook and data source connections.

    Attributes
    ----------
    datasource_id: str
        The identifier of the data source.

    datasource_name: str
        The name of the data source.

    id: str
        The identifier of the connection.

    connection_type: str
        The type of connection.

    username: str
        The username for the connection. (see ConnectionCredentials)

    password: str
        The password used for the connection. (see ConnectionCredentials)

    embed_password: bool
        Determines whether to embed the password (True) for the workbook or data source connection or not (False). (see ConnectionCredentials)

    server_address: str
        The server address for the connection.

    server_port: str
        The port used for the connection.

    auth_type: str
        Specifies the type of authentication used by the connection.

    connection_credentials: ConnectionCredentials
        The Connection Credentials object containing authentication details for
        the connection. Replaces username/password/embed_password when
        publishing a flow, document or workbook file in the request body.

    database_name: str
        The name of the database for the connection.
    """

    def __init__(self):
        self._datasource_id: str | None = None
        self._datasource_name: str | None = None
        self._id: str | None = None
        self._connection_type: str | None = None
        self.embed_password: bool = None
        self.password: str | None = None
        self.server_address: str | None = None
        self.server_port: str | None = None
        self.username: str | None = None
        self.connection_credentials: ConnectionCredentials | None = None
        self._query_tagging: bool | None = None
        self._auth_type: str | None = None
        self._database_name: str | None = None

    @property
    def datasource_id(self) -> str | None:
        return self._datasource_id

    @property
    def datasource_name(self) -> str | None:
        return self._datasource_name

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def connection_type(self) -> str | None:
        return self._connection_type

    @property
    def query_tagging(self) -> bool | None:
        return self._query_tagging

    @query_tagging.setter
    @property_is_boolean
    def query_tagging(self, value: bool | None):
        # if connection type = hyper, Snowflake, or Teradata, we can't change this value: it is always true
        if self._connection_type in ["hyper", "snowflake", "teradata"]:
            logger.debug(
                f"Cannot update value: Query tagging is always enabled for {self._connection_type} connections"
            )
            return
        self._query_tagging = value

    @property
    def auth_type(self) -> str | None:
        return self._auth_type

    @auth_type.setter
    def auth_type(self, value: str | None):
        self._auth_type = value

    @property
    def database_name(self) -> str | None:
        return self._database_name

    @database_name.setter
    def database_name(self, value: str | None):
        self._database_name = value

    def __repr__(self):
        return "<ConnectionItem#{_id} embed={embed_password} type={_connection_type} auth={_auth_type} username={username}>".format(
            **self.__dict__
        )

    @classmethod
    def from_response(cls, resp, ns) -> list["ConnectionItem"]:
        all_connection_items = list()
        parsed_response = fromstring(resp)
        all_connection_xml = parsed_response.findall(".//t:connection", namespaces=ns)
        for connection_xml in all_connection_xml:
            connection_item = cls()
            connection_item._id = connection_xml.get("id", connection_xml.get("connectionId", None))
            connection_item._connection_type = connection_xml.get("type", connection_xml.get("dbClass", None))
            connection_item.embed_password = string_to_bool(connection_xml.get("embedPassword", ""))
            connection_item.server_address = connection_xml.get("serverAddress", connection_xml.get("server", None))
            connection_item.server_port = connection_xml.get("serverPort", connection_xml.get("port", None))
            connection_item.username = connection_xml.get("userName", connection_xml.get("username", None))
            connection_item._query_tagging = (
                string_to_bool(s) if (s := connection_xml.get("queryTagging", None)) else None
            )
            connection_item._auth_type = connection_xml.get("authenticationType", None)
            # The REST API GET /connections response uses "dbName" for the database
            # name attribute.  This is different from the publish request body, which
            # uses "databaseName" (see _add_connections_element in request_factory.py).
            # Both names map to the same database_name property on ConnectionItem.
            connection_item._database_name = connection_xml.get("dbName", None)
            datasource_elem = connection_xml.find(".//t:datasource", namespaces=ns)
            if datasource_elem is not None:
                connection_item._datasource_id = datasource_elem.get("id", None)
                connection_item._datasource_name = datasource_elem.get("name", None)
            all_connection_items.append(connection_item)
        return all_connection_items

    @classmethod
    def from_xml_element(cls, parsed_response, ns) -> list["ConnectionItem"]:
        """
        <connections>
            <connection serverAddress="mysql.test.com">
                <connectionCredentials embed="true" name="test" password="secret" />
            </connection>
            <connection serverAddress="pgsql.test.com">
                <connectionCredentials embed="true" name="test" password="secret" />
                </connection>
        </connections>
        """
        all_connection_items: list["ConnectionItem"] = list()
        all_connection_xml = parsed_response.findall(".//t:connection", namespaces=ns)

        for connection_xml in all_connection_xml:
            connection_item = cls()

            connection_item.server_address = connection_xml.get("serverAddress", None)
            connection_item.server_port = connection_xml.get("serverPort", None)
            connection_item._auth_type = connection_xml.get("authenticationType", None)
            # Publish/update request bodies use "databaseName" (matching the
            # publish-request schema), while GET responses use "dbName".  See
            # from_response() above and _add_connections_element() in request_factory.py.
            connection_item._database_name = connection_xml.get("databaseName", None)

            connection_credentials = connection_xml.find(".//t:connectionCredentials", namespaces=ns)

            if connection_credentials is not None:
                connection_item.connection_credentials = ConnectionCredentials.from_xml_element(
                    connection_credentials, ns
                )

        return all_connection_items


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s is not None and s.lower() == "true"
