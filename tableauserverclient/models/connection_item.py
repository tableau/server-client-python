import logging
from typing import Optional

from defusedxml.ElementTree import fromstring

from .connection_credentials import ConnectionCredentials
from .property_decorators import property_is_boolean
from tableauserverclient.helpers.logging import logger


class ConnectionItem:
    def __init__(self):
        self._datasource_id: Optional[str] = None
        self._datasource_name: Optional[str] = None
        self._id: Optional[str] = None
        self._connection_type: Optional[str] = None
        self.embed_password: bool = None
        self.password: Optional[str] = None
        self.server_address: Optional[str] = None
        self.server_port: Optional[str] = None
        self.username: Optional[str] = None
        self.connection_credentials: Optional[ConnectionCredentials] = None
        self._query_tagging: Optional[bool] = None

    @property
    def datasource_id(self) -> Optional[str]:
        return self._datasource_id

    @property
    def datasource_name(self) -> Optional[str]:
        return self._datasource_name

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def connection_type(self) -> Optional[str]:
        return self._connection_type

    @property
    def query_tagging(self) -> Optional[bool]:
        return self._query_tagging

    @query_tagging.setter
    @property_is_boolean
    def query_tagging(self, value: Optional[bool]):
        # if connection type = hyper, Snowflake, or Teradata, we can't change this value: it is always true
        if self._connection_type in ["hyper", "snowflake", "teradata"]:
            logger.debug(
                f"Cannot update value: Query tagging is always enabled for {self._connection_type} connections"
            )
            return
        self._query_tagging = value

    def __repr__(self):
        return "<ConnectionItem#{_id} embed={embed_password} type={_connection_type} username={username}>".format(
            **self.__dict__
        )

    @classmethod
    def from_response(cls, resp, ns) -> list["ConnectionItem"]:
        all_connection_items = list()
        parsed_response = fromstring(resp)
        all_connection_xml = parsed_response.findall(".//t:connection", namespaces=ns)
        for connection_xml in all_connection_xml:
            connection_item = cls()
            connection_item._id = connection_xml.get("id", None)
            connection_item._connection_type = connection_xml.get("type", connection_xml.get("dbClass", None))
            connection_item.embed_password = string_to_bool(connection_xml.get("embedPassword", ""))
            connection_item.server_address = connection_xml.get("serverAddress", None)
            connection_item.server_port = connection_xml.get("serverPort", None)
            connection_item.username = connection_xml.get("userName", None)
            connection_item._query_tagging = (
                string_to_bool(s) if (s := connection_xml.get("queryTagging", None)) else None
            )
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

            connection_credentials = connection_xml.find(".//t:connectionCredentials", namespaces=ns)

            if connection_credentials is not None:
                connection_item.connection_credentials = ConnectionCredentials.from_xml_element(
                    connection_credentials, ns
                )

        return all_connection_items


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s is not None and s.lower() == "true"
