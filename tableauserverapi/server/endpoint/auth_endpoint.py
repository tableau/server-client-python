from endpoint import Endpoint
from .. import RequestFactory, TableauAuth
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
        TableauAuth.from_response(self.parent_srv, server_response.text)
        logger.info('Signed into {0} as {1}'.format(self.parent_srv.server_address, auth_req.username))
        return Auth.contextmgr(self.sign_out)

    def sign_out(self):
        url = "{0}/{1}".format(self.baseurl, 'signout')
        self.post_request(url, '')
        self.parent_srv._clear_auth()
        logger.info('Signed out')
