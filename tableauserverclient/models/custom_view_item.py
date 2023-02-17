from datetime import datetime
from defusedxml.ElementTree import fromstring
from typing import Callable, List, Optional

from .exceptions import UnpopulatedPropertyError
from ..datetime_helpers import parse_datetime


class CustomViewItem(object):
    def __init__(self) -> None:
        self._content_url: Optional[str] = None
        self._created_at: Optional["datetime"] = None
        self._id: Optional[str] = None
        self._image: Optional[Callable[[], bytes]] = None
        self._name: Optional[str] = None
        self._owner_id: Optional[str] = None
        self._updated_at: Optional["datetime"] = None
        self._view_id: Optional[str] = None
        self._workbook_id: Optional[str] = None

    def _set_image(self, image):
        self._image = image

    @property
    def content_url(self) -> Optional[str]:
        return self._content_url

    @property
    def created_at(self) -> Optional["datetime"]:
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
    def updated_at(self) -> Optional["datetime"]:
        return self._updated_at

    @property
    def workbook_id(self) -> Optional[str]:
        return self._workbook_id

    @classmethod
    def from_response(cls, resp, ns, workbook_id="") -> List["CustomViewItem"]:
        return cls.from_xml_element(fromstring(resp), ns, workbook_id)

    """
    <customView
    id="37d015c6-bc28-4c88-989c-72c0a171f7aa"
    name="New name 2"
    createdAt="2016-02-03T23:35:09Z"
    updatedAt="2022-09-28T23:56:01Z"
    shared="false">
      <view id="8e33ff19-a7a4-4aa5-9dd8-a171e2b9c29f" name="circle"/>
      <workbook id="2fbe87c9-a7d8-45bf-b2b3-877a26ec9af5" name="marks and viz types 2"/>
      <owner id="cdfe8548-84c8-418e-9b33-2c0728b2398a" name="workgroupuser"/>
    </customView>
    """

    @classmethod
    def from_xml_element(cls, parsed_response, ns, workbook_id="") -> List["CustomViewItem"]:
        all_view_items = list()
        all_view_xml = parsed_response.findall(".//t:customView", namespaces=ns)
        for custom_view_xml in all_view_xml:
            cv_item = cls()
            view_elem = custom_view_xml.find(".//t:view", namespaces=ns)
            workbook_elem = custom_view_xml.find(".//t:workbook", namespaces=ns)
            owner_elem = custom_view_xml.find(".//t:owner", namespaces=ns)
            cv_item._created_at = parse_datetime(custom_view_xml.get("createdAt", None))
            cv_item._updated_at = parse_datetime(custom_view_xml.get("updatedAt", None))
            cv_item._id = custom_view_xml.get("id", None)
            cv_item._name = custom_view_xml.get("name", None)

            if owner_elem is not None:
                cv_item._owner_id = owner_elem.get("id", None)

            if view_elem is not None:
                cv_item._view_id = view_elem.get("id", None)

            if workbook_id:
                cv_item._workbook_id = workbook_id
            elif workbook_elem is not None:
                cv_item._workbook_id = workbook_elem.get("id", None)

            all_view_items.append(cv_item)
        return all_view_items
