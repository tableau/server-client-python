from tableauserverclient.models.extensions_item import ExtensionsServer
from tableauserverclient.server.endpoint.endpoint import Endpoint
from tableauserverclient.server.endpoint.endpoint import api


class Extensions(Endpoint):
    def __init__(self, parent_srv):
        super().__init__(parent_srv)

    @property
    def _server_baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/settings/extensions"

    @api(version="3.21")
    def get_server_settings(self) -> ExtensionsServer:
        """Lists the settings for extensions of a server

        Returns
        -------
        ExtensionsServer
            The server extensions settings
        """
        response = self.get_request(self._server_baseurl)
        return ExtensionsServer.from_response(response.content, self.parent_srv.namespace)
