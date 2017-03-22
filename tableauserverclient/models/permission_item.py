import xml.etree.ElementTree as ET

from .property_decorators import property_not_nullable
from .. import NAMESPACE


class CapabilityItem(object):
    Allow = "Allow"
    Deny = "Deny"

    AddComment = "AddComment"
    ChangeHierarchy = "ChangeHierarchy"
    ChangePermissions = "ChangePermissions"
    Connect = "Connect"
    Delete = "Delete"
    ExportData = "ExportData"
    ExportImage = "ExportImage"
    ExportXml = "ExportXml"
    Filter = "Filter"
    ProjectLeader = "ProjectLeader"
    Read = "Read"
    ShareView = "ShareView"
    ViewComments = "ViewComments"
    ViewUnderlyingData = "ViewUnderlyingData"
    WebAuthoring = "WebAuthoring"
    Write = "Write"

    def __init__(self):
        self._allowed = set()
        self._denied = set()

    @property
    def allowed(self):
        return self._allowed

    @allowed.setter
    def allowed(self, value):
        self._allowed.add(value)

    @property
    def denied(self):
        return self._denied

    @denied.setter
    def denied(self, value):
        self._denied.add(value)


class PermissionItem(object):
    Group = 'group'
    User = 'user'

    def __init__(self):
        self._grantee_type = None
        self._grantee_id = None
        self._user_capabilities = set()
        self._group_capabilities = set()

    @property
    def grantee_type(self):
        return self._grantee_type

    @grantee_type.setter
    @property_not_nullable
    def grantee_type(self, value):
        self._grantee_type = value

    @property
    def grantee_id(self):
        return self._grantee_id

    @grantee_id.setter
    @property_not_nullable
    def grantee_id(self, value):
        self._grantee_id = value

    @property
    def user_capabilities(self):
        return self._user_capabilities

    @user_capabilities.setter
    def user_capabilities(self, capability):
        self._user_capabilities.add(capability)

    @property
    def group_capabilities(self):
        return self._group_capabilities

    @group_capabilities.setter
    def group_capabilities(self, capability):
        self._group_capabilities.add(capability)

    @classmethod
    def from_response(cls, resp):
        all_permission_items = list()
        parsed_response = ET.fromstring(resp)
        all_grantee_xml = parsed_response.findall('.//t:granteeCapabilities', namespaces=NAMESPACE)
        for grantee_xml in all_grantee_xml:
            permission_item = cls()
            all_capability_xml = grantee_xml.findall('.//t:capability', namespaces=NAMESPACE)
            cap_items = CapabilityItem()
            for capability_xml in all_capability_xml:
                name = capability_xml.get('name', None)
                mode = capability_xml.get('mode', None)
                if mode == CapabilityItem.Allow:
                    cap_items.allowed = name
                elif mode == CapabilityItem.Deny:
                    cap_items.denied = name
            group_elem = grantee_xml.find('.//t:group', namespaces=NAMESPACE)
            user_elem = grantee_xml.find('.//t:user', namespaces=NAMESPACE)
            if group_elem is not None:
                permission_item._grantee_id = group_elem.get('id', None)
                permission_item._grantee_type = permission_item.Group
                permission_item.group_capabilities = cap_items
            elif user_elem is not None:
                permission_item._grantee_id = user_elem.get('id', None)
                permission_item._grantee_type = permission_item.User
                permission_item.user_capabilities = cap_items
            all_permission_items.append(permission_item)
        return all_permission_items

