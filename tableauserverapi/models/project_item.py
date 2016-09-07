import xml.etree.ElementTree as ET
from .. import NAMESPACE


class ProjectItem(object):
    class ContentPermissions:
        LockedToProject = 'LockedToProject'
        ManagedByOwner = 'ManagedByOwner'

    def __init__(self, name, description=None, content_permissions=None):
        self._content_permissions = None
        self._id = None
        self._name = None
        self.description = description

        # Invoke setter
        self.name = name

        if content_permissions:
            # In order to invoke the setter method to validate content_permissions,
            # _content_permissions must be initialized first.
            self.content_permissions = content_permissions

    @property
    def content_permissions(self):
        return self._content_permissions

    @content_permissions.setter
    def content_permissions(self, value):
        if value and not hasattr(ProjectItem.ContentPermissions, value):
            error = 'Invalid content permission defined.'
            raise ValueError(error)
        else:
            self._content_permissions = value

    @property
    def id(self):
        return self._id

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

    def is_default(self):
        return self.name.lower() == 'default'

    def _parse_common_tags(self, project_xml):
        if not isinstance(project_xml, ET.Element):
            project_xml = ET.fromstring(project_xml).find('.//t:project', namespaces=NAMESPACE)

        if project_xml is not None:
            (_, name, description, content_permissions) = self._parse_element(project_xml)
            self._set_values(None, name, description, content_permissions)
        return self

    def _set_values(self, project_id, name, description, content_permissions):
        if project_id is not None:
            self._id = project_id
        if name:
            self._name = name
        if description:
            self.description = description
        if content_permissions:
            self._content_permissions = content_permissions

    @classmethod
    def from_response(cls, resp):
        all_project_items = list()
        parsed_response = ET.fromstring(resp)
        all_project_xml = parsed_response.findall('.//t:project', namespaces=NAMESPACE)

        for project_xml in all_project_xml:
            (id, name, description, content_permissions) = cls._parse_element(project_xml)
            project_item = cls(name)
            project_item._set_values(id, name, description, content_permissions)
            all_project_items.append(project_item)
        return all_project_items

    @staticmethod
    def _parse_element(project_xml):
        id = project_xml.get('id', None)
        name = project_xml.get('name', None)
        description = project_xml.get('description', None)
        content_permissions = project_xml.get('contentPermissions', None)

        return id, name, description, content_permissions
