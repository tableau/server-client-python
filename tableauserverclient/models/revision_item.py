import xml.etree.ElementTree as ET

class RevisionItem(object):
    def __init__(self):
        self._resource_id = None
        self._resource_name = None
        self._revision_number = None
        self._current = None
        self._deleted = None
        self._created_at = None

    @property
    def resource_id(self):
        return self._resource_id

    @property
    def resource_name(self):
        return self._resource_name

    @property
    def revision_number(self):
        return self._revision_number

    @property
    def current(self):
        return self._current

    @property
    def deleted(self):
        return self._deleted

    @property
    def created_at(self):
        return self._created_at

    def __repr__(self):
        return (
            "<RevisionItem# revisionNumber={_revision_number} "
            "current={_current} deleted={_deleted}>".format(**self.__dict__)
        )

    @classmethod
    def from_response(cls, resp, ns, resource_item):
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
            revision_item._created_at = revision_xml.get("createdAt", None)

            all_revision_items.append(revision_item)
        return all_revision_items


# Used to convert string represented boolean to a boolean type
def string_to_bool(s):
    return s.lower() == "true"
