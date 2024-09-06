from typing import Dict, List, Optional
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import fromstring

from tableauserverclient.models.group_item import GroupItem
from tableauserverclient.models.reference_item import ResourceReference


class GroupSetItem:
    tag_name: str = "groupSet"

    def __init__(self, name: Optional[str] = None) -> None:
        self.name = name
        self.id: Optional[str] = None
        self.groups: List["GroupItem"] = []
        self.group_count: int = 0

    def __str__(self) -> str:
        name = self.name
        id = self.id
        return f"<{self.__class__.__qualname__}({name=}, {id=})>"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_response(cls, response: bytes, ns: Dict[str, str]) -> List["GroupSetItem"]:
        parsed_response = fromstring(response)
        all_groupset_xml = parsed_response.findall(".//t:groupSet", namespaces=ns)
        return [cls.from_xml(xml, ns) for xml in all_groupset_xml]

    @classmethod
    def from_xml(cls, groupset_xml: ET.Element, ns: Dict[str, str]) -> "GroupSetItem":
        def get_group(group_xml: ET.Element) -> GroupItem:
            group_item = GroupItem()
            group_item._id = group_xml.get("id")
            group_item.name = group_xml.get("name")
            return group_item

        group_set_item = cls()
        group_set_item.name = groupset_xml.get("name")
        group_set_item.id = groupset_xml.get("id")
        group_set_item.group_count = int(count) if (count := groupset_xml.get("groupCount")) else 0
        group_set_item.groups = [
            get_group(group_xml) for group_xml in groupset_xml.findall(".//t:group", namespaces=ns)
        ]

        return group_set_item

    @staticmethod
    def as_reference(id_: str) -> ResourceReference:
        return ResourceReference(id_, GroupSetItem.tag_name)
