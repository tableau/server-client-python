import xml.etree.ElementTree as ET
from typing import Mapping, Set, TypeVar

T = TypeVar('T', bound='TagItem')


class TagItem(object):
    @classmethod
    def from_response(cls, resp: str, ns: Mapping) -> Set[T]:
        return cls.from_xml_element(ET.fromstring(resp), ns)

    @classmethod
    def from_xml_element(cls, parsed_response: ET.ElementTree, ns: Mapping) -> Set[T]:
        all_tags = set()
        tag_elem = parsed_response.findall('.//t:tag', namespaces=ns)
        for tag_xml in tag_elem:
            tag = tag_xml.get('label', None)
            if tag is not None:
                all_tags.add(tag)
        return all_tags
