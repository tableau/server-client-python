import datetime as dt
import json
from typing import Callable
from collections.abc import Iterable
from xml.etree.ElementTree import Element

from defusedxml.ElementTree import fromstring

from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.connection_item import ConnectionItem
from tableauserverclient.models.exceptions import UnpopulatedPropertyError
from tableauserverclient.models.permissions_item import PermissionsRule


class VirtualConnectionItem:
    def __init__(self, name: str) -> None:
        self.name = name
        self.created_at: dt.datetime | None = None
        self.has_extracts: bool | None = None
        self._id: str | None = None
        self.is_certified: bool | None = None
        self.updated_at: dt.datetime | None = None
        self.webpage_url: str | None = None
        self._connections: Callable[[], Iterable[ConnectionItem]] | None = None
        self.project_id: str | None = None
        self.owner_id: str | None = None
        self.content: dict[str, dict] | None = None
        self.certification_note: str | None = None

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name})"

    def __repr__(self) -> str:
        return f"<{self!s}>"

    def _set_permissions(self, permissions):
        self._permissions = permissions

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def permissions(self) -> list[PermissionsRule]:
        if self._permissions is None:
            error = "Workbook item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._permissions()

    @property
    def connections(self) -> Iterable[ConnectionItem]:
        if self._connections is None:
            raise AttributeError("connections not populated. Call populate_connections() first.")
        return self._connections()

    @classmethod
    def from_response(cls, response: bytes, ns: dict[str, str]) -> list["VirtualConnectionItem"]:
        parsed_response = fromstring(response)
        return [cls.from_xml(xml, ns) for xml in parsed_response.findall(".//t:virtualConnection[@name]", ns)]

    @classmethod
    def from_xml(cls, xml: Element, ns: dict[str, str]) -> "VirtualConnectionItem":
        v_conn = cls(xml.get("name", ""))
        v_conn._id = xml.get("id", None)
        v_conn.webpage_url = xml.get("webpageUrl", None)
        v_conn.created_at = parse_datetime(xml.get("createdAt", None))
        v_conn.updated_at = parse_datetime(xml.get("updatedAt", None))
        v_conn.is_certified = string_to_bool(s) if (s := xml.get("isCertified", None)) else None
        v_conn.certification_note = xml.get("certificationNote", None)
        v_conn.has_extracts = string_to_bool(s) if (s := xml.get("hasExtracts", None)) else None
        v_conn.project_id = p.get("id", None) if ((p := xml.find(".//t:project[@id]", ns)) is not None) else None
        v_conn.owner_id = o.get("id", None) if ((o := xml.find(".//t:owner[@id]", ns)) is not None) else None
        v_conn.content = json.loads(c.text or "{}") if ((c := xml.find(".//t:content", ns)) is not None) else None
        return v_conn


def string_to_bool(s: str) -> bool:
    return s.lower() in ["true", "1", "t", "y", "yes"]
