import xml.etree.ElementTree as ET
from .. import NAMESPACE


class PermissionItem(object):
    Group = 'group'
    User = 'user'

    def __init__(self):
        self._grantee_type = None
        self._grantee_id = None
        self.permissions = {}

    @property
    def grantee_type(self):
        return self._grantee_type

    @property
    def grantee_id(self):
        return self._grantee_id

    @classmethod
    def from_response(cls, resp):
        all_permission_items = list()
        parsed_response = ET.fromstring(resp)
        all_grantee_xml = parsed_response.findall('.//t:granteeCapabilities', namespaces=NAMESPACE)
        for grantee_xml in all_grantee_xml:
            permission_item = cls()
            all_capability_xml = grantee_xml.findall('.//t:capability', namespaces=NAMESPACE)
            for capability_xml in all_capability_xml:
                name = capability_xml.get('name', None)
                mode = capability_xml.get('mode', None)
                permission_item.permissions[name] = mode

            group_elem = grantee_xml.find('.//t:group', namespaces=NAMESPACE)
            user_elem = grantee_xml.find('.//t:user', namespaces=NAMESPACE)
            if group_elem is not None:
                permission_item._grantee_id = group_elem.get('id', None)
                permission_item._grantee_type = permission_item.Group
            elif user_elem is not None:
                permission_item._grantee_id = user_elem.get('id', None)
                permission_item._grantee_type = permission_item.User
            all_permission_items.append(permission_item)
        return all_permission_items
