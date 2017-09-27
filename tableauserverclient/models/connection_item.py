import xml.etree.ElementTree as ET


class ConnectionItem(object):
    def __init__(self, datasource_id=None, _datasource_name=None, _id=None, _connection_type=None, embed_password=None,
                 password=None, server_address=None, server_port=None, username=None):
        self._datasource_id = datasource_id
        self._datasource_name = _datasource_name
        self._id = _id
        self._connection_type = _connection_type
        self.embed_password = embed_password
        self.password = password
        self.server_address = server_address
        self.server_port = server_port
        self.username = username

    @property
    def datasource_id(self):
        return self._datasource_id

    @property
    def datasource_name(self):
        return self._datasource_name

    @property
    def id(self):
        return self._id

    @property
    def connection_type(self):
        return self._connection_type

    # def set_embed_password(self, embed_password):
    #     self.embed_password = embed_password
    #
    # def set_password(self, password):
    #     self.password = password
    #
    # def set_server_address(self, server_address):
    #     self.server_address = server_address
    #
    # def set_server_port(self, server_port):
    #     self.server_port = server_port
    #
    # def set_username(self, username):
    #     self.username = username
    #
    # def _set_connection_type(self, connection_type):
    #     self.connection_type = connection_type

    @classmethod
    def from_response(cls, resp, ns):
        all_connection_items = list()
        parsed_response = ET.fromstring(resp)
        all_connection_xml = parsed_response.findall('.//t:connection', namespaces=ns)
        for connection_xml in all_connection_xml:
            connection_item = cls()
            connection_item._id = connection_xml.get('id', None)
            connection_item._connection_type = connection_xml.get('type', None)
            connection_item.server_address = connection_xml.get('serverAddress', None)
            connection_item.server_port = connection_xml.get('serverPort', None)
            connection_item.username = connection_xml.get('userName', None)
            datasource_elem = connection_xml.find('.//t:datasource', namespaces=ns)
            if datasource_elem is not None:
                connection_item._datasource_id = datasource_elem.get('id', None)
                connection_item._datasource_name = datasource_elem.get('name', None)
            all_connection_items.append(connection_item)
        return all_connection_items
