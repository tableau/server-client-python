import copy
from datetime import datetime
from requests import Response
from typing import Callable, Optional
from collections.abc import Iterator

from defusedxml.ElementTree import fromstring

from tableauserverclient.datetime_helpers import parse_datetime
from .exceptions import UnpopulatedPropertyError
from .permissions_item import PermissionsRule
from .tag_item import TagItem


class ViewItem:
    def __init__(self) -> None:
        self._content_url: Optional[str] = None
        self._created_at: Optional[datetime] = None
        self._id: Optional[str] = None
        self._image: Optional[Callable[[], bytes]] = None
        self._initial_tags: set[str] = set()
        self._name: Optional[str] = None
        self._owner_id: Optional[str] = None
        self._preview_image: Optional[Callable[[], bytes]] = None
        self._project_id: Optional[str] = None
        self._pdf: Optional[Callable[[], bytes]] = None
        self._csv: Optional[Callable[[], Iterator[bytes]]] = None
        self._excel: Optional[Callable[[], Iterator[bytes]]] = None
        self._total_views: Optional[int] = None
        self._sheet_type: Optional[str] = None
        self._updated_at: Optional[datetime] = None
        self._workbook_id: Optional[str] = None
        self._permissions: Optional[Callable[[], list[PermissionsRule]]] = None
        self.tags: set[str] = set()
        self._data_acceleration_config = {
            "acceleration_enabled": None,
            "acceleration_status": None,
        }

    def __str__(self):
        return "<ViewItem {} '{}' contentUrl='{}' project={}>".format(
            self._id, self.name, self.content_url, self.project_id
        )

    def __repr__(self):
        return self.__str__() + "  { " + ", ".join(" % s: % s" % item for item in vars(self).items()) + "}"

    def _set_preview_image(self, preview_image):
        self._preview_image = preview_image

    def _set_image(self, image):
        self._image = image

    def _set_pdf(self, pdf):
        self._pdf = pdf

    def _set_csv(self, csv):
        self._csv = csv

    def _set_excel(self, excel):
        self._excel = excel

    @property
    def content_url(self) -> Optional[str]:
        return self._content_url

    @property
    def created_at(self) -> Optional[datetime]:
        return self._created_at

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def image(self) -> bytes:
        if self._image is None:
            error = "View item must be populated with its png image first."
            raise UnpopulatedPropertyError(error)
        return self._image()

    @property
    def name(self) -> Optional[str]:
        return self._name

    @property
    def owner_id(self) -> Optional[str]:
        return self._owner_id

    @property
    def preview_image(self) -> bytes:
        if self._preview_image is None:
            error = "View item must be populated with its preview image first."
            raise UnpopulatedPropertyError(error)
        return self._preview_image()

    @property
    def project_id(self) -> Optional[str]:
        return self._project_id

    @property
    def pdf(self) -> bytes:
        if self._pdf is None:
            error = "View item must be populated with its pdf first."
            raise UnpopulatedPropertyError(error)
        return self._pdf()

    @property
    def csv(self) -> Iterator[bytes]:
        if self._csv is None:
            error = "View item must be populated with its csv first."
            raise UnpopulatedPropertyError(error)
        return self._csv()

    @property
    def excel(self) -> Iterator[bytes]:
        if self._excel is None:
            error = "View item must be populated with its excel first."
            raise UnpopulatedPropertyError(error)
        return self._excel()

    @property
    def sheet_type(self) -> Optional[str]:
        return self._sheet_type

    @property
    def total_views(self):
        if self._total_views is None:
            error = "Usage statistics must be requested when querying for view."
            raise UnpopulatedPropertyError(error)
        return self._total_views

    @property
    def updated_at(self) -> Optional[datetime]:
        return self._updated_at

    @property
    def workbook_id(self) -> Optional[str]:
        return self._workbook_id

    @property
    def data_acceleration_config(self):
        return self._data_acceleration_config

    @data_acceleration_config.setter
    def data_acceleration_config(self, value):
        self._data_acceleration_config = value

    @property
    def permissions(self) -> list[PermissionsRule]:
        if self._permissions is None:
            error = "View item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._permissions()

    def _set_permissions(self, permissions: Callable[[], list[PermissionsRule]]) -> None:
        self._permissions = permissions

    @classmethod
    def from_response(cls, resp: "Response", ns, workbook_id="") -> list["ViewItem"]:
        return cls.from_xml_element(fromstring(resp), ns, workbook_id)

    @classmethod
    def from_xml_element(cls, parsed_response, ns, workbook_id="") -> list["ViewItem"]:
        all_view_items = list()
        all_view_xml = parsed_response.findall(".//t:view", namespaces=ns)
        for view_xml in all_view_xml:
            view_item = cls.from_xml(view_xml, ns, workbook_id)
            all_view_items.append(view_item)
        return all_view_items

    @classmethod
    def from_xml(cls, view_xml, ns, workbook_id="") -> "ViewItem":
        view_item = cls()
        usage_elem = view_xml.find(".//t:usage", namespaces=ns)
        workbook_elem = view_xml.find(".//t:workbook", namespaces=ns)
        owner_elem = view_xml.find(".//t:owner", namespaces=ns)
        project_elem = view_xml.find(".//t:project", namespaces=ns)
        tags_elem = view_xml.find(".//t:tags", namespaces=ns)
        data_acceleration_config_elem = view_xml.find(".//t:dataAccelerationConfig", namespaces=ns)
        view_item._created_at = parse_datetime(view_xml.get("createdAt", None))
        view_item._updated_at = parse_datetime(view_xml.get("updatedAt", None))
        view_item._id = view_xml.get("id", None)
        view_item._name = view_xml.get("name", None)
        view_item._content_url = view_xml.get("contentUrl", None)
        view_item._sheet_type = view_xml.get("sheetType", None)
        if usage_elem is not None:
            total_view = usage_elem.get("totalViewCount", None)
            if total_view:
                view_item._total_views = int(total_view)
        if owner_elem is not None:
            view_item._owner_id = owner_elem.get("id", None)
        if project_elem is not None:
            view_item._project_id = project_elem.get("id", None)
        if workbook_id:
            view_item._workbook_id = workbook_id
        elif workbook_elem is not None:
            view_item._workbook_id = workbook_elem.get("id", None)
        if tags_elem is not None:
            tags = TagItem.from_xml_element(tags_elem, ns)
            view_item.tags = tags
            view_item._initial_tags = copy.copy(tags)
        if data_acceleration_config_elem is not None:
            data_acceleration_config = parse_data_acceleration_config(data_acceleration_config_elem)
            view_item.data_acceleration_config = data_acceleration_config
        return view_item


def parse_data_acceleration_config(data_acceleration_elem):
    data_acceleration_config = dict()

    acceleration_enabled = data_acceleration_elem.get("accelerationEnabled", None)
    if acceleration_enabled is not None:
        acceleration_enabled = string_to_bool(acceleration_enabled)

    acceleration_status = data_acceleration_elem.get("accelerationStatus", None)

    data_acceleration_config["acceleration_enabled"] = acceleration_enabled
    data_acceleration_config["acceleration_status"] = acceleration_status
    return data_acceleration_config


def string_to_bool(s: str) -> bool:
    return s.lower() == "true"
