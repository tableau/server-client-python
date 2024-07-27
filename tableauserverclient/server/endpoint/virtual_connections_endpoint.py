from typing import List, Optional, TYPE_CHECKING, Tuple

from tableauserverclient.server.request_options import RequestOptions
from tableauserverclient.server.endpoint.endpoint import QuerysetEndpoint, api
from tableauserverclient.server.endpoint.permissions_endpoint import _PermissionsEndpoint
from tableauserverclient.server.endpoint.resource_tagger import _ResourceTagger
from tableauserverclient.models.pagination_item import PaginationItem
from tableauserverclient.models.virtual_connection_item import VirtualConnectionItem

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
