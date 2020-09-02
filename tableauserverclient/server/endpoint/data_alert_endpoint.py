from .endpoint import api, Endpoint
from .exceptions import MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .default_permissions_endpoint import _DefaultPermissionsEndpoint

from .. import RequestFactory, DataAlertItem, PaginationItem, UserItem

import logging

logger = logging.getLogger('tableau.endpoint.dataAlerts')


class DataAlerts(Endpoint):
    def __init__(self, parent_srv):
        super(DataAlerts, self).__init__(parent_srv)

    @property
    def baseurl(self):
        return "{0}/sites/{1}/dataAlerts".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="3.2")
    def get(self, req_options=None):
        logger.info('Querying all dataAlerts on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_dataAlert_items = DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_dataAlert_items, pagination_item

    # Get 1 dataAlert
    @api(version="3.2")
    def get_by_id(self, dataAlert_id):
        if not dataAlert_id:
            error = "dataAlert ID undefined."
            raise ValueError(error)
        logger.info('Querying single dataAlert (ID: {0})'.format(dataAlert_id))
        url = "{0}/{1}".format(self.baseurl, dataAlert_id)
        server_response = self.get_request(url)
        return DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.2")
    def delete(self, dataAlert):
        dataAlert_id = getattr(dataAlert, 'id', dataAlert)
        if not dataAlert_id:
            error = "Dataalert ID undefined."
            raise ValueError(error)
        # DELETE /api/api-version/sites/site-id/dataAlerts/data-alert-id/users/user-id
        url = "{0}/{1}".format(self.baseurl, dataAlert_id)
        self.delete_request(url)
        logger.info('Deleted single dataAlert (ID: {0})'.format(dataAlert_id))

    @api(version="3.2")
    def delete_user_from_alert(self, dataAlert, user):
        dataAlert_id = getattr(dataAlert, 'id', dataAlert)
        user_id = getattr(user, 'id', user)
        if not dataAlert_id:
            error = "Dataalert ID undefined."
            raise ValueError(error)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        # DELETE /api/api-version/sites/site-id/dataAlerts/data-alert-id/users/user-id
        url = "{0}/{1}/users/{2}".format(self.baseurl, dataAlert_id, user_id)
        self.delete_request(url)
        logger.info('Deleted User (ID {0}) from dataAlert (ID: {1})'.format(user_id, dataAlert_id))

    @api(version="3.2")
    def add_user_to_alert(self, dataAlert_item, user):
        if not dataAlert_item.id:
            error = "Dataalert item missing ID."
            raise MissingRequiredFieldError(error)
        user_id = getattr(user, 'id', user)
        if not user_id:
            error = "User ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/users".format(self.baseurl, dataAlert_item.id)
        update_req = RequestFactory.DataAlert.add_user_to_alert(dataAlert_item, user_id)
        server_response = self.post_request(url, update_req)
        logger.info('Added user (ID {0}) to dataAlert item (ID: {1})'.format(user_id, dataAlert_item.id))
        user = UserItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return user

    @api(version="3.2")
    def update(self, dataAlert_item):
        if not dataAlert_item.id:
            error = "Dataalert item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, dataAlert_item.id)
        update_req = RequestFactory.DataAlert.update_req(dataAlert_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated dataAlert item (ID: {0})'.format(dataAlert_item.id))
        updated_dataAlert = DataAlertItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_dataAlert
