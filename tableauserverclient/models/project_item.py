import logging
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import fromstring

from .exceptions import UnpopulatedPropertyError
from .property_decorators import property_is_enum, property_not_empty

from typing import List, Optional


class ProjectItem(object):
    class ContentPermissions:
        LockedToProject: str = "LockedToProject"
        ManagedByOwner: str = "ManagedByOwner"
        LockedToProjectWithoutNested: str = "LockedToProjectWithoutNested"

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        content_permissions: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> None:
        self._content_permissions = None
        self._id: Optional[str] = None
        self.description: Optional[str] = description
        self.name: str = name
        self.content_permissions: Optional[str] = content_permissions
        self.parent_id: Optional[str] = parent_id

        self._permissions = None
        self._default_workbook_permissions = None
        self._default_datasource_permissions = None
        self._default_flow_permissions = None
        self._default_lens_permissions = None

    @property
    def content_permissions(self):
        return self._content_permissions

    @content_permissions.setter
    @property_is_enum(ContentPermissions)
    def content_permissions(self, value: Optional[str]) -> None:
        self._content_permissions = value

    @property
    def permissions(self):
        if self._permissions is None:
            error = "Project item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._permissions()

    @property
    def default_datasource_permissions(self):
        if self._default_datasource_permissions is None:
            error = "Project item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._default_datasource_permissions()

    @property
    def default_workbook_permissions(self):
        if self._default_workbook_permissions is None:
            error = "Project item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._default_workbook_permissions()

    @property
    def default_flow_permissions(self):
        if self._default_flow_permissions is None:
            error = "Project item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._default_flow_permissions()

    @property
    def default_lens_permissions(self):
        if self._default_lens_permissions is None:
            error = "Project item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._default_lens_permissions()

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @property_not_empty
    def name(self, value: str) -> None:
        self._name = value

    @property
    def owner_id(self) -> Optional[str]:
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: str) -> None:
        raise NotImplementedError("REST API does not currently support updating project owner.")

    def is_default(self):
        return self.name.lower() == "default"

    def _parse_common_tags(self, project_xml, ns):
        if not isinstance(project_xml, ET.Element):
            project_xml = fromstring(project_xml).find(".//t:project", namespaces=ns)

        if project_xml is not None:
            (
                _,
                name,
                description,
                content_permissions,
                parent_id,
            ) = self._parse_element(project_xml)
            self._set_values(None, name, description, content_permissions, parent_id)
        return self

    def _set_values(self, project_id, name, description, content_permissions, parent_id, owner_id):
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
        if owner_id:
            self._owner_id = owner_id

    def _set_permissions(self, permissions):
        self._permissions = permissions

    def _set_default_permissions(self, permissions, content_type):
        attr = "_default_{content}_permissions".format(content=content_type)
        setattr(
            self,
            attr,
            permissions,
        )
        fetch_call = getattr(self, attr)
        logging.getLogger().info({"type": attr, "value": fetch_call()})
        return fetch_call()

    @classmethod
    def from_response(cls, resp, ns) -> List["ProjectItem"]:
        all_project_items = list()
        parsed_response = fromstring(resp)
        all_project_xml = parsed_response.findall(".//t:project", namespaces=ns)

        for project_xml in all_project_xml:
            (
                id,
                name,
                description,
                content_permissions,
                parent_id,
                owner_id,
            ) = cls._parse_element(project_xml)
            project_item = cls(name)
            project_item._set_values(id, name, description, content_permissions, parent_id, owner_id)
            all_project_items.append(project_item)
        return all_project_items

    @staticmethod
    def _parse_element(project_xml):
        id = project_xml.get("id", None)
        name = project_xml.get("name", None)
        description = project_xml.get("description", None)
        content_permissions = project_xml.get("contentPermissions", None)
        parent_id = project_xml.get("parentProjectId", None)
        owner_id = None
        for owner in project_xml:
            owner_id = owner.get("id", None)

        return id, name, description, content_permissions, parent_id, owner_id
