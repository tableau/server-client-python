from typing import Optional, TypeVar, overload
from typing_extensions import Self

from defusedxml.ElementTree import fromstring

T = TypeVar("T")


class ExtensionsServer:
    def __init__(self) -> None:
        self._enabled: Optional[bool] = None
        self._block_list: Optional[list[str]] = None

    @property
    def enabled(self) -> Optional[bool]:
        """Indicates whether the extensions server is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: Optional[bool]) -> None:
        self._enabled = value

    @property
    def block_list(self) -> Optional[list[str]]:
        """List of blocked extensions."""
        return self._block_list

    @block_list.setter
    def block_list(self, value: Optional[list[str]]) -> None:
        self._block_list = value

    @classmethod
    def from_response(cls: type[Self], response, ns) -> Self:
        xml = fromstring(response)
        obj = cls()
        element = xml.find(".//t:extensionsServerSettings", namespaces=ns)
        if element is None:
            raise ValueError("Missing extensionsServerSettings element in response")

        if (enabled_element := element.find("./t:extensionsGloballyEnabled", namespaces=ns)) is not None:
            obj.enabled = string_to_bool(enabled_element.text)
        obj.block_list = [e.text for e in element.findall("./t:blockList", namespaces=ns)]

        return obj


@overload
def string_to_bool(s: str) -> bool: ...


@overload
def string_to_bool(s: None) -> None: ...


def string_to_bool(s):
    return s.lower() == "true" if s is not None else None
