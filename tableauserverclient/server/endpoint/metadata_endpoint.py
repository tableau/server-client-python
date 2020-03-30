from .endpoint import Endpoint, api
from .exceptions import GraphQLError
import logging
import json

logger = logging.getLogger('tableau.endpoint.metadata')


class Metadata(Endpoint):
    @property
    def baseurl(self):
        return "{0}/api/metadata/graphql".format(self.parent_srv.server_address)

    @staticmethod
    def extract_values(obj, key):
        """Pull all values of specified key from nested JSON."""
        arr = []

        def extract(obj, arr, key):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        extract(v, arr, key)
                    elif k == key:
                        arr.append(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract(item, arr, key)
            return arr

        results = extract(obj, arr, key)
        return results

    @staticmethod
    def get_page_info(result):
        next_page = Metadata.extract_values(result, 'hasNextPage').pop()
        cursor = Metadata.extract_values(result, 'endCursor').pop()
        return next_page, cursor

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
    def paginated_query(self, query, variables=None, abort_on_error=False):
        #boilerplate
        logger.info('Querying Metadata API')
        url = self.baseurl
        # validate this is a pagable query
        # if all (k in foo for k in ("foo","bar"))

        graphql_query = json.dumps({'query': query, 'variables': variables})
        parsed_query = json.loads(graphql_query)

        if not all(k in parsed_query['variables'] for k in ('first', 'afterToken')):
            raise Exception

        paginated_results = []

        # get first page
        server_response = self.post_request(url, graphql_query, content_type='text/json')
        results = server_response.json()
        
        if abort_on_error and results.get('errors', None):
            raise GraphQLError(results['errors'])
        
        paginated_results.append(results)
        # repeat
        has_another_page, cursor = self.get_page_info(results)
        while has_another_page:
            variables.update({'afterToken': cursor})
            print("Calling Token: " + cursor)
            graphql_query = json.dumps({'query': query, 'variables': variables})
            has_another_page, cursor = self.get_page_info(results)
            server_response = self.post_request(url, graphql_query, content_type='text/json')
            results = server_response.json()
            paginated_results.append(results)
        return paginated_results
