import datetime
import xml.etree.ElementTree as ET

from defusedxml.ElementTree import fromstring

from tableauserverclient.datetime_helpers import parse_datetime


class RecycleBinItem:
    """
    An item of content (workbook, data source, flow or project) that has been
    deleted and is held in the site's recycle bin.

    Parameters
    ----------
    id_ : str | None
        The identifier of the deleted content.

    name : str | None
        The name of the deleted content.

    content_type : str | None
        The type of the deleted content, as reported by the server: one of
        "workbook", "datasource", "flow" or "project".

    created_at : datetime.datetime | None
        When the content was originally created.

    updated_at : datetime.datetime | None
        When the content was last updated before it was deleted.

    original_path : str | None
        The project path the content was in before it was deleted.

    is_read_only : bool | None
        Whether the content is read only.

    owner_id : str | None
        The identifier of the user who owned the content.

    deleter_id : str | None
        The identifier of the user who deleted the content.
    """

    tag_name: str = "contentItem"

    def __init__(
        self,
        id_: str | None = None,
        name: str | None = None,
        content_type: str | None = None,
        created_at: datetime.datetime | None = None,
        updated_at: datetime.datetime | None = None,
        original_path: str | None = None,
        is_read_only: bool | None = None,
        owner_id: str | None = None,
        deleter_id: str | None = None,
    ) -> None:
        self._id = id_
        self.name = name
        self.content_type = content_type
        self.created_at = created_at
        self.updated_at = updated_at
        self.original_path = original_path
        self.is_read_only = is_read_only
        self.owner_id = owner_id
        self.deleter_id = deleter_id

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__} id={self._id} name={self.name} "
            f"content_type={self.content_type} original_path={self.original_path}>"
        )

    @property
    def id(self) -> str | None:
        return self._id

    @classmethod
    def from_response(cls, resp: bytes, ns: dict[str, str]) -> list["RecycleBinItem"]:
        parsed_response = fromstring(resp)
        return [cls.from_xml(xml, ns) for xml in parsed_response.findall(".//t:contentItem", namespaces=ns)]

    @classmethod
    def from_xml(cls, xml: ET.Element, ns: dict[str, str]) -> "RecycleBinItem":
        is_read_only = xml.get("isReadOnly")
        owner = xml.find("t:owner", namespaces=ns)
        deleter = xml.find("t:deleter", namespaces=ns)
        return cls(
            id_=xml.get("id"),
            name=xml.get("name"),
            content_type=xml.get("contentType"),
            created_at=parse_datetime(xml.get("createdAt")),
            updated_at=parse_datetime(xml.get("updatedAt")),
            original_path=xml.get("originalPath"),
            is_read_only=None if is_read_only is None else is_read_only.lower() == "true",
            owner_id=owner.get("id") if owner is not None else None,
            deleter_id=deleter.get("id") if deleter is not None else None,
        )
