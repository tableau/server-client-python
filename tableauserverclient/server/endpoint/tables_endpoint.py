import logging

from .dqw_endpoint import _DataQualityWarningEndpoint
from .endpoint import api, Endpoint
from .exceptions import MissingRequiredFieldError
from .permissions_endpoint import _PermissionsEndpoint
from .. import RequestFactory, TableItem, ColumnItem, PaginationItem
from ..pager import Pager

logger = logging.getLogger("tableau.endpoint.tables")


class Tables(Endpoint):
    def __init__(self, parent_srv):
        super(Tables, self).__init__(parent_srv)

        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._data_quality_warnings = _DataQualityWarningEndpoint(self.parent_srv, "table")

    @property
    def baseurl(self):
        return "{0}/sites/{1}/tables".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @api(version="3.5")
    def get(self, req_options=None):
        logger.info("Querying all tables on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_table_items = TableItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_table_items, pagination_item

    # Get 1 table
    @api(version="3.5")
    def get_by_id(self, table_id):
        if not table_id:
            error = "table ID undefined."
            raise ValueError(error)
        logger.info("Querying single table (ID: {0})".format(table_id))
        url = "{0}/{1}".format(self.baseurl, table_id)
        server_response = self.get_request(url)
        return TableItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.5")
    def delete(self, table_id):
        if not table_id:
            error = "Database ID undefined."
            raise ValueError(error)
        url = "{0}/{1}".format(self.baseurl, table_id)
        self.delete_request(url)
        logger.info("Deleted single table (ID: {0})".format(table_id))

    @api(version="3.5")
    def update(self, table_item):
        if not table_item.id:
            error = "table item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}".format(self.baseurl, table_item.id)
        update_req = RequestFactory.Table.update_req(table_item)
        server_response = self.put_request(url, update_req)
        logger.info("Updated table item (ID: {0})".format(table_item.id))
        updated_table = TableItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_table

    # Get all columns of the table
    @api(version="3.5")
    def populate_columns(self, table_item, req_options=None):
        if not table_item.id:
            error = "Table item missing ID. table must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def column_fetcher():
            return Pager(
                lambda options: self._get_columns_for_table(table_item, options),
                req_options,
            )

        table_item._set_columns(column_fetcher)
        logger.info("Populated columns for table (ID: {0}".format(table_item.id))

    def _get_columns_for_table(self, table_item, req_options=None):
        url = "{0}/{1}/columns".format(self.baseurl, table_item.id)
        server_response = self.get_request(url, req_options)
        columns = ColumnItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        return columns, pagination_item

    @api(version="3.5")
    def update_column(self, table_item, column_item):
        url = "{0}/{1}/columns/{2}".format(self.baseurl, table_item.id, column_item.id)
        update_req = RequestFactory.Column.update_req(column_item)
        server_response = self.put_request(url, update_req)
        column = ColumnItem.from_response(server_response.content, self.parent_srv.namespace)[0]

        logger.info("Updated table item (ID: {0} & column item {1}".format(table_item.id, column_item.id))
        return column

    @api(version="3.5")
    def populate_permissions(self, item):
        self._permissions.populate(item)

    @api(version="3.5")
    def update_permission(self, item, rules):
        import warnings

        warnings.warn(
            "Server.tables.update_permission is deprecated, " "please use Server.tables.update_permissions instead.",
            DeprecationWarning,
        )
        return self._permissions.update(item, rules)

    @api(version="3.5")
    def update_permissions(self, item, rules):
        return self._permissions.update(item, rules)

    @api(version="3.5")
    def delete_permission(self, item, rules):
        return self._permissions.delete(item, rules)

    @api(version="3.5")
    def populate_dqw(self, item):
        self._data_quality_warnings.populate(item)

    @api(version="3.5")
    def update_dqw(self, item, warning):
        return self._data_quality_warnings.update(item, warning)

    @api(version="3.5")
    def add_dqw(self, item, warning):
        return self._data_quality_warnings.add(item, warning)

    @api(version="3.5")
    def delete_dqw(self, item):
        self._data_quality_warnings.clear(item)
