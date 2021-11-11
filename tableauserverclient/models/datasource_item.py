import copy
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING

from defusedxml.ElementTree import fromstring

from .exceptions import UnpopulatedPropertyError
from .property_decorators import (
    property_not_nullable,
    property_is_boolean,
    property_is_enum,
)
from .tag_item import TagItem
from ..datetime_helpers import parse_datetime

if TYPE_CHECKING:
    from .permissions_item import PermissionsRule
    from .connection_item import ConnectionItem
    from .revision_item import RevisionItem
    import datetime

from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .permissions_item import PermissionsRule
    from .connection_item import ConnectionItem
    from .revision_item import RevisionItem
    import datetime


class DatasourceItem(object):
    class AskDataEnablement:
        Enabled = "Enabled"
        Disabled = "Disabled"
        SiteDefault = "SiteDefault"

    def __init__(self, project_id: str, name: str = None) -> None:
        self._ask_data_enablement = None
        self._certified = None
        self._certification_note = None
        self._connections = None
        self._content_url: Optional[str] = None
        self._created_at = None
        self._datasource_type = None
        self._description = None
        self._encrypt_extracts = None
        self._has_extracts = None
        self._id: Optional[str] = None
        self._initial_tags: Set = set()
        self._project_name: Optional[str] = None
        self._revisions = None
        self._updated_at = None
        self._use_remote_query_agent = None
        self._webpage_url = None
        self.description = None
        self.name = name
        self.owner_id: Optional[str] = None
        self.project_id = project_id
        self.tags: Set[str] = set()

        self._permissions = None
        self._data_quality_warnings = None

        return None

    @property
    def ask_data_enablement(self) -> Optional["DatasourceItem.AskDataEnablement"]:
        return self._ask_data_enablement

    @ask_data_enablement.setter
    @property_is_enum(AskDataEnablement)
    def ask_data_enablement(self, value: Optional["DatasourceItem.AskDataEnablement"]):
        self._ask_data_enablement = value

    @property
    def connections(self) -> Optional[List["ConnectionItem"]]:
        if self._connections is None:
            error = "Datasource item must be populated with connections first."
            raise UnpopulatedPropertyError(error)
        return self._connections()

    @property
    def permissions(self) -> Optional[List["PermissionsRule"]]:
        if self._permissions is None:
            error = "Project item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._permissions()

    @property
    def content_url(self) -> Optional[str]:
        return self._content_url

    @property
    def created_at(self) -> Optional["datetime.datetime"]:
        return self._created_at

    @property
    def certified(self) -> Optional[bool]:
        return self._certified

    @certified.setter
    @property_not_nullable
    @property_is_boolean
    def certified(self, value: Optional[bool]):
        self._certified = value

    @property
    def certification_note(self) -> Optional[str]:
        return self._certification_note

    @certification_note.setter
    def certification_note(self, value: Optional[str]):
        self._certification_note = value

    @property
    def encrypt_extracts(self):
        return self._encrypt_extracts

    @encrypt_extracts.setter
    @property_is_boolean
    def encrypt_extracts(self, value: Optional[bool]):
        self._encrypt_extracts = value

    @property
    def dqws(self):
        if self._data_quality_warnings is None:
            error = "Project item must be populated with dqws first."
            raise UnpopulatedPropertyError(error)
        return self._data_quality_warnings()

    @property
    def has_extracts(self) -> Optional[bool]:
        return self._has_extracts

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def project_id(self) -> str:
        return self._project_id

    @project_id.setter
    @property_not_nullable
    def project_id(self, value: str):
        self._project_id = value

    @property
    def project_name(self) -> Optional[str]:
        return self._project_name

    @property
    def datasource_type(self) -> Optional[str]:
        return self._datasource_type

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: str):
        self._description = value

    @property
    def updated_at(self) -> Optional["datetime.datetime"]:
        return self._updated_at

    @property
    def use_remote_query_agent(self) -> Optional[bool]:
        return self._use_remote_query_agent

    @use_remote_query_agent.setter
    @property_is_boolean
    def use_remote_query_agent(self, value: bool):
        self._use_remote_query_agent = value

    @property
    def webpage_url(self) -> Optional[str]:
        return self._webpage_url

    @property
    def revisions(self) -> List["RevisionItem"]:
        if self._revisions is None:
            error = "Datasource item must be populated with revisions first."
            raise UnpopulatedPropertyError(error)
        return self._revisions()

    def _set_connections(self, connections):
        self._connections = connections

    def _set_permissions(self, permissions):
        self._permissions = permissions

    def _set_data_quality_warnings(self, dqws):
        self._data_quality_warnings = dqws

    def _set_revisions(self, revisions):
        self._revisions = revisions

    def _parse_common_elements(self, datasource_xml, ns):
        if not isinstance(datasource_xml, ET.Element):
            datasource_xml = fromstring(datasource_xml).find(".//t:datasource", namespaces=ns)
        if datasource_xml is not None:
            (
                ask_data_enablement,
                certified,
                certification_note,
                _,
                _,
                _,
                _,
                encrypt_extracts,
                has_extracts,
                _,
                _,
                owner_id,
                project_id,
                project_name,
                _,
                updated_at,
                use_remote_query_agent,
                webpage_url,
            ) = self._parse_element(datasource_xml, ns)
            self._set_values(
                ask_data_enablement,
                certified,
                certification_note,
                None,
                None,
                None,
                None,
                encrypt_extracts,
                has_extracts,
                None,
                None,
                owner_id,
                project_id,
                project_name,
                None,
                updated_at,
                use_remote_query_agent,
                webpage_url,
            )
        return self

    def _set_values(
        self,
        ask_data_enablement,
        certified,
        certification_note,
        content_url,
        created_at,
        datasource_type,
        description,
        encrypt_extracts,
        has_extracts,
        id_,
        name,
        owner_id,
        project_id,
        project_name,
        tags,
        updated_at,
        use_remote_query_agent,
        webpage_url,
    ):
        if ask_data_enablement is not None:
            self._ask_data_enablement = ask_data_enablement
        if certification_note:
            self.certification_note = certification_note
        self.certified = certified  # Always True/False, not conditional
        if content_url:
            self._content_url = content_url
        if created_at:
            self._created_at = created_at
        if datasource_type:
            self._datasource_type = datasource_type
        if description:
            self.description = description
        if encrypt_extracts is not None:
            self.encrypt_extracts = str(encrypt_extracts).lower() == "true"
        if has_extracts is not None:
            self._has_extracts = str(has_extracts).lower() == "true"
        if id_ is not None:
            self._id = id_
        if name:
            self.name = name
        if owner_id:
            self.owner_id = owner_id
        if project_id:
            self.project_id = project_id
        if project_name:
            self._project_name = project_name
        if tags:
            self.tags = tags
            self._initial_tags = copy.copy(tags)
        if updated_at:
            self._updated_at = updated_at
        if use_remote_query_agent is not None:
            self._use_remote_query_agent = str(use_remote_query_agent).lower() == "true"
        if webpage_url:
            self._webpage_url = webpage_url

    @classmethod
    def from_response(cls, resp: str, ns: Dict) -> List["DatasourceItem"]:
        all_datasource_items = list()
        parsed_response = fromstring(resp)
        all_datasource_xml = parsed_response.findall(".//t:datasource", namespaces=ns)

        for datasource_xml in all_datasource_xml:
            (
                ask_data_enablement,
                certified,
                certification_note,
                content_url,
                created_at,
                datasource_type,
                description,
                encrypt_extracts,
                has_extracts,
                id_,
                name,
                owner_id,
                project_id,
                project_name,
                tags,
                updated_at,
                use_remote_query_agent,
                webpage_url,
            ) = cls._parse_element(datasource_xml, ns)
            datasource_item = cls(project_id)
            datasource_item._set_values(
                ask_data_enablement,
                certified,
                certification_note,
                content_url,
                created_at,
                datasource_type,
                description,
                encrypt_extracts,
                has_extracts,
                id_,
                name,
                owner_id,
                None,
                project_name,
                tags,
                updated_at,
                use_remote_query_agent,
                webpage_url,
            )
            all_datasource_items.append(datasource_item)
        return all_datasource_items

    @staticmethod
    def _parse_element(datasource_xml: ET.Element, ns: Dict) -> Tuple:
        id_ = datasource_xml.get("id", None)
        name = datasource_xml.get("name", None)
        datasource_type = datasource_xml.get("type", None)
        description = datasource_xml.get("description", None)
        content_url = datasource_xml.get("contentUrl", None)
        created_at = parse_datetime(datasource_xml.get("createdAt", None))
        updated_at = parse_datetime(datasource_xml.get("updatedAt", None))
        certification_note = datasource_xml.get("certificationNote", None)
        certified = str(datasource_xml.get("isCertified", None)).lower() == "true"
        certification_note = datasource_xml.get("certificationNote", None)
        certified = str(datasource_xml.get("isCertified", None)).lower() == "true"
        content_url = datasource_xml.get("contentUrl", None)
        created_at = parse_datetime(datasource_xml.get("createdAt", None))
        datasource_type = datasource_xml.get("type", None)
        description = datasource_xml.get("description", None)
        encrypt_extracts = datasource_xml.get("encryptExtracts", None)
        has_extracts = datasource_xml.get("hasExtracts", None)
        id_ = datasource_xml.get("id", None)
        name = datasource_xml.get("name", None)
        updated_at = parse_datetime(datasource_xml.get("updatedAt", None))
        use_remote_query_agent = datasource_xml.get("useRemoteQueryAgent", None)
        webpage_url = datasource_xml.get("webpageUrl", None)

        tags = None
        tags_elem = datasource_xml.find(".//t:tags", namespaces=ns)
        if tags_elem is not None:
            tags = TagItem.from_xml_element(tags_elem, ns)

        project_id = None
        project_name = None
        project_elem = datasource_xml.find(".//t:project", namespaces=ns)
        if project_elem is not None:
            project_id = project_elem.get("id", None)
            project_name = project_elem.get("name", None)

        owner_id = None
        owner_elem = datasource_xml.find(".//t:owner", namespaces=ns)
        if owner_elem is not None:
            owner_id = owner_elem.get("id", None)

        ask_data_enablement = None
        ask_data_elem = datasource_xml.find(".//t:askData", namespaces=ns)
        if ask_data_elem is not None:
            ask_data_enablement = ask_data_elem.get("enablement", None)

        return (
            ask_data_enablement,
            certified,
            certification_note,
            content_url,
            created_at,
            datasource_type,
            description,
            encrypt_extracts,
            has_extracts,
            id_,
            name,
            owner_id,
            project_id,
            project_name,
            tags,
            updated_at,
            use_remote_query_agent,
            webpage_url,
        )
