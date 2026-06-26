import re

from defusedxml.ElementTree import fromstring

OLD_NAMESPACE = "http://tableausoftware.com/api"
NEW_NAMESPACE = "http://tableau.com/api"
NAMESPACE_RE = re.compile(r"\{(.*?)\}")


class UnknownNamespaceError(Exception):
    """Raised when an XML response contains an unrecognized Tableau API namespace."""


class Namespace:
    """Detects and stores the Tableau REST API XML namespace from server responses."""

    def __init__(self):
        self._namespace = {"t": NEW_NAMESPACE}
        self._detected = False

    def __call__(self):
        return self._namespace

    def detect(self, xml):
        """Detect the XML namespace from raw response bytes, updating the stored namespace on first call."""
        if self._detected:
            return

        if not xml.startswith(b"<?xml"):
            return  # Not an xml file, don't detect anything

        root = fromstring(xml)
        matches = NAMESPACE_RE.match(root.tag)
        if matches:
            detected_ns = matches.group(1)
            if detected_ns in (OLD_NAMESPACE, NEW_NAMESPACE):
                self._namespace = {"t": detected_ns}
                self._detected = True
            else:
                raise UnknownNamespaceError(detected_ns)
