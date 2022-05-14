from functools import singledispatch
from typing import TypeVar
import requests
import sys


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
    redacted_response: str = redact(loggable_response)
    return redacted_response


def _replace(text: T, position: int, replacement: T) -> T:
    result: T = text[:position] + replacement + text[position + len(replacement) :]
    return result


def _redact_typeful(content: T, target: T, replacement: T) -> T:
    search_start: int = 0
    while search_start >= 0:
        try:
            replacement_begin: int = content.index(target, search_start) + 8
            content = _replace(content, replacement_begin, replacement)
            search_start = replacement_begin + 8
        except ValueError:
            search_start = -1
    content = content.replace(target, replacement)
    return content


@singledispatch
def redact(content):
    # this will only be called if it didn't get directed to the str or bytes overloads
    raise TypeError("Redaction only works on str or bytes")


@redact.register
def _(arg: str) -> str:
    return _redact_typeful(arg, target="password", replacement="redacted")


@redact.register  # type: ignore[no-redef]
def _(arg: bytes) -> bytes:
    return _redact_typeful(arg, target=b"password", replacement=b"redacted")
