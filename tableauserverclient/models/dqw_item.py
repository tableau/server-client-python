import xml.etree.ElementTree as ET
from enum import Enum
from ..datetime_helpers import parse_datetime


class DQWItem(object):
    class WarningType:
        WARNING = "WARNING"
        DEPRECATED = "DEPRECATED"
        STALE = "STALE"
        SENSITIVE_DATA = "SENSITIVE_DATA"
        MAINTENANCE = "MINTENANCE"

    def __init__(self, warning_type="WARNING", message=None, active=True, severe=False):
        self.id = None
        # content related
        self.content_id = None
        self.content_type = None

        # DQW related
        self.warning_type = warning_type
        self.message = message
        self.active = active
        self.severe = severe
        self.created_at = None
        self.updated_at = None

        # owner
        self.owner_display_name = None
        self.owner_id = None

    @classmethod
    def from_response(cls, resp, ns):
        return cls.from_xml_element(ET.fromstring(resp), ns)

    @classmethod
    def from_xml_element(cls, parsed_response, ns):
        all_dqws = []
        dqw_elem_list = parsed_response.findall(".//t:dataQualityWarning", namespaces=ns)
        for dqw_elem in dqw_elem_list:
            dqw = DQWItem()
            dqw.id = dqw_elem.get("id", None)
            dqw.owner_display_name = dqw_elem.get("userDisplayName", None)
            dqw.content_id = dqw_elem.get("contentId", None)
            dqw.content_type = dqw_elem.get("contentType", None)
            dqw.message = dqw_elem.get("message", None)
            dqw.warning_type = dqw_elem.get("type", None)

            is_active = dqw_elem.get("isActive", None)
            if is_active is not None:
                dqw.active = string_to_bool(is_active)

            is_severe = dqw_elem.get("isSevere", None)
            if is_severe is not None:
                dqw.severe = string_to_bool(is_severe)

            dqw.created_at = parse_datetime(dqw_elem.get("createdAt", None))
            dqw.updated_at = parse_datetime(dqw_elem.get("updatedAt", None))

            owner_id = None
            owner_tag = dqw_elem.find(".//t:owner", namespaces=ns)
            if owner_tag is not None:
                owner_id = owner_tag.get("id", None)
            dqw.owner_id = owner_id

            all_dqws.append(dqw)

        return all_dqws


# Used to convert string represented boolean to a boolean type
def string_to_bool(s):
    return s.lower() == "true"
