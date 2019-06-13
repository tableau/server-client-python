import xml.etree.ElementTree as ET

from .property_decorators import property_is_enum, property_not_empty
from .exceptions import UnpopulatedPropertyError


class ColumnItem(object):
    def __init__(self, name, description=None):
        self._content_permissions = None
        self._id = None
        self.description = description
        self.name = name

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    @property_not_empty
    def name(self, value):
        self._name = value

    def _set_values(self, id, name, description, remote_type, embedded, schema):
        if id is not None:
            self._id = id
        if name:
            self._name = name
        if description:
            self.description = description
        if embedded:
            self.embedded = embedded
        if schema:
            self.schema = schema
        if remote_type:
            self.remote_type = remote_type

    @classmethod
    def from_response(cls, resp, ns):
        all_column_items = list()
        parsed_response = ET.fromstring(resp)
        all_column_xml = parsed_response.findall('.//t:column', namespaces=ns)

        for column_xml in all_column_xml:
            (id, name, description, remote_type, embedded, schema) = cls._parse_element(column_xml, ns)
            column_item = cls(name)
            column_item._set_values(id, name, description, remote_type, embedded, schema)
            all_column_items.append(column_item)
        return all_column_items

    @staticmethod
    def _parse_element(column_xml, ns):
        id = column_xml.get('id', None)
        name = column_xml.get('name', None)
        description = column_xml.get('description', None)
        remote_type = column_xml.get('remoteType', None)
        embedded = column_xml.get('embedded', None)
        schema = column_xml.get('schema', None)

        return id, name, description, remote_type, embedded, schema

# Used to convert string represented boolean to a boolean type
def string_to_bool(s):
    return s.lower() == 'true'