import copy
import logging
import os
from typing import List, Optional, Tuple, Union

from .endpoint import QuerysetEndpoint, api
from .exceptions import MissingRequiredFieldError, ServerResponseError
from .. import RequestFactory, RequestOptions, UserItem, WorkbookItem, PaginationItem, GroupItem
from ..pager import Pager

# duplicate defined in workbooks_endpoint
FilePath = Union[str, os.PathLike]

logger = logging.getLogger("tableau.endpoint.users")


class Users(QuerysetEndpoint):
    @property
    def baseurl(self) -> str:
        return "{0}/sites/{1}/users".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Gets all users
    @api(version="2.0")
    def get(self, req_options: RequestOptions = None) -> Tuple[List[UserItem], PaginationItem]:
        logger.info("Querying all users on site")

        if req_options is None:
            req_options = RequestOptions()
        req_options._all_fields = True

        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_user_items = UserItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_user_items, pagination_item

    # Gets 1 user by id
    @api(version="2.0")
    def get_by_id(self, user_id: str) -> UserItem:
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        logger.info("Querying single user (ID: {0})".format(user_id))
        url = "{0}/{1}".format(self.baseurl, user_id)
        server_response = self.get_request(url)
        return UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()

    # Update user
    @api(version="2.0")
    def update(self, user_item: UserItem, password: str = None) -> UserItem:
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, user_item.id)
        update_req = RequestFactory.User.update_req(user_item, password)
        server_response = self.put_request(url, update_req)
        logger.info("Updated user item (ID: {0})".format(user_item.id))
        updated_item = copy.copy(user_item)
        return updated_item._parse_common_tags(server_response.content, self.parent_srv.namespace)

    # Delete 1 user by id
    @api(version="2.0")
    def remove(self, user_id: str, map_assets_to: Optional[str] = None) -> None:
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, user_id)
        if map_assets_to is not None:
            url += f"?mapAssetsTo={map_assets_to}"
        self.delete_request(url)
        logger.info("Removed single user (ID: {0})".format(user_id))

    # Add new user to site
    @api(version="2.0")
    def add(self, user_item: UserItem) -> UserItem:
        url = self.baseurl
        logger.info("Add user {}".format(user_item.name))
        add_req = RequestFactory.User.add_req(user_item)
        server_response = self.post_request(url, add_req)
        logger.info(server_response)
        new_user = UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()
        logger.info("Added new user (ID: {0})".format(new_user.id))
        return new_user

    # Add new users to site. This does not actually perform a bulk action, it's syntactic sugar
    @api(version="2.0")
    def add_all(self, users: List[UserItem]):
        created = []
        failed = []
        for user in users:
            try:
                result = self.add(user)
                created.append(result)
            except Exception as e:
                failed.append(user)
        return created, failed

    # helping the user by parsing a file they could have used to add users through the UI
    # line format: Username [required], password, display name, license, admin, publish
    @api(version="2.0")
    def create_from_file(self, filepath: str) -> Tuple[List[UserItem], List[Tuple[UserItem, ServerResponseError]]]:
        created = []
        failed = []
        if not filepath.find("csv"):
            raise ValueError("Only csv files are accepted")

        with open(filepath) as csv_file:
            csv_file.seek(0)  # set to start of file in case it has been read earlier
            line: str = csv_file.readline()
            while line and line != "":
                user: UserItem = UserItem.CSVImport.create_user_from_line(line)
                try:
                    print(user)
                    result = self.add(user)
                    created.append(result)
                except ServerResponseError as serverError:
                    print("failed")
                    failed.append((user, serverError))
                line = csv_file.readline()
        return created, failed

    # Get workbooks for user
    @api(version="2.0")
    def populate_workbooks(self, user_item: UserItem, req_options: RequestOptions = None) -> None:
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        def wb_pager():
            return Pager(lambda options: self._get_wbs_for_user(user_item, options), req_options)

        user_item._set_workbooks(wb_pager)

    def _get_wbs_for_user(
        self, user_item: UserItem, req_options: RequestOptions = None
    ) -> Tuple[List[WorkbookItem], PaginationItem]:
        url = "{0}/{1}/workbooks".format(self.baseurl, user_item.id)
        server_response = self.get_request(url, req_options)
        logger.info("Populated workbooks for user (ID: {0})".format(user_item.id))
        workbook_item = WorkbookItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        return workbook_item, pagination_item

    def populate_favorites(self, user_item: UserItem) -> None:
        self.parent_srv.favorites.get(user_item)

    # Get groups for user
    @api(version="3.7")
    def populate_groups(self, user_item: UserItem, req_options: RequestOptions = None) -> None:
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        def groups_for_user_pager():
            return Pager(
                lambda options: self._get_groups_for_user(user_item, options),
                req_options,
            )

        user_item._set_groups(groups_for_user_pager)

    def _get_groups_for_user(
        self, user_item: UserItem, req_options: RequestOptions = None
    ) -> Tuple[List[GroupItem], PaginationItem]:
        url = "{0}/{1}/groups".format(self.baseurl, user_item.id)
        server_response = self.get_request(url, req_options)
        logger.info("Populated groups for user (ID: {0})".format(user_item.id))
        group_item = GroupItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        return group_item, pagination_item
