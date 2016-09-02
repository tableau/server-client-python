import xml.etree.ElementTree as ET
from .. import NAMESPACE


class TagItem(object):
    @classmethod
    def from_response(cls, resp):
        return cls.from_xml_element(ET.fromstring(resp))

    @classmethod
    def from_xml_element(cls, parsed_response):
        all_tags = set()
        tag_elem = parsed_response.findall('.//t:tag', namespaces=NAMESPACE)
        for tag_xml in tag_elem:
            tag = tag_xml.get('label', None)
            if tag is not None:
                all_tags.add(tag)
        return all_tags
