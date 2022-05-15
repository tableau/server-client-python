from functools import singledispatch
from typing import TypeVar, Any
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
    result: T = text[:position] + replacement + text[position + len(replacement):]
    return result


# usage: _redact_typeful("<xml workbook password= cooliothesecond>", "password", "redacted",
#                           get_element=get_char_from_str)
# -> "<xml workbook password =***************">
def _redact_any_type(content: T, target: T, replacement: Any, get_element: Any) -> T:
    search_start: int = 0
    while search_start >= 0:
        try:
            replacement_begin: int = content.index(target, search_start) + 10
            i: int = replacement_begin
            # replace until we hit a space or quote or xml end-bracket
            # this *could* mean it stops partway into a password, if that character is present
            # so do a minimum of 8 characters
            next_char = None
            n_replaced = 0
            while i < len(content) and \
                    (n_replaced < 8 or
                     not (next_char == " " or next_char == '"' or next_char == ">")):
                next_char = get_element(content, i)
                content = content[:i] + replacement + content[i + 1:]
                i = i + 1
                n_replaced = n_replaced + 1
            search_start = i
        except ValueError:  # thrown when we don't find any more uses of target string
            search_start = -1
    return content


@singledispatch
def redact(content):
    # this will only be called if it didn't get directed to the str or bytes overloads
    raise TypeError("Redaction only works on str or bytes")


def get_char_from_str(content, i):
    return content[i]


@redact.register
def _(arg: str) -> str:
    return _redact_any_type(arg, target="password", replacement="*", get_element=get_char_from_str)


def get_char_from_bytes(element_list, i):
    return chr(element_list[i])


@redact.register  # type: ignore[no-redef]
def _(arg: bytes) -> bytes:
    return _redact_any_type(bytearray(arg), b"password", b"*", get_char_from_bytes)
