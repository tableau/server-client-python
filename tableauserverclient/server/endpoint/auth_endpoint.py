from .endpoint import Endpoint
from .. import RequestFactory, NAMESPACE
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger('tableau.endpoint.auth')


class Auth(Endpoint):
    class contextmgr(object):
        def __init__(self, callback):
            self._callback = callback

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._callback()

    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.baseurl = "{0}/auth".format(parent_srv.baseurl)
        self.parent_srv = parent_srv

    def sign_in(self, auth_req):
        url = "{0}/{1}".format(self.baseurl, 'signin')
        signin_req = RequestFactory.Auth.signin_req(auth_req)
        server_response = self.parent_srv.session.post(url, data=signin_req,
                                                       **self.parent_srv.http_options)
        Endpoint._check_status(server_response)
        parsed_response = ET.fromstring(server_response.content)
        site_id = parsed_response.find('.//t:site', namespaces=NAMESPACE).get('id', None)
        user_id = parsed_response.find('.//t:user', namespaces=NAMESPACE).get('id', None)
        auth_token = parsed_response.find('t:credentials', namespaces=NAMESPACE).get('token', None)
        self.parent_srv._set_auth(site_id, user_id, auth_token)
        logger.info('Signed into {0} as {1}'.format(self.parent_srv.server_address, auth_req.username))
        return Auth.contextmgr(self.sign_out)

    def sign_out(self):
        url = "{0}/{1}".format(self.baseurl, 'signout')
        self.post_request(url, '')
        self.parent_srv._clear_auth()
        logger.info('Signed out')
