from .endpoint import QuerysetEndpoint, api
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, RequestOptions, UserItem, WorkbookItem, PaginationItem, GroupItem
from ..pager import Pager

import copy
import logging

logger = logging.getLogger('tableau.endpoint.users')


class Users(QuerysetEndpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/users".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Gets all users
    @api(version="2.0")
    def get(self, req_options=None):
        logger.info('Querying all users on site')

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
    def get_by_id(self, user_id):
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        logger.info('Querying single user (ID: {0})'.format(user_id))
        url = "{0}/{1}".format(self.baseurl, user_id)
        server_response = self.get_request(url)
        return UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()

    # Update user
    @api(version="2.0")
    def update(self, user_item, password=None):
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, user_item.id)
        update_req = RequestFactory.User.update_req(user_item, password)
        server_response = self.put_request(url, update_req)
        logger.info('Updated user item (ID: {0})'.format(user_item.id))
        updated_item = copy.copy(user_item)
        return updated_item._parse_common_tags(server_response.content, self.parent_srv.namespace)

    # Delete 1 user by id
    @api(version="2.0")
    def remove(self, user_id):
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, user_id)
        self.delete_request(url)
        logger.info('Removed single user (ID: {0})'.format(user_id))

    # Add new user to site
    @api(version="2.0")
    def add(self, user_item):
        url = self.baseurl
        add_req = RequestFactory.User.add_req(user_item)
        server_response = self.post_request(url, add_req)
        new_user = UserItem.from_response(server_response.content, self.parent_srv.namespace).pop()
        logger.info('Added new user (ID: {0})'.format(new_user.id))
        return new_user

    # Get workbooks for user
    @api(version="2.0")
    def populate_workbooks(self, user_item, req_options=None):
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        def wb_pager():
            return Pager(lambda options: self._get_wbs_for_user(user_item, options), req_options)

        user_item._set_workbooks(wb_pager)

    def _get_wbs_for_user(self, user_item, req_options=None):
        url = "{0}/{1}/workbooks".format(self.baseurl, user_item.id)
        server_response = self.get_request(url, req_options)
        logger.info('Populated workbooks for user (ID: {0})'.format(user_item.id))
        workbook_item = WorkbookItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        return workbook_item, pagination_item

    def populate_favorites(self, user_item):
        self.parent_srv.favorites.get(user_item)

    # Get groups for user
    @api(version="3.7")
    def populate_groups(self, user_item, req_options=None):
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        def groups_for_user_pager():
            return Pager(lambda options: self._get_groups_for_user(user_item, options), req_options)

        user_item._set_groups(groups_for_user_pager)

    def _get_groups_for_user(self, user_item, req_options=None):
        url = "{0}/{1}/groups".format(self.baseurl, user_item.id)
        server_response = self.get_request(url, req_options)
        logger.info('Populated groups for user (ID: {0})'.format(user_item.id))
        group_item = GroupItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        return group_item, pagination_item
