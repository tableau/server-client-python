import xml.etree.ElementTree as ET
import logging

from .exceptions import UnknownGranteeTypeError


logger = logging.getLogger('tableau.models.permissions_item')


class Permission:
    class GranteeType:
        User = 'user'
        Group = 'group'

    class CapabilityMode:
        Allow = 'Allow'
        Deny = 'Deny'

    class DatasourceCapabilityType:
        ChangePermissions = 'ChangePermissions'
        Connect = 'Connect'
        Delete = 'Delete'
        ExportXml = 'ExportXml'
        Read = 'Read'
        Write = 'Write'

    class WorkbookCapabilityType:
        AddComment = 'AddComment'
        ChangeHierarchy = 'ChangeHierarchy'
        ChangePermissions = 'ChangePermissions'
        Delete = 'Delete'
        ExportData = 'ExportData'
        ExportImage = 'ExportImage'
        ExportXml = 'ExportXml'
        Filter = 'Filter'
        Read = 'Read'
        ShareView = 'ShareView'
        ViewComments = 'ViewComments'
        ViewUnderlyingData = 'ViewUnderlyingData'
        WebAuthoring = 'WebAuthoring'
        Write = 'Write'

    class ProjectCapabilityType:
        ProjectLeader = 'ProjectLeader'
        Read = 'Read'
        Write = 'Write'


class CapabilityItem(object):
    def __init__(self, type=None, object_id=None, map={}):
        self._type = type
        self._object_id = object_id
        self.map = map

    @property
    def type(self):
        return self._type

    @property
    def object_id(self):
        return self._object_id


class PermissionsRuleItem(object):
    def __init__(self):
        self._rules = None

    def _set_values(self, rules):
        self._rules = rules

    @property
    def rules(self):
        return self._rules

    @classmethod
    def from_response(cls, resp, ns=None):
        permissions = PermissionsRuleItem()
        parsed_response = ET.fromstring(resp)

        capabilities = {}
        all_xml = parsed_response.findall('.//t:granteeCapabilities',
                                          namespaces=ns)

        for grantee_capability_xml in all_xml:
            grantee_id = None
            grantee_type = None
            capability_map = {}

            try:
                grantee_id = grantee_capability_xml.find('.//t:group',
                                                         namespaces=ns)\
                                                    .get('id')
                grantee_type = Permission.GranteeType.Group
            except AttributeError:
                pass
            try:
                grantee_id = grantee_capability_xml.find('.//t:user',
                                                         namespaces=ns)\
                                                    .get('id')
                grantee_type = Permission.GranteeType.User
            except AttributeError:
                pass

            if grantee_id is None:
                logger.error('Cannot find grantee type in response')
                raise UnknownGranteeTypeError()

            for capability_xml in grantee_capability_xml.findall(
                    './/t:capabilities/t:capability', namespaces=ns):
                name = capability_xml.get('name')
                mode = capability_xml.get('mode')

                capability_map[name] = mode

            capability_item = CapabilityItem(grantee_type, grantee_id,
                                             capability_map)
            capabilities[(grantee_type, grantee_id)] = capability_item

        permissions._set_values(capabilities)
        return permissions


## Compat Tests

PermissionsItem = PermissionsRuleItem