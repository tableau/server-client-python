import logging
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import fromstring
from .exceptions import UnknownGranteeTypeError, UnpopulatedPropertyError
from .group_item import GroupItem
from .user_item import UserItem

logger = logging.getLogger("tableau.models.permissions_item")

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .reference_item import ResourceReference


class Permission:
    class Mode:
        Allow = "Allow"
        Deny = "Deny"

    class Capability:
        AddComment = "AddComment"
        ChangeHierarchy = "ChangeHierarchy"
        ChangePermissions = "ChangePermissions"
        Connect = "Connect"
        Delete = "Delete"
        Execute = "Execute"
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
        RunExplainData = "RunExplainData"
        CreateRefreshMetrics = "CreateRefreshMetrics"
        SaveAs = "SaveAs"


class PermissionsRule(object):
    def __init__(self, grantee: "ResourceReference", capabilities: Dict[str, str]) -> None:
        self.grantee = grantee
        self.capabilities = capabilities

    def __str__(self):
        return "<PermissionsRule grantee={}, capabilities={}>".format(self.grantee, self.capabilities)

    __repr__ = __str__

    @classmethod
    def from_response(cls, resp, ns=None) -> List["PermissionsRule"]:
        parsed_response = fromstring(resp)

        rules = []
        permissions_rules_list_xml = parsed_response.findall(".//t:granteeCapabilities", namespaces=ns)

        for grantee_capability_xml in permissions_rules_list_xml:
            capability_dict: Dict[str, str] = {}

            grantee = PermissionsRule._parse_grantee_element(grantee_capability_xml, ns)

            for capability_xml in grantee_capability_xml.findall(".//t:capabilities/t:capability", namespaces=ns):
                name = capability_xml.get("name")
                mode = capability_xml.get("mode")

                if name is None or mode is None:
                    logger.error("Capability was not valid: {}".format(capability_xml))
                    raise UnpopulatedPropertyError()
                else:
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
