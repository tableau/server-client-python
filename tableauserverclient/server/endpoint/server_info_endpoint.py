from .endpoint import Endpoint
from ...models import ServerInfoItem
import logging

logger = logging.getLogger('tableau.endpoint.server_info')


class ServerInfo(Endpoint):
    @property
    def baseurl(self):
        return "{0}/serverInfo".format(self.parent_srv.baseurl)

    def get(self):
        """ Retrieve the server info for the server.  This is an unauthenticated call """
        server_response = self.get_unauthenticated_request(self.baseurl)
        server_info = ServerInfoItem.from_response(server_response.content)
        return server_info
