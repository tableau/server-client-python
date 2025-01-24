import logging
import xml.etree.ElementTree as ET
from .property_decorators import property_is_enum, property_not_empty, property_not_nullable
from ..datetime_helpers import parse_datetime
from typing import Optional

from defusedxml.ElementTree import fromstring

from tableauserverclient.models.exceptions import UnpopulatedPropertyError
from tableauserverclient.models.property_decorators import property_is_enum, property_not_empty


class ProjectItem:
    ERROR_MSG = "Project item must be populated with permissions first."

    class ContentPermissions:
        LockedToProject: str = "LockedToProject"
        ManagedByOwner: str = "ManagedByOwner"
        LockedToProjectWithoutNested: str = "LockedToProjectWithoutNested"

    def __repr__(self):
        return "<Project {} {} parent={} permissions={}>".format(
            self._id, self.name, self.parent_id or "None (Top level)", self.content_permissions or "Not Set"
        )

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        content_permissions: Optional[str] = None,
        parent_id: Optional[str] = None,
        samples: Optional[bool] = None,
    ) -> None:
        self._content_permissions = None
        self._id: Optional[str] = None
        self.description: Optional[str] = description
        self.name: str = name
        self.content_permissions: Optional[str] = content_permissions
        self.parent_id: Optional[str] = parent_id
        self._samples: Optional[bool] = samples
        self._owner_id: Optional[str] = None

        self._created_at = None
        self._owner_name: Optional[str] = None
        self._top_level_project: Optional[bool] = None
        self._updated_at = None

        self._permissions = None
        self._default_workbook_permissions = None
        self._default_datasource_permissions = None
        self._default_flow_permissions = None
        self._default_lens_permissions = None
        self._default_datarole_permissions = None
        self._default_metric_permissions = None
        self._default_virtualconnection_permissions = None
        self._default_database_permissions = None
        self._default_table_permissions = None

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
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._permissions()

    @property
    def default_datasource_permissions(self):
        if self._default_datasource_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_datasource_permissions()

    @property
    def default_workbook_permissions(self):
        if self._default_workbook_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_workbook_permissions()

    @property
    def default_flow_permissions(self):
        if self._default_flow_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_flow_permissions()

    @property
    def default_lens_permissions(self):
        if self._default_lens_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_lens_permissions()

    @property
    def default_datarole_permissions(self):
        if self._default_datarole_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_datarole_permissions()

    @property
    def default_metric_permissions(self):
        if self._default_metric_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_metric_permissions()

    @property
    def default_virtualconnection_permissions(self):
        if self._default_virtualconnection_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_virtualconnection_permissions()

    @property
    def default_database_permissions(self):
        if self._default_database_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_database_permissions()

    @property
    def default_table_permissions(self):
        if self._default_table_permissions is None:
            raise UnpopulatedPropertyError(self.ERROR_MSG)
        return self._default_table_permissions()

    @property
    def id(self) -> Optional[str]:
        return self._id

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
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

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

    @property
    def owner_id(self) -> Optional[str]:
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: str) -> None:
        self._owner_id = value

    def is_default(self):
        return self.name.lower() == "default"

    def _parse_common_tags(self, project_xml, ns):
        return ProjectItem.from_xml(ProjectItem, project_xml, ns)

    def _set_permissions(self, permissions):
        self._permissions = permissions

    def _set_default_permissions(self, permissions, content_type):
        attr = f"_default_{content_type}_permissions"
        setattr(
            self,
            attr,
            permissions,
        )

    @classmethod
    def from_response(cls, resp, ns) -> list["ProjectItem"]:
        all_project_items = list()
        parsed_response = fromstring(resp)
        all_project_xml = parsed_response.findall(".//t:project", namespaces=ns)

        for project_xml in all_project_xml:
            project_item = cls.from_xml(project_xml, ns)
            all_project_items.append(project_item)
        return all_project_items

    @classmethod
    def from_xml(cls, project_xml, ns) -> "ProjectItem":
        project_item = cls()
        if project_xml.get("contentPermissions", None):
            project_item._content_permissions = project_xml.get("contentPermissions")
        if project_xml.get("createdAt", None):
            project_item._created_at = parse_datetime(project_xml.get("createdAt"))
        if project_xml.get("description", None):
            project_item._description = project_xml.get("description")
        if project_xml.get("id", None):
            project_item._id = project_xml.get("id")
        if project_xml.get("name", None):
            project_item._name = project_xml.get("name")
        if project_xml.get("parentProjectId", None):
            project_item._parent_id = project_xml.get("parentProjectId")
        if project_xml.get("topLevelProject", None):
            project_item._top_level_project = ProjectItem.string_to_bool(project_xml.get("topLevelProject"))
        if project_xml.get("updatedAt", None):
            project_item._updated_at = parse_datetime(project_xml.get("updatedAt"))

        if project_item.parent_id is not None:
            project_item._top_level_project = False

        owner_elem = project_xml.find(".//t:owner", ns)
        if owner_elem is not None:
            project_item._owner_id = owner_elem.get("id", None)
            project_item._owner_name = owner_elem.get("name", None)

        return project_item

    # Used to convert string represented boolean to a boolean type
    def string_to_bool(s):
        return s.lower() == "true"
