import logging
from typing import TYPE_CHECKING
import warnings

from defusedxml.ElementTree import fromstring

from tableauserverclient.server.endpoint.endpoint import Endpoint, api
from tableauserverclient.server.endpoint.exceptions import ServerResponseError
from tableauserverclient.server.request_factory import RequestFactory

from tableauserverclient.helpers.logging import logger

if TYPE_CHECKING:
    from tableauserverclient.models.site_item import SiteItem
    from tableauserverclient.models.tableau_auth import Credentials


class Auth(Endpoint):
    class contextmgr(object):
        def __init__(self, callback):
            self._callback = callback

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._callback()

    @property
    def baseurl(self) -> str:
        return "{0}/auth".format(self.parent_srv.baseurl)

    @api(version="2.0")
    def sign_in(self, auth_req: "Credentials") -> contextmgr:
        """
        Sign in to a Tableau Server or Tableau Online using a credentials object.

        The credentials object can either be a TableauAuth object, a
        PersonalAccessTokenAuth object, or a JWTAuth object. This method now
        accepts them all. The object should be populated with the site_id and
        optionally a user_id to impersonate.

        Creates a context manager that will sign out of the server upon exit.
        """
        url = "{0}/{1}".format(self.baseurl, "signin")
        signin_req = RequestFactory.Auth.signin_req(auth_req)
        server_response = self.parent_srv.session.post(
            url, data=signin_req, **self.parent_srv.http_options, allow_redirects=False
        )
        # manually handle a redirect so that we send the correct POST request instead of GET
        # this will make e.g http://online.tableau.com work to redirect to http://east.online.tableau.com
        if server_response.status_code == 301:
            server_response = self.parent_srv.session.post(
                server_response.headers["Location"],
                data=signin_req,
                **self.parent_srv.http_options,
                allow_redirects=False,
            )
        self.parent_srv._namespace.detect(server_response.content)
        self._check_status(server_response, url)
        parsed_response = fromstring(server_response.content)
        site_id = parsed_response.find(".//t:site", namespaces=self.parent_srv.namespace).get("id", None)
        user_id = parsed_response.find(".//t:user", namespaces=self.parent_srv.namespace).get("id", None)
        auth_token = parsed_response.find("t:credentials", namespaces=self.parent_srv.namespace).get("token", None)
        self.parent_srv._set_auth(site_id, user_id, auth_token)
        logger.info("Signed into {0} as user with id {1}".format(self.parent_srv.server_address, user_id))
        return Auth.contextmgr(self.sign_out)

    # We use the same request that username/password login uses for all auth types.
    # The distinct methods are mostly useful for explicitly showing api version support for each auth type
    @api(version="3.6")
    def sign_in_with_personal_access_token(self, auth_req: "Credentials") -> contextmgr:
        return self.sign_in(auth_req)

    @api(version="3.17")
    def sign_in_with_json_web_token(self, auth_req: "Credentials") -> contextmgr:
        return self.sign_in(auth_req)

    @api(version="2.0")
    def sign_out(self) -> None:
        url = "{0}/{1}".format(self.baseurl, "signout")
        # If there are no auth tokens you're already signed out. No-op
        if not self.parent_srv.is_signed_in():
            return
        self.post_request(url, "")
        self.parent_srv._clear_auth()
        logger.info("Signed out")

    @api(version="2.6")
    def switch_site(self, site_item: "SiteItem") -> contextmgr:
        url = "{0}/{1}".format(self.baseurl, "switchSite")
        switch_req = RequestFactory.Auth.switch_req(site_item.content_url)
        try:
            server_response = self.post_request(url, switch_req)
        except ServerResponseError as e:
            if e.code == "403070":
                return Auth.contextmgr(self.sign_out)
            else:
                raise e
        self.parent_srv._namespace.detect(server_response.content)
        self._check_status(server_response, url)
        parsed_response = fromstring(server_response.content)
        site_id = parsed_response.find(".//t:site", namespaces=self.parent_srv.namespace).get("id", None)
        user_id = parsed_response.find(".//t:user", namespaces=self.parent_srv.namespace).get("id", None)
        auth_token = parsed_response.find("t:credentials", namespaces=self.parent_srv.namespace).get("token", None)
        self.parent_srv._set_auth(site_id, user_id, auth_token)
        logger.info("Signed into {0} as user with id {1}".format(self.parent_srv.server_address, user_id))
        return Auth.contextmgr(self.sign_out)

    @api(version="3.10")
    def revoke_all_server_admin_tokens(self) -> None:
        url = "{0}/{1}".format(self.baseurl, "revokeAllServerAdminTokens")
        self.post_request(url, "")
        logger.info("Revoked all tokens for all server admins")
