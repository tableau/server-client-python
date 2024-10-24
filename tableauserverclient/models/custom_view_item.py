from datetime import datetime

from defusedxml import ElementTree
from defusedxml.ElementTree import fromstring, tostring
from typing import Callable, List, Optional

from .exceptions import UnpopulatedPropertyError
from .user_item import UserItem
from .view_item import ViewItem
from .workbook_item import WorkbookItem
from ..datetime_helpers import parse_datetime


class CustomViewItem(object):
    def __init__(self, id: Optional[str] = None, name: Optional[str] = None) -> None:
        self._content_url: Optional[str] = None  # ?
        self._created_at: Optional["datetime"] = None
        self._id: Optional[str] = id
        self._image: Optional[Callable[[], bytes]] = None
        self._name: Optional[str] = name
        self._shared: Optional[bool] = False
        self._updated_at: Optional["datetime"] = None

        self._owner: Optional[UserItem] = None
        self._view: Optional[ViewItem] = None
        self._workbook: Optional[WorkbookItem] = None

    def __repr__(self: "CustomViewItem"):
        view_info = ""
        if self._view:
            view_info = " view='{}'".format(self._view.name or self._view.id or "unknown")
        wb_info = ""
        if self._workbook:
            wb_info = " workbook='{}'".format(self._workbook.name or self._workbook.id or "unknown")
        owner_info = ""
        if self._owner:
            owner_info = " owner='{}'".format(self._owner.name or self._owner.id or "unknown")
        return "<CustomViewItem id={} name=`{}`{}{}{}>".format(self.id, self.name, view_info, wb_info, owner_info)

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

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def shared(self) -> Optional[bool]:
        return self._shared

    @shared.setter
    def shared(self, value: bool):
        self._shared = value

    @property
    def updated_at(self) -> Optional["datetime"]:
        return self._updated_at

    @property
    def owner(self) -> Optional[UserItem]:
        return self._owner

    @owner.setter
    def owner(self, value: UserItem):
        self._owner = value

    @property
    def workbook(self) -> Optional[WorkbookItem]:
        return self._workbook

    @property
    def view(self) -> Optional[ViewItem]:
        return self._view

    @classmethod
    def from_response(cls, resp, ns, workbook_id="") -> Optional["CustomViewItem"]:
        item = cls.list_from_response(resp, ns, workbook_id)
        if not item or len(item) == 0:
            return None
        else:
            return item[0]

    @classmethod
    def list_from_response(cls, resp, ns, workbook_id="") -> List["CustomViewItem"]:
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
            view_elem: ElementTree = custom_view_xml.find(".//t:view", namespaces=ns)
            workbook_elem: str = custom_view_xml.find(".//t:workbook", namespaces=ns)
            owner_elem: str = custom_view_xml.find(".//t:owner", namespaces=ns)
            cv_item._created_at = parse_datetime(custom_view_xml.get("createdAt", None))
            cv_item._updated_at = parse_datetime(custom_view_xml.get("updatedAt", None))
            cv_item._content_url = custom_view_xml.get("contentUrl", None)
            cv_item._id = custom_view_xml.get("id", None)
            cv_item._name = custom_view_xml.get("name", None)
            cv_item._shared = string_to_bool(custom_view_xml.get("shared", None))

            if owner_elem is not None:
                parsed_owners = UserItem.from_response_as_owner(tostring(custom_view_xml), ns)
                if parsed_owners and len(parsed_owners) > 0:
                    cv_item._owner = parsed_owners[0]

            if view_elem is not None:
                parsed_views = ViewItem.from_response(tostring(custom_view_xml), ns)
                if parsed_views and len(parsed_views) > 0:
                    cv_item._view = parsed_views[0]

            if workbook_id:
                cv_item._workbook = WorkbookItem(workbook_id)
            elif workbook_elem is not None:
                parsed_workbooks = WorkbookItem.from_response(tostring(custom_view_xml), ns)
                if parsed_workbooks and len(parsed_workbooks) > 0:
                    cv_item._workbook = parsed_workbooks[0]

            all_view_items.append(cv_item)
        return all_view_items


def string_to_bool(s: Optional[str]) -> bool:
    return (s or "").lower() == "true"
