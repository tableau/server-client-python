import xml.etree.ElementTree as ET
import logging

from .exceptions import UnknownGranteeTypeError
from . import UserItem, GroupItem

logger = logging.getLogger('tableau.models.permissions_item')


class Permission:

    class Mode:
        Allow = 'Allow'
        Deny = 'Deny'

    class Capability:
        AddComment = 'AddComment'
        ChangeHierarchy = 'ChangeHierarchy'
        ChangePermissions = 'ChangePermissions'
        Connect = 'Connect'
        Delete = 'Delete'
        ExportData = 'ExportData'
        ExportImage = 'ExportImage'
        ExportXml = 'ExportXml'
        Filter = 'Filter'
        ProjectLeader = 'ProjectLeader'
        Read = 'Read'
        ShareView = 'ShareView'
        ViewComments = 'ViewComments'
        ViewUnderlyingData = 'ViewUnderlyingData'
        WebAuthoring = 'WebAuthoring'
        Write = 'Write'


class PermissionsRule(object):

    def __init__(self, grantee, capabilities):
        self.grantee = grantee
        self.capabilities = capabilities


class ExplicitPermissions(object):
    def __init__(self, rules=None):
        self._rules = rules

    def _set_values(self, rules):
        self._rules = rules

    @property
    def rules(self):
        return self._rules

    @classmethod
    def from_response(cls, resp, ns=None):
        permissions = ExplicitPermissions()
        parsed_response = ET.fromstring(resp)

        rules = []
        permissions_rules_list_xml = parsed_response.findall('.//t:granteeCapabilities',
                                                             namespaces=ns)

        for grantee_capability_xml in permissions_rules_list_xml:
            capability_dict = {}

            grantee_element = grantee_capability_xml.findall('.//*[@id]', namespaces=ns).pop()
            grantee_id = grantee_element.get('id', None)
            grantee_type = grantee_element.tag.split('}').pop()

            if grantee_id is None:
                logger.error('Cannot find grantee type in response')
                raise UnknownGranteeTypeError()

            if grantee_type == 'user':
                grantee = UserItem.for_permissions(grantee_id)
            else:
                grantee = GroupItem.for_permissions(grantee_id)

            for capability_xml in grantee_capability_xml.findall(
                    './/t:capabilities/t:capability', namespaces=ns):
                name = capability_xml.get('name')
                mode = capability_xml.get('mode')

                capability_dict[name] = mode

            rule = PermissionsRule(grantee,
                                   capability_dict)
            rules.append(rule)

        permissions._set_values(rules)
        return permissions