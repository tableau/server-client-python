import logging
from typing import Union
from collections.abc import Iterable

from tableauserverclient.server.endpoint.default_permissions_endpoint import _DefaultPermissionsEndpoint
from tableauserverclient.server.endpoint.dqw_endpoint import _DataQualityWarningEndpoint
from tableauserverclient.server.endpoint.endpoint import api, Endpoint
from tableauserverclient.server.endpoint.exceptions import MissingRequiredFieldError
from tableauserverclient.server.endpoint.permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.server.endpoint.resource_tagger import TaggingMixin
from tableauserverclient.server import RequestFactory
from tableauserverclient.models import DatabaseItem, TableItem, PaginationItem, Resource

from tableauserverclient.helpers.logging import logger


class Databases(Endpoint, TaggingMixin):
    def __init__(self, parent_srv):
        super().__init__(parent_srv)

        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._default_permissions = _DefaultPermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._data_quality_warnings = _DataQualityWarningEndpoint(parent_srv, Resource.Database)

    @property
    def baseurl(self):
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/databases"

    @api(version="3.5")
    def get(self, req_options=None):
        logger.info("Querying all databases on site")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_database_items = DatabaseItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_database_items, pagination_item

    # Get 1 database
    @api(version="3.5")
    def get_by_id(self, database_id):
        if not database_id:
            error = "database ID undefined."
            raise ValueError(error)
        logger.info(f"Querying single database (ID: {database_id})")
        url = f"{self.baseurl}/{database_id}"
        server_response = self.get_request(url)
        return DatabaseItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    @api(version="3.5")
    def delete(self, database_id):
        if not database_id:
            error = "Database ID undefined."
            raise ValueError(error)
        url = f"{self.baseurl}/{database_id}"
        self.delete_request(url)
        logger.info(f"Deleted single database (ID: {database_id})")

    @api(version="3.5")
    def update(self, database_item):
        if not database_item.id:
            error = "Database item missing ID."
            raise MissingRequiredFieldError(error)

        url = f"{self.baseurl}/{database_item.id}"
        update_req = RequestFactory.Database.update_req(database_item)
        server_response = self.put_request(url, update_req)
        logger.info(f"Updated database item (ID: {database_item.id})")
        updated_database = DatabaseItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        return updated_database

    # Not Implemented Yet
    @api(version="99")
    def populate_tables(self, database_item):
        if not database_item.id:
            error = "database item missing ID. database must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def column_fetcher():
            return self._get_tables_for_database(database_item)

        database_item._set_tables(column_fetcher)
        logger.info(f"Populated tables for database (ID: {database_item.id}")

    def _get_tables_for_database(self, database_item):
        url = f"{self.baseurl}/{database_item.id}/tables"
        server_response = self.get_request(url)
        tables = TableItem.from_response(server_response.content, self.parent_srv.namespace)
        return tables

    @api(version="3.5")
    def populate_permissions(self, item):
        self._permissions.populate(item)

    @api(version="3.5")
    def update_permissions(self, item, rules):
        return self._permissions.update(item, rules)

    @api(version="3.5")
    def delete_permission(self, item, rules):
        self._permissions.delete(item, rules)

    @api(version="3.5")
    def populate_table_default_permissions(self, item):
        self._default_permissions.populate_default_permissions(item, Resource.Table)

    @api(version="3.5")
    def update_table_default_permissions(self, item):
        return self._default_permissions.update_default_permissions(item, Resource.Table)

    @api(version="3.5")
    def delete_table_default_permissions(self, item):
        self._default_permissions.delete_default_permission(item, Resource.Table)

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

    @api(version="3.9")
    def add_tags(self, item: Union[DatabaseItem, str], tags: Iterable[str]) -> set[str]:
        return super().add_tags(item, tags)

    @api(version="3.9")
    def delete_tags(self, item: Union[DatabaseItem, str], tags: Iterable[str]) -> None:
        super().delete_tags(item, tags)

    @api(version="3.9")
    def update_tags(self, item: DatabaseItem) -> None:
        raise NotImplementedError("Update tags is not supported for databases.")
