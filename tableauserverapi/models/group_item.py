import xml.etree.ElementTree as ET
from exceptions import UnpopulatedPropertyError
from .. import NAMESPACE


class GroupItem(object):
    def __init__(self, name):
        self._id = None
        self._domain_name = None
        self._users = None
        self._name = None
        self.name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value:
            error = 'Name must be defined.'
            raise ValueError(error)
        else:
            self._name = value

    @property
    def id(self):
        return self._id

    @property
    def domain_name(self):
        return self._domain_name

    @property
    def users(self):
        if self._users is None:
            error = "Group must be populated with users first."
            raise UnpopulatedPropertyError(error)
        return self._users

    def _set_users(self, users):
        self._users = users

    @classmethod
    def from_response(cls, resp):
        all_group_items = list()
        parsed_response = ET.fromstring(resp)
        all_group_xml = parsed_response.findall('.//t:group', namespaces=NAMESPACE)
        for group_xml in all_group_xml:
            name = group_xml.get('name', None)
            group_item = cls(name)
            group_item._id = group_xml.get('id', None)

            domain_elem = group_xml.find('.//t:domain', namespaces=NAMESPACE)
            if domain_elem is not None:
                group_item._domain_name = domain_elem.get('name', None)
            all_group_items.append(group_item)
        return all_group_items
