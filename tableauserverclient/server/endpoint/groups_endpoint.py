import logging

from .endpoint import QuerysetEndpoint, api
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, GroupItem, UserItem, PaginationItem, JobItem
from ..pager import Pager

logger = logging.getLogger("tableau.endpoint.groups")

from typing import List, Optional, TYPE_CHECKING, Tuple, Union

if TYPE_CHECKING:
    from ..request_options import RequestOptions


class Groups(QuerysetEndpoint):
    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/groups".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Gets all groups
    @api(version="2.0")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[GroupItem], PaginationItem]:
        logger.info("Querying all groups on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_group_items = GroupItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_group_items, pagination_item

    # Gets all users in a given group
    @api(version="2.0")
    def populate_users(self, group_item, req_options: Optional["RequestOptions"] = None) -> None:
        if not group_item.id:
            error = "Group item missing ID. Group must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        # Define an inner function that we bind to the model_item's `.user` property.

        def user_pager():
            return Pager(
                lambda options: self._get_users_for_group(group_item, options),
                req_options,
            )

        group_item._set_users(user_pager)

    def _get_users_for_group(
        self, group_item, req_options: Optional["RequestOptions"] = None
    ) -> Tuple[List[UserItem], PaginationItem]:
        url = "{0}/{1}/users".format(self.baseurl, group_item.id)
        server_response = self.get_request(url, req_options)
        user_item = UserItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        logger.info("Populated users for group (ID: {0})".format(group_item.id))
        return user_item, pagination_item

    # Deletes 1 group by id
    @api(version="2.0")
    def delete(self, group_id: str) -> None:
        if not group_id:
            error = "Group ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, group_id)
        self.delete_request(url)
        logger.info("Deleted single group (ID: {0})".format(group_id))

    @api(version="2.0")
    def update(
        self, group_item: GroupItem, default_site_role: Optional[str] = None, as_job: bool = False
    ) -> Union[GroupItem, JobItem]:
        # (1/8/2021): Deprecated starting v0.15
        if default_site_role is not None:
            import warnings

            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(
                'Groups.update(...default_site_role=""...) is deprecated, '
                "please set the minimum_site_role field of GroupItem",
                DeprecationWarning,
            )
            group_item.minimum_site_role = default_site_role

        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if as_job and (group_item.domain_name is None or group_item.domain_name == "local"):
            error = "Local groups cannot be updated asynchronously."
            raise ValueError(error)

        url = "{0}/{1}".format(self.baseurl, group_item.id)
        update_req = RequestFactory.Group.update_req(group_item, None)
        server_response = self.put_request(url, update_req)
        logger.info("Updated group item (ID: {0})".format(group_item.id))
        if as_job:
            return JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        else:
            return GroupItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Create a 'local' Tableau group
    @api(version="2.0")
    def create(self, group_item: GroupItem) -> GroupItem:
        url = self.baseurl
        create_req = RequestFactory.Group.create_local_req(group_item)
        server_response = self.post_request(url, create_req)
        return GroupItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Create a group based on Active Directory
    @api(version="2.0")
    def create_AD_group(self, group_item: GroupItem, asJob: bool = False) -> Union[GroupItem, JobItem]:
        asJobparameter = "?asJob=true" if asJob else ""
        url = self.baseurl + asJobparameter
        create_req = RequestFactory.Group.create_ad_req(group_item)
        server_response = self.post_request(url, create_req)
        if asJob:
            return JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        else:
            return GroupItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Removes 1 user from 1 group
    @api(version="2.0")
    def remove_user(self, group_item: GroupItem, user_id: str) -> None:
        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/users/{2}".format(self.baseurl, group_item.id, user_id)
        self.delete_request(url)
        logger.info("Removed user (id: {0}) from group (ID: {1})".format(user_id, group_item.id))

    # Adds 1 user to 1 group
    @api(version="2.0")
    def add_user(self, group_item: GroupItem, user_id: str) -> UserItem:
        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/users".format(self.baseurl, group_item.id)
        add_req = RequestFactory.Group.add_user_req(user_id)
        server_response = self.post_request(url, add_req)
        user = UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()
        logger.info("Added user (id: {0}) to group (ID: {1})".format(user_id, group_item.id))
        return user
