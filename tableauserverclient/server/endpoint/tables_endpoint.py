from .endpoint import api, Endpoint
from .exceptions import MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .default_permissions_endpoint import _DefaultPermissionsEndpoint

from .. import RequestFactory, TableItem, ColumnItem, PaginationItem, PermissionsRule, Permission

import logging

logger = logging.getLogger('tableau.endpoint.projects')


class Tables(Endpoint):
    def __init__(self, parent_srv):
        super(Tables, self).__init__(parent_srv)

        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)

    @property
    def baseurl(self):
        return "{0}/sites/{1}/tables".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="3.5")
    def get(self, req_options=None):
        logger.info('Querying all tables on site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_table_items = TableItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_table_items, pagination_item

    @api(version="3.5")
    def delete(self, table_id):
        if not table_id:
            error = "Database ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, table_id)
        self.delete_request(url)
        logger.info('Deleted single table (ID: {0})'.format(table_id))

    @api(version="3.5")
    def update(self, table_item):
        if not table_item.id:
            error = "table item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, table_item.id)
        update_req = RequestFactory.Table.update_req(table_item)
        server_response = self.put_request(url, update_req)
        logger.info('Updated table item (ID: {0})'.format(table_item.id))
        updated_table = TableItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_table

    # Get all columns of the table
    @api(version="3.5")
    def populate_columns(self, table_item):
        if not table_item.id:
            error = "Table item missing ID. table must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def column_fetcher():
            return self._get_columns_for_table(table_item)

        table_item._set_columns(column_fetcher)
        logger.info('Populated columns for table (ID: {0}'.format(table_item.id))

    def _get_columns_for_table(self, table_item):
        url = "{0}/{1}/columns".format(self.baseurl, table_item.id)
        server_response = self.get_request(url)
        columns = ColumnItem.from_response(server_response.content,
                                       self.parent_srv.namespace)
        return columns

    @api(version='3.5')
    def populate_permissions(self, item):
        self._permissions.populate(item)

    @api(version='3.5')
    def update_permission(self, item, rules):
        return self._permissions.update(item, rules)

    @api(version='3.5')
    def delete_permission(self, item, rules):
        return self._permissions.delete(item, rules)
