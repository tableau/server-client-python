import logging

from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.endpoint.exceptions import MissingRequiredFieldError
from tableauserverclient.server import RequestFactory
from tableauserverclient.models import GroupItem, UserItem, PaginationItem, JobItem
from tableauserverclient.server.pager import Pager

from tableauserverclient.helpers.logging import logger

from typing import Optional, TYPE_CHECKING, Union
from collections.abc import Iterable

from tableauserverclient.server.query import QuerySet

if TYPE_CHECKING:
    from tableauserverclient.server.request_options import RequestOptions


class Groups(QuerysetEndpoint[GroupItem]):
    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/groups"

    @api(version="2.0")
    def get(self, req_options: Optional["RequestOptions"] = None) -> tuple[list[GroupItem], PaginationItem]:
        """Gets all groups"""
        logger.info("Querying all groups on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_group_items = GroupItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_group_items, pagination_item

    @api(version="2.0")
    def populate_users(self, group_item: GroupItem, req_options: Optional["RequestOptions"] = None) -> None:
        """Gets all users in a given group"""
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
        self, group_item: GroupItem, req_options: Optional["RequestOptions"] = None
    ) -> tuple[list[UserItem], PaginationItem]:
        url = f"{self.baseurl}/{group_item.id}/users"
        server_response = self.get_request(url, req_options)
        user_item = UserItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        logger.info(f"Populated users for group (ID: {group_item.id})")
        return user_item, pagination_item

    @api(version="2.0")
    def delete(self, group_id: str) -> None:
        """Deletes 1 group by id"""
        if not group_id:
            error = "Group ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{group_id}"
        self.delete_request(url)
        logger.info(f"Deleted single group (ID: {group_id})")

    @api(version="2.0")
    def update(self, group_item: GroupItem, as_job: bool = False) -> Union[GroupItem, JobItem]:
        url = f"{self.baseurl}/{group_item.id}"

        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if as_job and (group_item.domain_name is None or group_item.domain_name == "local"):
            error = "Local groups cannot be updated asynchronously."
            raise ValueError(error)
        elif as_job:
            url = "?".join([url, "asJob=True"])

        update_req = RequestFactory.Group.update_req(group_item)
        server_response = self.put_request(url, update_req)
        logger.info(f"Updated group item (ID: {group_item.id})")
        if as_job:
            return JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        else:
            return GroupItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="2.0")
    def create(self, group_item: GroupItem) -> GroupItem:
        """Create a 'local' Tableau group"""
        url = self.baseurl
        create_req = RequestFactory.Group.create_local_req(group_item)
        server_response = self.post_request(url, create_req)
        return GroupItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="2.0")
    def create_AD_group(self, group_item: GroupItem, asJob: bool = False) -> Union[GroupItem, JobItem]:
        """Create a group based on Active Directory"""
        asJobparameter = "?asJob=true" if asJob else ""
        url = self.baseurl + asJobparameter
        create_req = RequestFactory.Group.create_ad_req(group_item)
        server_response = self.post_request(url, create_req)
        if asJob:
            return JobItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        else:
            return GroupItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="2.0")
    def remove_user(self, group_item: GroupItem, user_id: str) -> None:
        """Removes 1 user from 1 group"""
        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{group_item.id}/users/{user_id}"
        self.delete_request(url)
        logger.info(f"Removed user (id: {user_id}) from group (ID: {group_item.id})")

    @api(version="3.21")
    def remove_users(self, group_item: GroupItem, users: Iterable[Union[str, UserItem]]) -> None:
        """Removes multiple users from 1 group"""
        group_id = group_item.id if hasattr(group_item, "id") else group_item
        if not isinstance(group_id, str):
            raise ValueError(f"Invalid group provided: {group_item}")

        url = f"{self.baseurl}/{group_id}/users/remove"
        add_req = RequestFactory.Group.remove_users_req(users)
        _ = self.put_request(url, add_req)
        logger.info(f"Removed users to group (ID: {group_item.id})")
        return None

    @api(version="2.0")
    def add_user(self, group_item: GroupItem, user_id: str) -> UserItem:
        """Adds 1 user to 1 group"""
        if not group_item.id:
            error = "Group item missing ID."
            raise MissingRequiredFieldError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{group_item.id}/users"
        add_req = RequestFactory.Group.add_user_req(user_id)
        server_response = self.post_request(url, add_req)
        user = UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()
        logger.info(f"Added user (id: {user_id}) to group (ID: {group_item.id})")
        return user

    @api(version="3.21")
    def add_users(self, group_item: GroupItem, users: Iterable[Union[str, UserItem]]) -> list[UserItem]:
        """Adds multiple users to 1 group"""
        group_id = group_item.id if hasattr(group_item, "id") else group_item
        if not isinstance(group_id, str):
            raise ValueError(f"Invalid group provided: {group_item}")

        url = f"{self.baseurl}/{group_id}/users"
        add_req = RequestFactory.Group.add_users_req(users)
        server_response = self.post_request(url, add_req)
        users = UserItem.from_response(server_response.content, self.parent_srv.namespace)
        logger.info(f"Added users to group (ID: {group_item.id})")
        return users

    def filter(self, *invalid, page_size: Optional[int] = None, **kwargs) -> QuerySet[GroupItem]:
        """
        Queries the Tableau Server for items using the specified filters. Page
        size can be specified to limit the number of items returned in a single
        request. If not specified, the default page size is 100. Page size can
        be an integer between 1 and 1000.

        No positional arguments are allowed. All filters must be specified as
        keyword arguments. If you use the equality operator, you can specify it
        through <field_name>=<value>. If you want to use a different operator,
        you can specify it through <field_name>__<operator>=<value>. Field
        names can either be in snake_case or camelCase.

        This endpoint supports the following fields and operators:


        domain_name=...
        domain_name__in=...
        domain_nickname=...
        domain_nickname__in=...
        is_external_user_enabled=...
        is_local=...
        luid=...
        luid__in=...
        minimum_site_role=...
        minimum_site_role__in=...
        name__cieq=...
        name=...
        name__in=...
        name__like=...
        user_count=...
        user_count__gt=...
        user_count__gte=...
        user_count__lt=...
        user_count__lte=...
        """

        return super().filter(*invalid, page_size=page_size, **kwargs)
