from typing import List, Literal, Optional, Tuple, TYPE_CHECKING, Union

from tableauserverclient.helpers.logging import logger
from tableauserverclient.models.group_item import GroupItem
from tableauserverclient.models.groupset_item import GroupSetItem
from tableauserverclient.models.pagination_item import PaginationItem
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint
from tableauserverclient.server.request_options import RequestOptions
from tableauserverclient.server.request_factory import RequestFactory
from tableauserverclient.server.endpoint.endpoint import api

if TYPE_CHECKING:
    from tableauserverclient.server import Server


class GroupSets(QuerysetEndpoint[GroupSetItem]):
    def __init__(self, parent_srv: "Server") -> None:
        super().__init__(parent_srv)

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/groupsets"

    @api(version="3.22")
    def get(
        self,
        request_options: Optional[RequestOptions] = None,
        result_level: Optional[Literal["members", "local"]] = None,
    ) -> Tuple[List[GroupSetItem], PaginationItem]:
        logger.info("Querying all group sets on site")
        url = self.baseurl
        if result_level:
            url += f"?resultlevel={result_level}"
        server_response = self.get_request(url, request_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_group_set_items = GroupSetItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_group_set_items, pagination_item

    @api(version="3.22")
    def get_by_id(self, groupset_id: str) -> GroupSetItem:
        logger.info(f"Querying group set (ID: {groupset_id})")
        url = f"{self.baseurl}/{groupset_id}"
        server_response = self.get_request(url)
        all_group_set_items = GroupSetItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_group_set_items[0]

    @api(version="3.22")
    def create(self, groupset_item: GroupSetItem) -> GroupSetItem:
        logger.info(f"Creating group set (name: {groupset_item.name})")
        url = self.baseurl
        request = RequestFactory.GroupSet.create_request(groupset_item)
        server_response = self.post_request(url, request)
        created_groupset = GroupSetItem.from_response(server_response.content, self.parent_srv.namespace)
        return created_groupset[0]

    @api(version="3.22")
    def add_group(self, groupset_item: GroupSetItem, group: Union[GroupItem, str]) -> None:
        group_id = group.id if isinstance(group, GroupItem) else group
        logger.info(f"Adding group (ID: {group_id}) to group set (ID: {groupset_item.id})")
        url = f"{self.baseurl}/{groupset_item.id}/groups/{group_id}"
        _ = self.put_request(url)
        return None

    @api(version="3.22")
    def remove_group(self, groupset_item: GroupSetItem, group: Union[GroupItem, str]) -> None:
        group_id = group.id if isinstance(group, GroupItem) else group
        logger.info(f"Removing group (ID: {group_id}) from group set (ID: {groupset_item.id})")
        url = f"{self.baseurl}/{groupset_item.id}/groups/{group_id}"
        _ = self.delete_request(url)
        return None

    @api(version="3.22")
    def delete(self, groupset: Union[GroupSetItem, str]) -> None:
        groupset_id = groupset.id if isinstance(groupset, GroupSetItem) else groupset
        logger.info(f"Deleting group set (ID: {groupset_id})")
        url = f"{self.baseurl}/{groupset_id}"
        _ = self.delete_request(url)
        return None

    @api(version="3.22")
    def update(self, groupset: GroupSetItem) -> GroupSetItem:
        logger.info(f"Updating group set (ID: {groupset.id})")
        url = f"{self.baseurl}/{groupset.id}"
        request = RequestFactory.GroupSet.update_request(groupset)
        server_response = self.put_request(url, request)
        updated_groupset = GroupSetItem.from_response(server_response.content, self.parent_srv.namespace)
        return updated_groupset[0]
