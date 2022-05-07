import copy
import uuid
import xml.etree.ElementTree as ET
from typing import Callable, Dict, List, Optional, Set, TYPE_CHECKING

from defusedxml.ElementTree import fromstring

from .exceptions import UnpopulatedPropertyError
from .permissions_item import PermissionsRule
from .property_decorators import (
    property_not_nullable,
    property_is_boolean,
    property_is_data_acceleration_config,
)
from .tag_item import TagItem
from .view_item import ViewItem
from ..datetime_helpers import parse_datetime


if TYPE_CHECKING:
    from .connection_item import ConnectionItem
    from .permissions_item import PermissionsRule
    import datetime
    from .revision_item import RevisionItem

from typing import Dict, List, Optional, Set, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .connection_item import ConnectionItem
    from .permissions_item import PermissionsRule
    import datetime
    from .revision_item import RevisionItem


class WorkbookItem(object):
    def __init__(self, project_id: str, name: str = None, show_tabs: bool = False) -> None:
        self._connections = None
        self._content_url = None
        self._webpage_url = None
        self._created_at = None
        self._id: Optional[str] = None
        self._initial_tags: set = set()
        self._pdf = None
        self._powerpoint = None
        self._preview_image = None
        self._project_name = None
        self._revisions = None
        self._size = None
        self._updated_at = None
        self._views = None
        self.name = name
        self._description = None
        self.owner_id: Optional[str] = None
        self.project_id = project_id
        self.show_tabs = show_tabs
        self.hidden_views: Optional[List[str]] = None
        self.tags: Set[str] = set()
        self.data_acceleration_config = {
            "acceleration_enabled": None,
            "accelerate_now": None,
            "last_updated_at": None,
            "acceleration_status": None,
        }
        self._permissions = None

        return None

    @property
    def connections(self) -> List["ConnectionItem"]:
        if self._connections is None:
            error = "Workbook item must be populated with connections first."
            raise UnpopulatedPropertyError(error)
        return self._connections()

    @property
    def permissions(self) -> List["PermissionsRule"]:
        if self._permissions is None:
            error = "Workbook item must be populated with permissions first."
            raise UnpopulatedPropertyError(error)
        return self._permissions()

    @property
    def content_url(self) -> Optional[str]:
        return self._content_url

    @property
    def webpage_url(self) -> Optional[str]:
        return self._webpage_url

    @property
    def created_at(self) -> Optional["datetime.datetime"]:
        return self._created_at

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def powerpoint(self) -> bytes:
        if self._powerpoint is None:
            error = "Workbook item must be populated with its powerpoint first."
            raise UnpopulatedPropertyError(error)
        return self._powerpoint()

    @property
    def pdf(self) -> bytes:
        if self._pdf is None:
            error = "Workbook item must be populated with its pdf first."
            raise UnpopulatedPropertyError(error)
        return self._pdf()

    @property
    def preview_image(self) -> bytes:
        if self._preview_image is None:
            error = "Workbook item must be populated with its preview image first."
            raise UnpopulatedPropertyError(error)
        return self._preview_image()

    @property
    def project_id(self) -> Optional[str]:
        return self._project_id

    @project_id.setter
    def project_id(self, value: str):
        self._project_id = value

    @property
    def project_name(self) -> Optional[str]:
        return self._project_name

    @property
    def show_tabs(self) -> bool:
        return self._show_tabs

    @show_tabs.setter
    @property_is_boolean
    def show_tabs(self, value: bool):
        self._show_tabs = value

    @property
    def size(self):
        return self._size

    @property
    def updated_at(self) -> Optional["datetime.datetime"]:
        return self._updated_at

    @property
    def views(self) -> List[ViewItem]:
        # Views can be set in an initial workbook response OR by a call
        # to Server. Without getting too fancy, I think we can rely on
        # returning a list from the response, until they call
        # populate_workbook, in which case we bind the fetcher and
        # return a callable.
        if self._views is None:
            error = "Workbook item must be populated with views first."
            raise UnpopulatedPropertyError(error)
        elif callable(self._views):
            # We've called `populate_views` on this model
            return self._views()
        else:
            # We had views included in a WorkbookItem response
            return self._views

    @property
    def data_acceleration_config(self):
        return self._data_acceleration_config

    @data_acceleration_config.setter
    @property_is_data_acceleration_config
    def data_acceleration_config(self, value):
        self._data_acceleration_config = value

    @property
    def revisions(self) -> List["RevisionItem"]:
        if self._revisions is None:
            error = "Workbook item must be populated with revisions first."
            raise UnpopulatedPropertyError(error)
        return self._revisions()

    def _set_connections(self, connections):
        self._connections = connections

    def _set_permissions(self, permissions):
        self._permissions = permissions

    def _set_views(self, views: Callable[[], List[ViewItem]]) -> None:
        self._views = views

    def _set_pdf(self, pdf: Callable[[], bytes]) -> None:
        self._pdf = pdf

    def _set_powerpoint(self, pptx: Callable[[], bytes]) -> None:
        self._powerpoint = pptx

    def _set_preview_image(self, preview_image: Callable[[], bytes]) -> None:
        self._preview_image = preview_image

    def _set_revisions(self, revisions):
        self._revisions = revisions

    def _parse_common_tags(self, workbook_xml, ns):
        if not isinstance(workbook_xml, ET.Element):
            workbook_xml = fromstring(workbook_xml).find(".//t:workbook", namespaces=ns)
        if workbook_xml is not None:
            (
                _,
                _,
                _,
                _,
                _,
                description,
                updated_at,
                _,
                show_tabs,
                project_id,
                project_name,
                owner_id,
                _,
                _,
                data_acceleration_config,
            ) = self._parse_element(workbook_xml, ns)

            self._set_values(
                None,
                None,
                None,
                None,
                None,
                description,
                updated_at,
                None,
                show_tabs,
                project_id,
                project_name,
                owner_id,
                None,
                None,
                data_acceleration_config,
            )

        return self

    def _set_values(
        self,
        id,
        name,
        content_url,
        webpage_url,
        created_at,
        description,
        updated_at,
        size,
        show_tabs,
        project_id,
        project_name,
        owner_id,
        tags,
        views,
        data_acceleration_config,
    ):
        if id is not None:
            self._id = id
        if name:
            self.name = name
        if content_url:
            self._content_url = content_url
        if webpage_url:
            self._webpage_url = webpage_url
        if created_at:
            self._created_at = created_at
        if description:
            self._description = description
        if updated_at:
            self._updated_at = updated_at
        if size:
            self._size = size
        if show_tabs:
            self._show_tabs = show_tabs
        if project_id:
            self.project_id = project_id
        if project_name:
            self._project_name = project_name
        if owner_id:
            self.owner_id = owner_id
        if tags:
            self.tags = tags
            self._initial_tags = copy.copy(tags)
        if views:
            self._views = views
        if data_acceleration_config is not None:
            self.data_acceleration_config = data_acceleration_config

    @classmethod
    def from_response(cls, resp: str, ns: Dict[str, str]) -> List["WorkbookItem"]:
        all_workbook_items = list()
        parsed_response = fromstring(resp)
        all_workbook_xml = parsed_response.findall(".//t:workbook", namespaces=ns)
        for workbook_xml in all_workbook_xml:
            (
                id,
                name,
                content_url,
                webpage_url,
                created_at,
                description,
                updated_at,
                size,
                show_tabs,
                project_id,
                project_name,
                owner_id,
                tags,
                views,
                data_acceleration_config,
            ) = cls._parse_element(workbook_xml, ns)

            # workaround for Personal Space workbooks which won't have a project
            if not project_id:
                project_id = uuid.uuid4()

            workbook_item = cls(project_id)
            workbook_item._set_values(
                id,
                name,
                content_url,
                webpage_url,
                created_at,
                description,
                updated_at,
                size,
                show_tabs,
                None,
                project_name,
                owner_id,
                tags,
                views,
                data_acceleration_config,
            )
            all_workbook_items.append(workbook_item)
        return all_workbook_items

    @staticmethod
    def _parse_element(workbook_xml, ns):
        id = workbook_xml.get("id", None)
        name = workbook_xml.get("name", None)
        content_url = workbook_xml.get("contentUrl", None)
        webpage_url = workbook_xml.get("webpageUrl", None)
        created_at = parse_datetime(workbook_xml.get("createdAt", None))
        description = workbook_xml.get("description", None)
        updated_at = parse_datetime(workbook_xml.get("updatedAt", None))

        size = workbook_xml.get("size", None)
        if size:
            size = int(size)

        show_tabs = string_to_bool(workbook_xml.get("showTabs", ""))

        project_id = None
        project_name = None
        project_tag = workbook_xml.find(".//t:project", namespaces=ns)
        if project_tag is not None:
            project_id = project_tag.get("id", None)
            project_name = project_tag.get("name", None)

        owner_id = None
        owner_tag = workbook_xml.find(".//t:owner", namespaces=ns)
        if owner_tag is not None:
            owner_id = owner_tag.get("id", None)

        tags = None
        tags_elem = workbook_xml.find(".//t:tags", namespaces=ns)
        if tags_elem is not None:
            all_tags = TagItem.from_xml_element(tags_elem, ns)
            tags = all_tags

        views = None
        views_elem = workbook_xml.find(".//t:views", namespaces=ns)
        if views_elem is not None:
            views = ViewItem.from_xml_element(views_elem, ns)

        data_acceleration_config = {
            "acceleration_enabled": None,
            "accelerate_now": None,
            "last_updated_at": None,
            "acceleration_status": None,
        }
        data_acceleration_elem = workbook_xml.find(".//t:dataAccelerationConfig", namespaces=ns)
        if data_acceleration_elem is not None:
            data_acceleration_config = parse_data_acceleration_config(data_acceleration_elem)

        return (
            id,
            name,
            content_url,
            webpage_url,
            created_at,
            description,
            updated_at,
            size,
            show_tabs,
            project_id,
            project_name,
            owner_id,
            tags,
            views,
            data_acceleration_config,
        )


def parse_data_acceleration_config(data_acceleration_elem):
    data_acceleration_config = dict()

    acceleration_enabled = data_acceleration_elem.get("accelerationEnabled", None)
    if acceleration_enabled is not None:
        acceleration_enabled = string_to_bool(acceleration_enabled)

    accelerate_now = data_acceleration_elem.get("accelerateNow", None)
    if accelerate_now is not None:
        accelerate_now = string_to_bool(accelerate_now)

    last_updated_at = data_acceleration_elem.get("lastUpdatedAt", None)
    if last_updated_at is not None:
        last_updated_at = parse_datetime(last_updated_at)

    acceleration_status = data_acceleration_elem.get("accelerationStatus", None)

    data_acceleration_config["acceleration_enabled"] = acceleration_enabled
    data_acceleration_config["accelerate_now"] = accelerate_now
    data_acceleration_config["last_updated_at"] = last_updated_at
    data_acceleration_config["acceleration_status"] = acceleration_status
    return data_acceleration_config


# Used to convert string represented boolean to a boolean type
def string_to_bool(s: str) -> bool:
    return s.lower() == "true"
