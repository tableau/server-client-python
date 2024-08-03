import copy
from typing import Iterable, Optional, Protocol, Set, Union, TYPE_CHECKING, runtime_checkable
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


class _ResourceTagger(Endpoint):
    # Add new tags to resource
    def _add_tags(self, baseurl, resource_id, tag_set):
        url = "{0}/{1}/tags".format(baseurl, resource_id)
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
    def _delete_tag(self, baseurl, resource_id, tag_name):
        encoded_tag_name = urllib.parse.quote(tag_name)
        url = "{0}/{1}/tags/{2}".format(baseurl, resource_id, encoded_tag_name)

        try:
            self.delete_request(url)
        except ServerResponseError as e:
            if e.code == "404008":
                error = "Deleting tags from this resource type is only available with REST API version 2.6 and later."
                raise EndpointUnavailableError(error)
            raise  # Some other error

    # Remove and add tags to match the resource item's tag set
    def update_tags(self, baseurl, resource_item):
        if resource_item.tags != resource_item._initial_tags:
            add_set = resource_item.tags - resource_item._initial_tags
            remove_set = resource_item._initial_tags - resource_item.tags
            for tag in remove_set:
                self._delete_tag(baseurl, resource_item.id, tag)
            if add_set:
                resource_item.tags = self._add_tags(baseurl, resource_item.id, add_set)
            resource_item._initial_tags = copy.copy(resource_item.tags)
        logger.info("Updated tags to {0}".format(resource_item.tags))


@runtime_checkable
class Taggable(Protocol):
    _initial_tags: Set[str]
    id: Optional[str] = None
    tags: Set[str]


class TaggingMixin:
    def add_tags(self, item: Union[Taggable, str], tags: Union[Iterable[str], str]) -> Set[str]:
        item_id = getattr(item, "id", item)

        if not isinstance(item_id, str):
            raise ValueError("ID not found.")

        if isinstance(tags, str):
            tag_set = set([tags])
        else:
            tag_set = set(tags)

        url = f"{self.baseurl}/{item_id}/tags"  # type: ignore
        add_req = RequestFactory.Tag.add_req(tag_set)
        server_response = self.put_request(url, add_req)  # type: ignore
        return TagItem.from_response(server_response.content, self.parent_srv.namespace)  # type: ignore

    def delete_tags(self, item: Union[Taggable, str], tags: Union[Iterable[str], str]) -> None:
        item_id = getattr(item, "id", item)

        if not isinstance(item_id, str):
            raise ValueError("ID not found.")

        if isinstance(tags, str):
            tag_set = set([tags])
        else:
            tag_set = set(tags)

        for tag in tag_set:
            encoded_tag_name = urllib.parse.quote(tag)
            url = f"{self.baseurl}/{item_id}/tags/{encoded_tag_name}"  # type: ignore
            self.delete_request(url)  # type: ignore

    def update_tags(self, item: Taggable) -> None:
        if item.tags == item._initial_tags:
            return

        add_set = item.tags - item._initial_tags
        remove_set = item._initial_tags - item.tags
        self.delete_tags(item, remove_set)
        if add_set:
            item.tags = self.add_tags(item, add_set)
        item._initial_tags = copy.copy(item.tags)
        logger.info(f"Updated tags to {item.tags}")


content = Iterable[Union["ColumnItem", "DatabaseItem", "DatasourceItem", "FlowItem", "TableItem", "WorkbookItem"]]


class Tags(Endpoint):
    def __init__(self, parent_srv: "Server"):
        super().__init__(parent_srv)

    @property
    def baseurl(self):
        return f"{self.parent_srv.baseurl}/tags"

    @api(version="3.9")
    def batch_add(self, tags: Union[Iterable[str], str], content: content) -> Set[str]:
        if isinstance(tags, str):
            tag_set = set([tags])
        else:
            tag_set = set(tags)

        url = f"{self.baseurl}:batchCreate"
        batch_create_req = RequestFactory.Tag.batch_create(tag_set, content)
        server_response = self.put_request(url, batch_create_req)
        return TagItem.from_response(server_response.content, self.parent_srv.namespace)

    @api(version="3.9")
    def batch_delete(self, tags: Union[Iterable[str], str], content: content) -> Set[str]:
        if isinstance(tags, str):
            tag_set = set([tags])
        else:
            tag_set = set(tags)

        url = f"{self.baseurl}:batchDelete"
        # The batch delete XML is the same as the batch create XML.
        batch_delete_req = RequestFactory.Tag.batch_create(tag_set, content)
        server_response = self.put_request(url, batch_delete_req)
        return TagItem.from_response(server_response.content, self.parent_srv.namespace)
