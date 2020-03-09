from .endpoint import Endpoint, api
from .exceptions import GraphQLError
import logging
import json
from urllib.parse import urlparse

logger = logging.getLogger('tableau.endpoint.metadata')


class Metadata(Endpoint):
    _backfill_port = None

    @property
    def baseurl(self):
        return "{0}/api/metadata/graphql".format(self.parent_srv.server_address)

    @property
    def backfill_port(self):
        if self._backfill_port is None:
            self._backfill_port, _ = self._find_backfill_port()
        
        return self._backfill_port

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
    def content_backfill_status(self):
        url = self.parent_srv.server_address[:-1] + ":" + str(self.backfill_port) + "/relationship-service-war/control/backfill/status/"
        response = self.get_request(url)
        return response.json()

    @api("3.2")
    def shortcut_backfill_status(self):
        url = self.parent_srv.server_address[:-1] + ":" + str(self.backfill_port) + "/relationship-service-war/control/secondaryIndexing/shortcutBackfillComplete/"
        response = self.get_request(url)
        return True if response.content == b'true' else False

    @api("3.2")
    def tsm_login(self, port):
        hostname = urlparse(self.parent_srv.server_address).netloc
        url = "https://" + hostname + ":" + str(port) + "/api/0.5/login"

        authentication = {
            'authentication': {
                'name': 'workgroupuser',
                'password': 'HardW0rker',
            }
        }

        auth_json = json.dumps(authentication)
        self.parent_srv.add_http_options({'verify': False})
        response = self.post_request(url, auth_json, 'application/json')
        print(response)

    @api("3.2")
    def _find_backfill_port(self):
        hostname = urlparse(self.parent_srv.server_address).netloc
        url = "https://" + hostname + ":" + str(8850) + "/api/0.5/ports"
        response = self.get_request(url)
        return self.extract_noninteractive_port(response.content)

    @staticmethod
    def extract_noninteractive_port(blob):

        parsed = json.loads(blob)

        primary_port = None
        primary_node = None

        for node in parsed['clusterPorts']['nodes']:
            for service in node['services']:
                if service['serviceName'] != "noninteractive":
                    continue
                for instansce in service['instances']:
                    for port in instansce['ports']:
                        if port['portType'] == 'primary':
                            print(port['port'])
                            primary_port = port['port']
                            node = node['nodeId']

        return primary_port, primary_node