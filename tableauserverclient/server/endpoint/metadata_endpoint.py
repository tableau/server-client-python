from .endpoint import Endpoint, api
from .exceptions import GraphQLError
import logging
import json
from urllib.parse import urlparse

logger = logging.getLogger('tableau.endpoint.metadata')


class Metadata(Endpoint):
    @property
    def baseurl(self):
        return "{0}/api/metadata/graphql".format(self.parent_srv.server_address)

    @property
    def control_baseurl(self):
        return "{0}/api/metadata/v1/control".format(self.parent_srv.server_address)

    @api("3.2")
    def query(self, query, variables=None, abort_on_error=False):
        logger.info('Querying Metadata API')
        url = self.baseurl

        try:
            graphql_query = json.dumps({'query': query, 'variables': variables})
        except Exception:
            # Place holder for now
            raise Exception('Must provide a string')

        # Setting content type because post_reuqest defaults to text/xml
        server_response = self.post_request(url, graphql_query, content_type='text/json')
        results = server_response.json()

        if abort_on_error and results.get('errors', None):
            raise GraphQLError(results['errors'])

        return results

    @api("3.2")
    def backfill_status(self):
        url = self.control_baseurl + "/backfill/status"
        response = self.get_request(url)
        return response.json()

    @api("3.2")
    def eventing_status(self):
        url = self.control_baseurl + "/eventing/status"
        response = self.get_request(url)
        return response.json()
