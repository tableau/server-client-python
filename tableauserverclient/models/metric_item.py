import xml.etree.ElementTree as ET
from ..datetime_helpers import parse_datetime
from .property_decorators import property_is_boolean, property_is_datetime
from .tag_item import TagItem
from typing import List, Optional, TYPE_CHECKING, Set

if TYPE_CHECKING:
    from datetime import datetime


class MetricItem(object):
    def __init__(self, name: Optional[str] = None):
        self._id: Optional[str] = None
        self._name: Optional[str] = name
        self._description: Optional[str] = None
        self._webpage_url: Optional[str] = None
        self._created_at: Optional["datetime"] = None
        self._updated_at: Optional["datetime"] = None
        self._suspended: Optional[bool] = None
        self._project_id: Optional[str] = None
        self._project_name: Optional[str] = None
        self._owner_id: Optional[str] = None
        self._view_id: Optional[str] = None
        self._initial_tags: Set[str] = set()
        self.tags: Set[str] = set()

    @property
    def id(self) -> Optional[str]:
        return self._id

    @id.setter
    def id(self, value: Optional[str]) -> None:
        self._id = value

    @property
    def name(self) -> Optional[str]:
        return self._name

    @name.setter
    def name(self, value: Optional[str]) -> None:
        self._name = value

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._description = value

    @property
    def webpage_url(self) -> Optional[str]:
        return self._webpage_url

    @property
    def created_at(self) -> Optional["datetime"]:
        return self._created_at

    @created_at.setter
    @property_is_datetime
    def created_at(self, value: "datetime") -> None:
        self._created_at = value

    @property
    def updated_at(self) -> Optional["datetime"]:
        return self._updated_at

    @updated_at.setter
    @property_is_datetime
    def updated_at(self, value: "datetime") -> None:
        self._updated_at = value

    @property
    def suspended(self) -> Optional[bool]:
        return self._suspended

    @suspended.setter
    @property_is_boolean
    def suspended(self, value: bool) -> None:
        self._suspended = value

    @property
    def project_id(self) -> Optional[str]:
        return self._project_id

    @project_id.setter
    def project_id(self, value: Optional[str]) -> None:
        self._project_id = value

    @property
    def project_name(self) -> Optional[str]:
        return self._project_name

    @project_name.setter
    def project_name(self, value: Optional[str]) -> None:
        self._project_name = value

    @property
    def owner_id(self) -> Optional[str]:
        return self._owner_id

    @owner_id.setter
    def owner_id(self, value: Optional[str]) -> None:
        self._owner_id = value

    @property
    def view_id(self) -> Optional[str]:
        return self._view_id

    @view_id.setter
    def view_id(self, value: Optional[str]) -> None:
        self._view_id = value

    def __repr__(self):
        return "<MetricItem# name={_name} id={_id} owner_id={_owner_id}>".format(**vars(self))

    @classmethod
    def from_response(
        cls,
        resp: bytes,
        ns,
    ) -> List["MetricItem"]:
        all_metric_items = list()
        parsed_response = ET.fromstring(resp)
        all_metric_xml = parsed_response.findall(".//t:metric", namespaces=ns)
        for metric_xml in all_metric_xml:
            metric_item = cls()
            metric_item._id = metric_xml.get("id", None)
            metric_item._name = metric_xml.get("name", None)
            metric_item._description = metric_xml.get("description", None)
            metric_item._webpage_url = metric_xml.get("webpageUrl", None)
            metric_item._created_at = parse_datetime(metric_xml.get("createdAt", None))
            metric_item._updated_at = parse_datetime(metric_xml.get("updatedAt", None))
            metric_item._suspended = string_to_bool(metric_xml.get("suspended", ""))
            for owner in metric_xml.findall(".//t:owner", namespaces=ns):
                metric_item._owner_id = owner.get("id", None)

            for project in metric_xml.findall(".//t:project", namespaces=ns):
                metric_item._project_id = project.get("id", None)
                metric_item._project_name = project.get("name", None)

            for view in metric_xml.findall(".//t:underlyingView", namespaces=ns):
                metric_item._view_id = view.get("id", None)

            tags = set()
            tags_elem = metric_xml.find(".//t:tags", namespaces=ns)
            if tags_elem is not None:
                all_tags = TagItem.from_xml_element(tags_elem, ns)
                tags = all_tags

            metric_item.tags = tags
            metric_item._initial_tags = tags

            all_metric_items.append(metric_item)
        return all_metric_items


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s.lower() == "true"
