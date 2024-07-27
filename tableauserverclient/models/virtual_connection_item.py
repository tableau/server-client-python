import datetime as dt
from typing import Callable, Dict, Iterable, List, Optional
from xml.etree.ElementTree import Element

from defusedxml.ElementTree import fromstring

from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.connection_item import ConnectionItem


class VirtualConnectionItem:
    def __init__(self, name: str) -> None:
        self.name = name
        self.created_at: Optional[dt.datetime] = None
        self.has_extracts: Optional[bool] = None
        self.id: Optional[str] = None
        self.is_certified: Optional[bool] = None
        self.updated_at: Optional[dt.datetime] = None
        self.webpage_url: Optional[str] = None
        self._connections: Optional[Callable[[], Iterable[ConnectionItem]]] = None

    def __str__(self) -> str:
        return f"{self.__class__.__qualname__}(name={self.name})"

    def __repr__(self) -> str:
        return f"<{self!s}>"

    @property
    def connections(self) -> Iterable[ConnectionItem]:
        if self._connections is None:
            raise AttributeError("connections not populated. Call populate_connections() first.")
        return self._connections()

    @classmethod
    def from_response(cls, response: bytes, ns: Dict[str, str]) -> List["VirtualConnectionItem"]:
        parsed_response = fromstring(response)
        return [cls.from_xml(xml, ns) for xml in parsed_response.findall(".//t:virtualConnection[@id]", ns)]

    @classmethod
    def from_xml(cls, xml: Element, ns: Dict[str, str]) -> "VirtualConnectionItem":
        v_conn = cls(xml.get("name", ""))
        v_conn.id = xml.get("id", None)
        v_conn.webpage_url = xml.get("webpageUrl", None)
        v_conn.created_at = parse_datetime(xml.get("createdAt", None))
        v_conn.updated_at = parse_datetime(xml.get("updatedAt", None))
        v_conn.is_certified = string_to_bool(s) if (s := xml.get("isCertified", None)) else None
        v_conn.has_extracts = string_to_bool(s) if (s := xml.get("hasExtracts", None)) else None
        return v_conn


def string_to_bool(s: str) -> bool:
    return s.lower() in ["true", "1", "t", "y", "yes"]
