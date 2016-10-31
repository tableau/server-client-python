from .exceptions import ServerResponseError
import logging


logger = logging.getLogger('tableau.endpoint')

Success_codes = [200, 201, 204]


class Endpoint(object):
    def __init__(self, parent_srv):
        self.parent_srv = parent_srv

    @staticmethod
    def _make_common_headers(auth_token, content_type):
        headers = {}
        if auth_token is not None:
            headers['x-tableau-auth'] = auth_token
        if content_type is not None:
            headers['content-type'] = content_type

        return headers

    def _make_request(self, method, url, content=None, request_object=None, auth_token=None, content_type=None):
        if request_object is not None:
            url = request_object.apply_query_params(url)
        parameters = {}
        parameters.update(self.parent_srv.http_options)
        parameters['headers'] = Endpoint._make_common_headers(auth_token, content_type)

        if content is not None:
            parameters['data'] = content

        server_response = method(url, **parameters)
        self._check_status(server_response)

        # This check is to determine if the response is a text response (xml or otherwise)
        # so that we do not attempt to log bytes and other binary data.
        if server_response.encoding:
            logger.debug(u'Server response from {0}:\n\t{1}'.format(
                url, server_response.content.decode(server_response.encoding)))
        return server_response

    @staticmethod
    def _check_status(server_response):
        if server_response.status_code not in Success_codes:
            raise ServerResponseError.from_response(server_response.content)

    def get_unauthenticated_request(self, url, request_object=None):
        return self._make_request(self.parent_srv.session.get, url, request_object=request_object)

    def get_request(self, url, request_object=None):
        return self._make_request(self.parent_srv.session.get, url, auth_token=self.parent_srv.auth_token,
                                  request_object=request_object)

    def delete_request(self, url):
        # We don't return anything for a delete
        self._make_request(self.parent_srv.session.delete, url, auth_token=self.parent_srv.auth_token)

    def put_request(self, url, xml_request, content_type='text/xml'):
        return self._make_request(self.parent_srv.session.put, url,
                                  content=xml_request,
                                  auth_token=self.parent_srv.auth_token,
                                  content_type=content_type)

    def post_request(self, url, xml_request, content_type='text/xml'):
        return self._make_request(self.parent_srv.session.post, url,
                                  content=xml_request,
                                  auth_token=self.parent_srv.auth_token,
                                  content_type=content_type)
