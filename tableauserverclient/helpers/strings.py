import requests

from defusedxml.ElementTree import fromstring, tostring
from functools import singledispatch
from typing import TypeVar


# the redact method can handle either strings or bytes, but it can't mix them.
# Generic type so we can write the actual logic once, then use singledispatch to
# create the replacement text with the correct type
T = TypeVar("T", str, bytes)


# TODO: ideally this would be in the logging config
def safe_to_log(server_response: requests.Response) -> str:
    """Checks if the server_response content is not xml (eg binary image or zip)
    and replaces it with a constant"""
    ALLOWED_CONTENT_TYPES = ("application/xml", "application/xml;charset=utf-8")
    if server_response.headers.get("Content-Type", None) not in ALLOWED_CONTENT_TYPES:
        return "[Truncated File Contents]"

    """ Check to determine if the response is a text response (xml or otherwise)
        so that we do not attempt to log bytes and other binary data. """
    if not server_response.content or not server_response.encoding:
        return ""
    # max length 1000
    loggable_response: str = server_response.content.decode(server_response.encoding)[:1000]
    redacted_response: str = redact_xml(loggable_response)
    return redacted_response


# usage: _redact_any_type("<xml workbook password= cooliothesecond>")
# -> b"<xml workbook password =***************">
def _redact_any_type(xml: T, sensitive_word: T, replacement: T, encoding=None) -> T:
    try:
        root = fromstring(xml)
        matches = root.findall(".//*[@password]")
        for item in matches:
            item.attrib["password"] = "********"
        matches = root.findall(".//password")
        for item in matches:
            item.text = "********"
        # tostring returns bytes unless an encoding value is passed
        return tostring(root, encoding=encoding)
    except Exception:
        # something about the xml handling failed. Just cut off the text at the first occurrence of "password"
        location = xml.find(sensitive_word)
        return xml[:location] + replacement


@singledispatch
def redact_xml(content):
    # this will only be called if it didn't get directed to the str or bytes overloads
    raise TypeError("Redaction only works on xml saved as str or bytes")


@redact_xml.register
def _(xml: str) -> str:
    out = _redact_any_type(xml, "password", "...[redacted]", encoding="unicode")
    return out


@redact_xml.register  # type: ignore[no-redef]
def _(xml: bytes) -> bytes:
    return _redact_any_type(bytearray(xml), b"password", b"..[redacted]")
