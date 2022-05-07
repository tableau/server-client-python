from functools import singledispatch


def safe_to_log(server_response) -> str:
    """Checks if the server_response content is not xml (eg binary image or zip)
        and replaces it with a constant """
    ALLOWED_CONTENT_TYPES = ("application/xml", "application/xml;charset=utf-8")
    if server_response.headers.get("Content-Type", None) not in ALLOWED_CONTENT_TYPES:
        return "[Truncated File Contents]"

    """ Check to determine if the response is a text response (xml or otherwise)
        so that we do not attempt to log bytes and other binary data. """
    if not server_response.content or not server_response.encoding:
        return None
    # max length 1000
    loggable_response = server_response.content.decode(server_response.encoding)[:1000]
    redacted_response = redact(loggable_response)
    return redacted_response


# string or bytes
def _replace(text, position: int, replacement):
    result = text[:position] + replacement + text[position + len(replacement):]
    return result


@singledispatch
def redact(content):
    # this will only be called if it didn't get directed to the str or bytes overloads
    raise TypeError("Redaction only works on str or bytes")


def _redact_typeful(content, target, replacement):
    search_start: int = 0
    while search_start >= 0:
        try:
            replacement_begin: int = content.index(target, search_start) + 8
            content = content.replace(target, replacement)
            content = _replace(content, replacement_begin, replacement)
            search_start = replacement_begin + 8 + 10
        except ValueError:
            search_start = -1
    return content


@redact.register(str)
def _(arg):
    print("str")
    return _redact_typeful(arg, target="password", replacement="redacted")


@redact.register(bytes)
def _(arg):
    print("bytes")
    return _redact_typeful(arg, target=b"password", replacement=b"redacted")
