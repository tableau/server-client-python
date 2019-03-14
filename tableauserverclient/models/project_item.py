import xml.etree.ElementTree as ET
from .property_decorators import property_is_enum, property_not_empty, property_not_nullable
from ..datetime_helpers import parse_datetime


class ProjectItem(object):
    class ContentPermissions:
        LockedToProject = 'LockedToProject'
        ManagedByOwner = 'ManagedByOwner'

    def __init__(self, name, description=None, content_permissions=None, parent_id=None):
        self._created_at = None
        self._id = None
        self._owner_id = None
        self._owner_name = None
        self._top_level_project = None
        self._updated_at = None

        self.content_permissions = content_permissions
        self.description = description
        self.name = name
        self.parent_id = parent_id

    @property
    def content_permissions(self):
        return self._content_permissions

    @content_permissions.setter
    @property_is_enum(ContentPermissions)
    def content_permissions(self, value):
        self._content_permissions = value

    @property
    def created_at(self):
        return self._created_at

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    @property_not_empty
    @property_not_nullable
    def name(self, value):
        self._name = value

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def owner_name(self):
        return self._owner_name

    @property
    def parent_id(self):
        return self._parent_id

    @parent_id.setter
    def parent_id(self, value):
        self._parent_id = value

    @property
    def top_level_project(self):
        return self._top_level_project

    @property
    def updated_at(self):
        return self._updated_at

    def is_default(self):
        return self.name.lower() == 'default'

    def _set_values(self, project_fields):
        if 'contentPermissions' in project_fields:
            self._content_permissions = project_fields['contentPermissions']
        if 'createdAt' in project_fields:
            self._created_at = parse_datetime(project_fields['createdAt'])
        if 'description' in project_fields:
            self._description = project_fields['description']
        if 'id' in project_fields:
            self._id = project_fields['id']
        if 'name' in project_fields:
            self._name = project_fields['name']
        if 'parentProjectId' in project_fields:
            self._parent_id = project_fields['parentProjectId']
        if 'topLevelProject' in project_fields:
            self._top_level_project = string_to_bool(project_fields['topLevelProject'])
        if 'updatedAt' in project_fields:
            self._updated_at = parse_datetime(project_fields['updatedAt'])
        if 'owner' in project_fields:
            owner_fields = project_fields['owner']
            if 'id' in owner_fields:
                self._owner_id = owner_fields['id']
            if 'name' in owner_fields:
                self._owner_name = owner_fields['name']
        if self.parent_id is not None:
            self._top_level_project = False

    @classmethod
    def from_response(cls, resp, ns):
        all_project_items = list()
        parsed_response = ET.fromstring(resp)
        all_project_xml = parsed_response.findall('.//t:project', namespaces=ns)

        for project_xml in all_project_xml:
            project_fields = cls._parse_element(project_xml, ns)
            project_item = cls(project_fields['name'])
            project_item._set_values(project_fields)
            all_project_items.append(project_item)
        return all_project_items

    @staticmethod
    def _parse_element(project_xml, ns):
        project_fields = project_xml.attrib
        owner_elem = project_xml.find('.//t:owner', namespaces=ns)
        if owner_elem is not None:
            owner_fields = owner_elem.attrib
            project_fields['owner'] = owner_fields

        return project_fields


# Used to convert string represented boolean to a boolean type
def string_to_bool(s):
    return s.lower() == 'true'
