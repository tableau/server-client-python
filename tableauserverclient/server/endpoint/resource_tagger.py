import abc
import copy
from typing import Generic, Protocol, TypeVar, TYPE_CHECKING
from collections.abc import Iterable
import urllib.parse

from tableauserverclient.server.endpoint.endpoint import Endpoint, api
from tableauserverclient.server.endpoint.exceptions import ServerResponseError
from tableauserverclient.server.exceptions import EndpointUnavailableError
from tableauserverclient.server import RequestFactory
from tableauserverclient.models import TagItem

from tableauserverclient.helpers.logging import logger

if TYPE_CHECKING:
    from tableauserverclient.models.column_item import ColumnItem
    from tableauserverclient.models.database_item import DatabaseItem
    from tableauserverclient.models.datasource_item import DatasourceItem
    from tableauserverclient.models.flow_item import FlowItem
    from tableauserverclient.models.table_item import TableItem
    from tableauserverclient.models.workbook_item import WorkbookItem
    from tableauserverclient.server.server import Server


class _TaggableWithInitial(Protocol):
    """Private structural protocol for items managed by _ResourceTagger.

    Extends the public TaggableItem interface with the ``_initial_tags``
    implementation detail used internally to track server-side tag state.

    ``id`` is declared as a read-only ``@property`` so that concrete item
    classes (``WorkbookItem``, ``DatasourceItem``, ``FlowItem``, etc.) that
    expose ``id`` as an ``@property`` satisfy the protocol under mypy's
    Protocol variance rules for data attributes.  ``tags`` and
    ``_initial_tags`` remain writable attributes because the tagger mutates
    them.
    """

    @property
    def id(self) -> str | None: ...

    tags: set[str]
    _initial_tags: set[str]


class _ResourceTagger(Endpoint):
    # Add new tags to resource
    def _add_tags(self, baseurl: str, resource_id: str | None, tag_set: set[str]) -> set[str]:
        url = f"{baseurl}/{resource_id}/tags"
        add_req = RequestFactory.Tag.add_req(tag_set)

        try:
            server_response = self.put_request(url, add_req)
            return TagItem.from_response(server_response.content, self.parent_srv.namespace)
        except ServerResponseError as e:
            if e.code == "404008":
                error = "Adding tags to this resource type is only available with REST API version 2.6 and later."
                raise EndpointUnavailableError(error)
            raise  # Some other error

    # Delete a resource's tag by name
    def _delete_tag(self, baseurl: str, resource_id: str | None, tag_name: str) -> None:
        encoded_tag_name = urllib.parse.quote(tag_name, safe="")
        url = f"{baseurl}/{resource_id}/tags/{encoded_tag_name}"

        try:
            self.delete_request(url)
        except ServerResponseError as e:
            if e.code == "404008":
                error = "Deleting tags from this resource type is only available with REST API version 2.6 and later."
                raise EndpointUnavailableError(error)
            raise  # Some other error

    # Remove and add tags to match the resource item's tag set
    def update_tags(self, baseurl: str, resource_item: _TaggableWithInitial) -> None:
        if resource_item.tags != resource_item._initial_tags:
            add_set = resource_item.tags - resource_item._initial_tags
            remove_set = resource_item._initial_tags - resource_item.tags
            for tag in remove_set:
                self._delete_tag(baseurl, resource_item.id, tag)
            if add_set:
                resource_item.tags = self._add_tags(baseurl, resource_item.id, add_set)
            resource_item._initial_tags = copy.copy(resource_item.tags)
        logger.info(f"Updated tags to {resource_item.tags}")


class Response(Protocol):
    content: bytes


T = TypeVar("T")


class TaggingMixin(abc.ABC, Generic[T]):
    parent_srv: "Server"

    @property
    @abc.abstractmethod
    def baseurl(self) -> str:
        pass

    @abc.abstractmethod
    def put_request(self, url, request) -> Response:
        pass

    @abc.abstractmethod
    def delete_request(self, url) -> None:
        pass

    def add_tags(self, item: T | str, tags: Iterable[str] | str) -> set[str]:
        item_id = getattr(item, "id", item)

        if not isinstance(item_id, str):
            raise ValueError("ID not found.")

        if isinstance(tags, str):
            tag_set = {tags}
        else:
            tag_set = set(tags)

        url = f"{self.baseurl}/{item_id}/tags"
        add_req = RequestFactory.Tag.add_req(tag_set)
        server_response = self.put_request(url, add_req)
        return TagItem.from_response(server_response.content, self.parent_srv.namespace)

    def delete_tags(self, item: T | str, tags: Iterable[str] | str) -> None:
        item_id = getattr(item, "id", item)

        if not isinstance(item_id, str):
            raise ValueError("ID not found.")

        if isinstance(tags, str):
            tag_set = {tags}
        else:
            tag_set = set(tags)

        for tag in tag_set:
            encoded_tag_name = urllib.parse.quote(tag, safe="")
            url = f"{self.baseurl}/{item_id}/tags/{encoded_tag_name}"
            self.delete_request(url)

    def update_tags(self, item: T) -> None:
        if (initial_tags := getattr(item, "_initial_tags", None)) is None:
            raise ValueError(f"{item} does not have initial tags.")
        if (tags := getattr(item, "tags", None)) is None:
            raise ValueError(f"{item} does not have tags.")
        if tags == initial_tags:
            return

        add_set = tags - initial_tags
        remove_set = initial_tags - tags
        self.delete_tags(item, remove_set)
        if add_set:
            tags = self.add_tags(item, add_set)
            setattr(item, "tags", tags)

        setattr(item, "_initial_tags", copy.copy(tags))
        logger.info(f"Updated tags to {tags}")


content = Iterable["ColumnItem | DatabaseItem | DatasourceItem | FlowItem | TableItem | WorkbookItem"]


class Tags(Endpoint):
    def __init__(self, parent_srv: "Server"):
        super().__init__(parent_srv)

    @property
    def baseurl(self):
        return f"{self.parent_srv.baseurl}/tags"

    @api(version="3.9")
    def batch_add(self, tags: Iterable[str] | str, content: content) -> set[str]:
        if isinstance(tags, str):
            tag_set = {tags}
        else:
            tag_set = set(tags)

        url = f"{self.baseurl}:batchCreate"
        batch_create_req = RequestFactory.Tag.batch_create(tag_set, content)
        server_response = self.put_request(url, batch_create_req)
        return TagItem.from_response(server_response.content, self.parent_srv.namespace)

    @api(version="3.9")
    def batch_delete(self, tags: Iterable[str] | str, content: content) -> set[str]:
        if isinstance(tags, str):
            tag_set = {tags}
        else:
            tag_set = set(tags)

        url = f"{self.baseurl}:batchDelete"
        # The batch delete XML is the same as the batch create XML.
        batch_delete_req = RequestFactory.Tag.batch_create(tag_set, content)
        server_response = self.put_request(url, batch_delete_req)
        return TagItem.from_response(server_response.content, self.parent_srv.namespace)
