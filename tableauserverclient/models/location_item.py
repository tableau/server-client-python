import xml.etree.ElementTree as ET


class LocationItem:
    """
    Details of where an item is located, such as a personal space or project.

    Attributes
    ----------
    id : str | None
        The ID of the location.

    type : str | None
        The type of location, such as PersonalSpace or Project.

    name : str | None
        The name of the location.
    """

    class Type:
        PersonalSpace = "PersonalSpace"
        Project = "Project"

    def __init__(self):
        self._id: str | None = None
        self._type: str | None = None
        self._name: str | None = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__!r})"

    @property
    def id(self) -> str | None:
        return self._id

    @property
    def type(self) -> str | None:
        return self._type

    @property
    def name(self) -> str | None:
        return self._name

    @classmethod
    def from_xml(cls, xml: ET.Element, ns: dict | None = None) -> "LocationItem":
        if ns is None:
            ns = {}
        location = cls()
        location._id = xml.get("id", None)
        location._type = xml.get("type", None)
        location._name = xml.get("name", None)
        return location
