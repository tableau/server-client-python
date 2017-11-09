from .endpoint import Endpoint, api
from .exceptions import ServerResponseError, ServerInfoEndpointNotFoundError
from ...models import ServerInfoItem
import logging
import tsc_swagger

logger = logging.getLogger('tableau.endpoint.server_info')


class ServerInfo(Endpoint):

    @api(version="2.4")
    def get(self):
        """ Retrieve the server info for the server.  This is an unauthenticated call """
        from tsc_swagger.configuration import Configuration

        server_api = tsc_swagger.ServerApi()
        response = server_api.serverinfo_get()
        return ServerInfoItem(
            product_version=response.server_info.product_version.value,
            build_number=response.server_info.product_version.build,
            rest_api_version=response.server_info.rest_api_version
        )
