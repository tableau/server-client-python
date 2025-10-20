from typing import Optional, overload
from typing_extensions import Self

from defusedxml.ElementTree import fromstring

from tableauserverclient.models.property_decorators import property_is_boolean


class ExtensionsServer:
    def __init__(self) -> None:
        self._enabled: Optional[bool] = None
        self._block_list: Optional[list[str]] = None

    @property
    def enabled(self) -> Optional[bool]:
        """Indicates whether the extensions server is enabled."""
        return self._enabled

    @enabled.setter
    @property_is_boolean
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


class SafeExtension:
    def __init__(
        self, url: Optional[str] = None, full_data_allowed: Optional[bool] = None, prompt_needed: Optional[bool] = None
    ) -> None:
        self.url = url
        self._full_data_allowed = full_data_allowed
        self._prompt_needed = prompt_needed

    @property
    def full_data_allowed(self) -> Optional[bool]:
        return self._full_data_allowed

    @full_data_allowed.setter
    @property_is_boolean
    def full_data_allowed(self, value: Optional[bool]) -> None:
        self._full_data_allowed = value

    @property
    def prompt_needed(self) -> Optional[bool]:
        return self._prompt_needed

    @prompt_needed.setter
    @property_is_boolean
    def prompt_needed(self, value: Optional[bool]) -> None:
        self._prompt_needed = value


class ExtensionsSiteSettings:
    def __init__(self) -> None:
        self._enabled: Optional[bool] = None
        self._use_default_setting: Optional[bool] = None
        self.safe_list: Optional[list[SafeExtension]] = None

    @property
    def enabled(self) -> Optional[bool]:
        return self._enabled

    @enabled.setter
    @property_is_boolean
    def enabled(self, value: Optional[bool]) -> None:
        self._enabled = value

    @property
    def use_default_setting(self) -> Optional[bool]:
        return self._use_default_setting

    @use_default_setting.setter
    @property_is_boolean
    def use_default_setting(self, value: Optional[bool]) -> None:
        self._use_default_setting = value

    @classmethod
    def from_response(cls: type[Self], response, ns) -> Self:
        xml = fromstring(response)
        element = xml.find(".//t:extensionsSiteSettings", namespaces=ns)
        obj = cls()
        if element is None:
            raise ValueError("Missing extensionsSiteSettings element in response")

        if (enabled_element := element.find("./t:extensionsEnabled", namespaces=ns)) is not None:
            obj.enabled = string_to_bool(enabled_element.text)
        if (default_settings_element := element.find("./t:useDefaultSetting", namespaces=ns)) is not None:
            obj.use_default_setting = string_to_bool(default_settings_element.text)

        safe_list = []
        for safe_extension_element in element.findall("./t:safeList", namespaces=ns):
            url = safe_extension_element.find("./t:url", namespaces=ns)
            full_data_allowed = safe_extension_element.find("./t:fullDataAllowed", namespaces=ns)
            prompt_needed = safe_extension_element.find("./t:promptNeeded", namespaces=ns)

            safe_extension = SafeExtension(
                url=url.text if url is not None else None,
                full_data_allowed=string_to_bool(full_data_allowed.text) if full_data_allowed is not None else None,
                prompt_needed=string_to_bool(prompt_needed.text) if prompt_needed is not None else None,
            )
            safe_list.append(safe_extension)

        obj.safe_list = safe_list
        return obj


@overload
def string_to_bool(s: str) -> bool: ...


@overload
def string_to_bool(s: None) -> None: ...


def string_to_bool(s):
    return s.lower() == "true" if s is not None else None
