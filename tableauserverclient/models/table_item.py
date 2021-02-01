import xml.etree.ElementTree as ET

from .property_decorators import property_not_empty, property_is_boolean
from .exceptions import UnpopulatedPropertyError
from .permissions_item import PermissionsRule
from .column_item import ColumnItem

from typing import List, Mapping, TypeVar

T = TypeVar('T', bound='TableItem')


class TableItem(object):
    def __init__(self, name: str, description: str = None) -> T:
        self._id = None
        self.description = description
        self.name = name

        self._contact_id = None
        self._certified = None
        self._certification_note = None
        self._permissions = None
        self._schema = None

        self._columns = None

    @property
    def permissions(self) -> List[PermissionsRule]:
        if self._permissions is None:
            error = "Project item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._permissions()

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @property_not_empty
    def name(self, value: str):
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def certified(self) -> bool:
        return self._certified

    @certified.setter
    @property_is_boolean
    def certified(self, value: bool):
        self._certified = value

    @property
    def certification_note(self) -> str:
        return self._certification_note

    @certification_note.setter
    def certification_note(self, value: str):
        self._certification_note = value

    @property
    def contact_id(self) -> str:
        return self._contact_id

    @contact_id.setter
    def contact_id(self, value: str):
        self._contact_id = value

    @property
    def schema(self):
        return self._schema

    @property
    def columns(self) -> List[ColumnItem]:
        if self._columns is None:
            error = "Table must be populated with columns first."
            raise UnpopulatedPropertyError(error)
        #  Each call to `.columns` should create a new pager, this just runs the callable
        return self._columns()

    def _set_columns(self, columns: List[ColumnItem]):
        self._columns = columns

    def _set_values(self, table_values):
        if 'id' in table_values:
            self._id = table_values['id']

        if 'name' in table_values:
            self._name = table_values['name']

        if 'description' in table_values:
            self._description = table_values['description']

        if 'isCertified' in table_values:
            self._certified = string_to_bool(table_values['isCertified'])

        if 'certificationNote' in table_values:
            self._certification_note = table_values['certificationNote']

        if 'isEmbedded' in table_values:
            self._embedded = string_to_bool(table_values['isEmbedded'])

        if 'schema' in table_values:
            self._schema = table_values['schema']

        if 'contact' in table_values:
            self._contact_id = table_values['contact']['id']

    def _set_permissions(self, permissions):
        self._permissions = permissions

    @classmethod
    def from_response(cls, resp: str, ns: Mapping) -> List[T]:
        all_table_items = list()
        parsed_response = ET.fromstring(resp)
        all_table_xml = parsed_response.findall('.//t:table', namespaces=ns)

        for table_xml in all_table_xml:
            parsed_table = cls._parse_element(table_xml, ns)
            table_item = cls(parsed_table["name"])
            table_item._set_values(parsed_table)
            all_table_items.append(table_item)
        return all_table_items

    @staticmethod
    def _parse_element(table_xml, ns):

        table_values = table_xml.attrib.copy()

        contact = table_xml.find('.//t:contact', namespaces=ns)
        if contact is not None:
            table_values['contact'] = contact.attrib.copy()

        return table_values


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s.lower() == 'true'
