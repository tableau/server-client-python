import logging

from .endpoint import Endpoint, api
from .exceptions import (
    ServerResponseError,
    ServerInfoEndpointNotFoundError,
    EndpointUnavailableError,
)
from ...models import ServerInfoItem

logger = logging.getLogger("tableau.endpoint.server_info")


class ServerInfo(Endpoint):
    def __init__(self, server):
        self.parent_srv = server
        self._info = None

    @property
    def serverInfo(self):
        if not self._info:
            self.get()
        return self._info

    def __repr__(self):
        return "<Endpoint {}>".format(self.serverInfo)

    @property
    def baseurl(self):
        return "{0}/serverInfo".format(self.parent_srv.baseurl)

    @api(version="2.4")
    def get(self):
        """Retrieve the server info for the server.  This is an unauthenticated call"""
        try:
            server_response = self.get_unauthenticated_request(self.baseurl)
        except ServerResponseError as e:
            if e.code == "404003":
                raise ServerInfoEndpointNotFoundError(e)
            if e.code == "404001":
                raise EndpointUnavailableError(e)
            raise e

        self._info = ServerInfoItem.from_response(server_response.content, self.parent_srv.namespace)
        return self._info
