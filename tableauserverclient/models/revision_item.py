import xml.etree.ElementTree as ET
from ..datetime_helpers import parse_datetime
from typing import List, Mapping, Optional, TYPE_CHECKING, Type, Union

if TYPE_CHECKING:
    from datetime import datetime

class RevisionItem(object):
    def __init__(self):
        self._resource_id: Optional[str] = None
        self._resource_name: Optional[str] = None
        self._revision_number: Optional[str] = None
        self._current: Optional[bool] = None
        self._deleted: Optional[bool] = None
        self._created_at: Optional["datetime"] = None

    @property
    def resource_id(self) -> Optional[str]:
        return self._resource_id

    @property
    def resource_name(self) -> Optional[str]:
        return self._resource_name

    @property
    def revision_number(self) -> Optional[str]:
        return self._revision_number

    @property
    def current(self) -> Optional[bool]:
        return self._current

    @property
    def deleted(self) -> Optional[bool]:
        return self._deleted

    @property
    def created_at(self) -> Optional["datetime"]:
        return self._created_at

    def __repr__(self):
        return (
            "<RevisionItem# revisionNumber={_revision_number} "
            "current={_current} deleted={_deleted}>".format(**self.__dict__)
        )

    @classmethod
    def from_response(
        cls: Type["RevisionItem"],
        resp: bytes,
        ns,
        resource_item
    ) -> List["RevisionItem"]:
        all_revision_items = list()
        parsed_response = ET.fromstring(resp)
        all_revision_xml = parsed_response.findall(".//t:revision", namespaces=ns)
        for revision_xml in all_revision_xml:
            revision_item = cls()
            revision_item._resource_id = resource_item.id
            revision_item._resource_name = resource_item.name
            revision_item._revision_number = revision_xml.get("revisionNumber", None)
            revision_item._current = string_to_bool(revision_xml.get("current", ""))
            revision_item._deleted = string_to_bool(revision_xml.get("deleted", ""))
            revision_item._created_at = parse_datetime(revision_xml.get("createdAt", None))

            all_revision_items.append(revision_item)
        return all_revision_items


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s.lower() == "true"
