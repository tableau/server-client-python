from defusedxml.ElementTree import fromstring, tostring
from functools import singledispatch
from typing import TypeVar, cast, overload

# the redact method can handle either strings or bytes, but it can't mix them.
# Generic type so we can write the actual logic once, then use singledispatch to
# create the replacement text with the correct type
T = TypeVar("T", str, bytes)

_REDACTED = "********"

# Elements that carry sign-in or connection credentials. Only the attributes named here are kept on them;
# any other attribute, including ones the server or library adds later, is replaced.
_CREDENTIAL_ELEMENTS = {"credentials", "connectionCredentials"}
_SAFE_CREDENTIAL_ATTRIBUTES = {"name", "personalAccessTokenName", "isUat", "embed", "oAuth", "id"}

# Outside credential elements, attributes and elements whose names contain one of these are replaced.
_SENSITIVE_NAME_PARTS = ("password", "secret", "token", "jwt", "authorization")


def _local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1]


def _is_sensitive(name: str) -> bool:
    lowered = name.lower()
    return any(part in lowered for part in _SENSITIVE_NAME_PARTS)


def _redact_any_type(xml: T, replacement: T, encoding=None) -> T:
    try:
        root = fromstring(xml)
    except Exception:
        # Not parseable (truncated, multipart, not xml): we can't tell which parts are safe, so log none of it.
        return replacement
    for element in root.iter():
        tag = _local_name(element.tag)
        is_credential_element = tag in _CREDENTIAL_ELEMENTS
        for attribute in element.attrib:
            name = _local_name(attribute)
            if is_credential_element:
                if name not in _SAFE_CREDENTIAL_ATTRIBUTES:
                    element.attrib[attribute] = _REDACTED
            elif _is_sensitive(name):
                element.attrib[attribute] = _REDACTED
        if element.text and _is_sensitive(tag):
            element.text = _REDACTED
    # tostring returns bytes unless an encoding value is passed; cast since
    # the callers pass encoding="unicode" for str and None for bytes
    return cast(T, tostring(root, encoding=encoding))


@singledispatch
def redact_xml(content):
    # this will only be called if it didn't get directed to the str or bytes overloads
    raise TypeError("Redaction only works on xml saved as str or bytes")


@redact_xml.register
def _(xml: str) -> str:
    out = _redact_any_type(xml, "[unparseable content redacted]", encoding="unicode")
    return out


@redact_xml.register  # type: ignore[no-redef]
def _(xml: bytes) -> bytes:
    return cast(bytes, _redact_any_type(xml, b"[unparseable content redacted]"))


@overload
def nullable_str_to_int(value: None) -> None: ...


@overload
def nullable_str_to_int(value: str) -> int: ...


def nullable_str_to_int(value):
    return int(value) if value is not None else None


@overload
def nullable_str_to_bool(value: None) -> None: ...


@overload
def nullable_str_to_bool(value: str) -> bool: ...


def nullable_str_to_bool(value):
    return str(value).lower() == "true" if value is not None else None
