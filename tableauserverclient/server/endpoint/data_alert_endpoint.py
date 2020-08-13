from .endpoint import api, Endpoint
from .exceptions import MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .default_permissions_endpoint import _DefaultPermissionsEndpoint

from .. import RequestFactory, DataAlertItem, PaginationItem, UserItem

import logging

logger = logging.getLogger('tableau.endpoint.dataalerts')


class DataAlerts(Endpoint):
    def __init__(self, parent_srv):
        super(DataAlerts, self).__init__(parent_srv)

    @property
    def baseurl(self):
        return "{0}/sites/{1}/dataalerts".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="3.2")
    def get(self, req_options=None):
        logger.info('Querying all dataalerts on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_dataalert_items = DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_dataalert_items, pagination_item

    # Get 1 dataalert
    @api(version="3.2")
    def get_by_id(self, dataalert_id):
        if not dataalert_id:
            error = "dataalert ID undefined."
            raise ValueError(error)
        logger.info('Querying single dataalert (ID: {0})'.format(dataalert_id))
        url = "{0}/{1}".format(self.baseurl, dataalert_id)
        server_response = self.get_request(url)
        return DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.2")
    def delete(self, dataalert):
        dataalert_id = getattr(dataalert, 'id', dataalert)
        if not dataalert_id:
            error = "Dataalert ID undefined."
            raise ValueError(error)
        # DELETE /api/api-version/sites/site-id/dataAlerts/data-alert-id/users/user-id
        url = "{0}/{1}".format(self.baseurl, dataalert_id)
        self.delete_request(url)
        logger.info('Deleted single dataalert (ID: {0})'.format(dataalert_id))

    @api(version="3.2")
    def delete_user_from_alert(self, dataalert, user):
        dataalert_id = getattr(dataalert, 'id', dataalert)
        user_id = getattr(user, 'id', user)
        if not dataalert_id:
            error = "Dataalert ID undefined."
            raise ValueError(error)
        # DELETE /api/api-version/sites/site-id/dataAlerts/data-alert-id/users/user-id
        url = "{0}/{1}/users/{2}".format(self.baseurl, dataalert_id, user_id)
        self.delete_request(url)
        logger.info('Deleted single dataalert (ID: {0})'.format(dataalert_id))

    @api(version="3.2")
    def add_user_to_alert(self, dataalert_item, user):
        if not dataalert_item.id:
            error = "Dataalert item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}/users".format(self.baseurl, dataalert_item.id)
        update_req = RequestFactory.DataAlert.add_user_to_alert(dataalert_item, user)
        server_response = self.post_request(url, update_req)
        logger.info('Updated dataalert item (ID: {0})'.format(dataalert_item.id))
        user = UserItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return user

    @api(version="3.2")
    def update(self, dataalert_item):
        if not dataalert_item.id:
            error = "Dataalert item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, dataalert_item.id)
        update_req = RequestFactory.DataAlert.update_req(dataalert_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated dataalert item (ID: {0})'.format(dataalert_item.id))
        updated_dataalert = DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_dataalert
