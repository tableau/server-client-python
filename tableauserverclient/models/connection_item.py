import xml.etree.ElementTree as ET


class ConnectionItem(object):
    def __init__(self):
        self._datasource_id = None
        self._datasource_name = None
        self._id = None
        self._connection_type = None
        self.embed_password = None
        self.password = None
        self.server_address = None
        self.server_port = None
        self.username = None

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
