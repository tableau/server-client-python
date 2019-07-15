import xml.etree.ElementTree as ET
import logging

from .exceptions import UnknownGranteeTypeError


logger = logging.getLogger("tableau.models.permissions_item")


class Permission:
    class GranteeType:
        User = "user"
        Group = "group"

    class CapabilityMode:
        Allow = "Allow"
        Deny = "Deny"

    class DatasourceCapabilityType:
        ChangePermissions = "ChangePermissions"
        Connect = "Connect"
        Delete = "Delete"
        ExportXml = "ExportXml"
        Read = "Read"
        Write = "Write"

    class WorkbookCapabilityType:
        AddComment = "AddComment"
        ChangeHierarchy = "ChangeHierarchy"
        ChangePermissions = "ChangePermissions"
        Delete = "Delete"
        ExportData = "ExportData"
        ExportImage = "ExportImage"
        ExportXml = "ExportXml"
        Filter = "Filter"
        Read = "Read"
        ShareView = "ShareView"
        ViewComments = "ViewComments"
        ViewUnderlyingData = "ViewUnderlyingData"
        WebAuthoring = "WebAuthoring"
        Write = "Write"

    class ProjectCapabilityType:
        ProjectLeader = "ProjectLeader"
        Read = "Read"
        Write = "Write"


class PermissionsGrantee(object):
    def __init__(self, grantee_type, grantee_id):

        if grantee_type not in [
            Permission.GranteeType.User,
            Permission.GranteeType.Group,
        ]:
            raise UnknownGranteeTypeError(grantee_type)

        self._grantee_type = grantee_type
        self._grantee_id = grantee_id

    @classmethod
    def from_xml_element(cls, xml_element):
        tag_without_namespace = xml_element.tag.split("}")[-1]
        return cls(tag_without_namespace, xml_element.get("id"))

    def to_xml_element(self):
        xml_element = ET.Element(self.grantee_type)
        xml_element.set("id", self.grantee_id)
        return xml_element

    @property
    def grantee_type(self):
        return self._grantee_type

    @property
    def grantee_id(self):
        return self._grantee_id


class PermissionsRule(object):
    def __init__(self, grantee, permissions_map=None):
        self._grantee = grantee
        self.permissions_map = permissions_map or {}

    @property
    def grantee(self):
        return self._grantee

    def to_xml_element(self):
        xml_element = ET.Element("granteeCapabilities")
        xml_element.append(self.grantee.to_xml_element())
        capabilities_element = ET.SubElement(xml_element, "capabilities")
        for permission, mode in self.permissions_map.items():
            ET.SubElement(
                capabilities_element, "capability", {"name": permission, "mode": mode}
            )
        return xml_element


class PermissionsCollection(object):
    def __init__(self, rules):
        self._rules = rules

    @property
    def rules(self):
        return self._rules

    @classmethod
    def from_response(cls, resp, ns=None):
        parsed_response = ET.fromstring(resp)

        capabilities = []
        all_xml = parsed_response.findall(".//t:granteeCapabilities", namespaces=ns)

        for grantee_capability_xml in all_xml:
            user_grantee_element = grantee_capability_xml.find(
                "./t:user", namespaces=ns
            )
            group_grantee_element = grantee_capability_xml.find(
                "./t:group", namespaces=ns
            )
            grantee_element = (
                user_grantee_element
                if user_grantee_element is not None
                else group_grantee_element
            )

            grantee = PermissionsGrantee.from_xml_element(grantee_element)

            capability_elements = grantee_capability_xml.findall(
                ".//t:capabilities/t:capability", namespaces=ns
            )
            capability_map = {
                el.get("name"): el.get("mode") for el in capability_elements
            }

            capability_item = PermissionsRule(grantee, capability_map)

            capabilities.append(capability_item)

        return cls(capabilities)

    def to_xml_element(self):
        xml_element = ET.Element("permissions")
        for permission_rule in self.rules:
            xml_element.append(permission_rule.to_xml_element())
        return xml_element
