import xml.etree.ElementTree as ET
from .property_decorators import property_is_enum, property_not_empty


class ProjectItem(object):
    class ContentPermissions:
        LockedToProject = 'LockedToProject'
        ManagedByOwner = 'ManagedByOwner'

    def __init__(self, name, description=None, content_permissions=None, parent_id=None):
        self._content_permissions = None
        self._id = None
        self.description = description
        self.name = name
        self.content_permissions = content_permissions
        self.parent_id = parent_id

    @property
    def content_permissions(self):
        return self._content_permissions

    @content_permissions.setter
    @property_is_enum(ContentPermissions)
    def content_permissions(self, value):
        self._content_permissions = value

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @name.setter
    @property_not_empty
    def name(self, value):
        self._name = value

    def is_default(self):
        return self.name.lower() == 'default'

    def _parse_common_tags(self, project_xml):
        if not isinstance(project_xml, ET.Element):
            project_xml = ET.fromstring(project_xml).find('.//t:project', namespaces=NAMESPACE)

        if project_xml is not None:
            (_, name, description, content_permissions, parent_id) = self._parse_element(project_xml)
            self._set_values(None, name, description, content_permissions, parent_id)
        return self

    def _set_values(self, project_id, name, description, content_permissions, parent_id):
        if project_id is not None:
            self._id = project_id
        if name:
            self._name = name
        if description:
            self.description = description
        if content_permissions:
            self._content_permissions = content_permissions
        if parent_id:
            self.parent_id = parent_id

    @classmethod
    def from_response(cls, resp, ns):
        all_project_items = list()
        parsed_response = ET.fromstring(resp)
        all_project_xml = parsed_response.findall('.//t:project', namespaces=ns)

        for project_xml in all_project_xml:
            (id, name, description, content_permissions, parent_id) = cls._parse_element(project_xml)
            project_item = cls(name)
            project_item._set_values(id, name, description, content_permissions, parent_id)
            all_project_items.append(project_item)
        return all_project_items

    @staticmethod
    def _parse_element(project_xml):
        id = project_xml.get('id', None)
        name = project_xml.get('name', None)
        description = project_xml.get('description', None)
        content_permissions = project_xml.get('contentPermissions', None)
        parent_id = project_xml.get('parentProjectId', None)

        return id, name, description, content_permissions, parent_id
