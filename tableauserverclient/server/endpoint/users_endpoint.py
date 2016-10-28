from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, UserItem, WorkbookItem, PaginationItem
import logging
import copy

logger = logging.getLogger('tableau.endpoint.users')


class Users(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/users".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Gets all users
    def get(self, req_options=None):
        logger.info('Querying all users on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        all_user_items = UserItem.from_response(server_response.content)
        return all_user_items, pagination_item

    # Gets 1 user by id
    def get_by_id(self, user_id):
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        logger.info('Querying single user (ID: {0})'.format(user_id))
        url = "{0}/{1}".format(self.baseurl, user_id)
        server_response = self.get_request(url)
        return UserItem.from_response(server_response.content).pop()

    # Update user
    def update(self, user_item, password=None):
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, user_item.id)
        update_req = RequestFactory.User.update_req(user_item, password)
        server_response = self.put_request(url, update_req)
        logger.info('Updated user item (ID: {0})'.format(user_item.id))
        updated_item = copy.copy(user_item)
        return updated_item._parse_common_tags(server_response.content)

    # Delete 1 user by id
    def remove(self, user_id):
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, user_id)
        self.delete_request(url)
        logger.info('Removed single user (ID: {0})'.format(user_id))

    # Add new user to site
    def add(self, user_item):
        url = self.baseurl
        add_req = RequestFactory.User.add_req(user_item)
        server_response = self.post_request(url, add_req)
        new_user = UserItem.from_response(server_response.content).pop()
        logger.info('Added new user (ID: {0})'.format(user_item.id))
        return new_user

    # Get workbooks for user
    def populate_workbooks(self, user_item, req_options=None):
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/workbooks".format(self.baseurl, user_item.id)
        server_response = self.get_request(url, req_options)
        logger.info('Populated workbooks for user (ID: {0})'.format(user_item.id))
        user_item._set_workbooks(WorkbookItem.from_response(server_response.content))
        pagination_item = PaginationItem.from_response(server_response.content)
        return pagination_item

    def populate_favorites(self, user_item):
        raise NotImplementedError('REST API currently does not support the ability to query favorites')
