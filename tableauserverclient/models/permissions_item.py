import xml.etree.ElementTree as ET
import logging

from .exceptions import UnknownGranteeTypeError
from .user_item import UserItem
from .group_item import GroupItem

logger = logging.getLogger("tableau.models.permissions_item")

from typing import Dict, List, Mapping, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .reference_item import ResourceReference


class Permission:
    class Mode:
        Allow: str = "Allow"
        Deny: str = "Deny"

    class Capability:
        AddComment: str = "AddComment"
        ChangeHierarchy: str = "ChangeHierarchy"
        ChangePermissions: str = "ChangePermissions"
        Connect: str = "Connect"
        Delete: str = "Delete"
        Execute: str = "Execute"
        ExportData: str = "ExportData"
        ExportImage: str = "ExportImage"
        ExportXml: str = "ExportXml"
        Filter: str = "Filter"
        ProjectLeader: str = "ProjectLeader"
        Read: str = "Read"
        ShareView: str = "ShareView"
        ViewComments: str = "ViewComments"
        ViewUnderlyingData: str = "ViewUnderlyingData"
        WebAuthoring: str = "WebAuthoring"
        Write: str = "Write"

    class Resource:
        Workbook: str = "workbook"
        Datasource: str = "datasource"
        Flow: str = "flow"
        Table: str = "table"
        Database: str = "database"
        View: str = "view"


class PermissionsRule(object):
    def __init__(self, grantee: "ResourceReference", capabilities: Dict[Optional[str], Optional[str]]) -> None:
        self.grantee = grantee
        self.capabilities = capabilities

    @classmethod
    def from_response(cls, resp, ns=None) -> List["PermissionsRule"]:
        parsed_response = ET.fromstring(resp)

        rules = []
        permissions_rules_list_xml = parsed_response.findall(".//t:granteeCapabilities", namespaces=ns)

        for grantee_capability_xml in permissions_rules_list_xml:
            capability_dict: Dict[Optional[str], Optional[str]] = {}

            grantee = PermissionsRule._parse_grantee_element(grantee_capability_xml, ns)

            for capability_xml in grantee_capability_xml.findall(".//t:capabilities/t:capability", namespaces=ns):
                name = capability_xml.get("name")
                mode = capability_xml.get("mode")

                capability_dict[name] = mode

            rule = PermissionsRule(grantee, capability_dict)
            rules.append(rule)

        return rules

    @staticmethod
    def _parse_grantee_element(grantee_capability_xml: ET.Element, ns: Optional[Dict[str, str]]) -> "ResourceReference":
        """Use Xpath magic and some string splitting to get the right object type from the xml"""

        # Get the first element in the tree with an 'id' attribute
        grantee_element = grantee_capability_xml.findall(".//*[@id]", namespaces=ns).pop()
        grantee_id = grantee_element.get("id", None)
        grantee_type = grantee_element.tag.split("}").pop()

        if grantee_id is None:
            logger.error("Cannot find grantee type in response")
            raise UnknownGranteeTypeError()

        if grantee_type == "user":
            grantee = UserItem.as_reference(grantee_id)
        elif grantee_type == "group":
            grantee = GroupItem.as_reference(grantee_id)
        else:
            raise UnknownGranteeTypeError("No support for grantee type of {}".format(grantee_type))

        return grantee
