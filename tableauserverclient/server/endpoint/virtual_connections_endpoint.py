from functools import partial
from typing import List, Optional, TYPE_CHECKING, Tuple, Union

from tableauserverclient.models.connection_item import ConnectionItem
from tableauserverclient.models.pagination_item import PaginationItem
from tableauserverclient.models.virtual_connection_item import VirtualConnectionItem
from tableauserverclient.server.request_factory import RequestFactory
from tableauserverclient.server.request_options import RequestOptions
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.endpoint.permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.server.endpoint.resource_tagger import _ResourceTagger
from tableauserverclient.server.pager import Pager

if TYPE_CHECKING:
    from tableauserverclient.server import Server


class VirtualConnections(QuerysetEndpoint[VirtualConnectionItem]):
    def __init__(self, parent_srv: "Server") -> None:
        super().__init__(parent_srv)
        self._permissions = _PermissionsEndpoint(parent_srv, lambda: self.baseurl)
        self._resource_tagger = _ResourceTagger(parent_srv)

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/virtualConnections"

    @api(version="3.18")
    def get(self, req_options: Optional[RequestOptions] = None) -> Tuple[List[VirtualConnectionItem], PaginationItem]:
        server_response = self.get_request(self.baseurl, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        virtual_connections = VirtualConnectionItem.from_response(server_response.content, self.parent_srv.namespace)
        return virtual_connections, pagination_item

    @api(version="3.18")
    def populate_connections(self, virtual_connection: VirtualConnectionItem) -> VirtualConnectionItem:
        def _connection_fetcher():
            return Pager(partial(self._get_virtual_database_connections, virtual_connection))

        virtual_connection._connections = _connection_fetcher
        return virtual_connection

    def _get_virtual_database_connections(
        self, virtual_connection: VirtualConnectionItem, req_options: Optional[RequestOptions] = None
    ) -> Tuple[List[ConnectionItem], PaginationItem]:
        server_response = self.get_request(f"{self.baseurl}/{virtual_connection.id}/connections", req_options)
        connections = ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)

        return connections, pagination_item

    @api(version="3.18")
    def update_connection_db_connection(
        self, virtual_connection: Union[str, VirtualConnectionItem], connection: ConnectionItem
    ) -> ConnectionItem:
        vconn_id = getattr(virtual_connection, "id", virtual_connection)
        url = f"{self.baseurl}/{vconn_id}/connections/{connection.id}/modify"
        xml_request = RequestFactory.VirtualConnection.update_db_connection(connection)
        server_response = self.put_request(url, xml_request)
        return ConnectionItem.from_response(server_response.content, self.parent_srv.namespace)[0]
