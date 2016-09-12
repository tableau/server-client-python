from .exceptions import ServerResponseError
import logging

logger = logging.getLogger('tableau.endpoint')

Success_codes = [200, 201, 204]


class Endpoint(object):
    def __init__(self):
        self.parent_srv = None

    @staticmethod
    def _check_status(server_response):
        if server_response.status_code not in Success_codes:
            raise ServerResponseError.from_response(server_response.content)

    def get_request(self, url, request_object=None):
        if request_object is not None:
            url = request_object.apply_query_params(url)
        auth_token = self.parent_srv.auth_token
        server_response = self.parent_srv.session.get(url,
                                                      headers={'x-tableau-auth': auth_token},
                                                      **self.parent_srv.http_options)
        self._check_status(server_response)
        if server_response.encoding:
            logger.debug(u'Server response from {0}: \n\t{1}'.format(
                url, server_response.content.decode(server_response.encoding)))
        return server_response

    def delete_request(self, url):
        auth_token = self.parent_srv.auth_token
        server_response = self.parent_srv.session.delete(url,
                                                         headers={'x-tableau-auth': auth_token},
                                                         **self.parent_srv.http_options)
        self._check_status(server_response)

    def put_request(self, url, xml_request, content_type='text/xml'):
        auth_token = self.parent_srv.auth_token
        server_response = self.parent_srv.session.put(url, data=xml_request,
                                                      headers={'x-tableau-auth': auth_token,
                                                               'content-type': content_type},
                                                      **self.parent_srv.http_options)
        self._check_status(server_response)
        if server_response.encoding:
            logger.debug(u'Server response from {0}: \n\t{1}'.format(
                url, server_response.content.decode(server_response.encoding)))
        return server_response

    def post_request(self, url, xml_request, content_type='text/xml'):
        auth_token = self.parent_srv.auth_token
        server_response = self.parent_srv.session.post(url, data=xml_request,
                                                       headers={'x-tableau-auth': auth_token,
                                                                'content-type': content_type},
                                                       **self.parent_srv.http_options)
        self._check_status(server_response)
        if server_response.encoding:
            logger.debug(u'Server response from {0}: \n\t{1}'.format(
                url, server_response.content.decode(server_response.encoding)))
        return server_response
