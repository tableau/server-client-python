import copy
import logging

from .auth_endpoint import Auth
from .endpoint import Endpoint, api
from .. import RequestFactory, SiteItem, PaginationItem

from typing import TYPE_CHECKING, List, Optional, Tuple
if TYPE_CHECKING:
    from ..request_options import RequestOptions

logger = logging.getLogger("tableau.endpoint.sites")
wrong_site_error = "You can only {0} the site for which you are currently authenticated."


class Sites(Endpoint):
    @property
    def baseurl(self) -> str:
        return "{0}/sites".format(self.parent_srv.baseurl)

    # Gets all sites
    @api(version="2.0")
    def get(self, req_options: Optional["RequestOptions"] = None) -> Tuple[List[SiteItem], PaginationItem]:
        logger.info("Querying all sites on site")
        logger.info("Requires Server Admin permissions")
        url = self.baseurl
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_site_items = SiteItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_site_items, pagination_item

    @api(version="2.0")
    def get_current_site(self):
        return self.get_by_id(self.parent_srv.site_id)

    # Gets 1 site by id
    @api(version="2.0")
    def get_by_id(self, site_id: str) -> SiteItem:
        self._check_site_id(site_id)

        logger.info("Querying single site (ID: {0})".format(site_id))
        url = "{0}/{1}".format(self.baseurl, site_id)
        server_response = self.get_request(url)
        return SiteItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Gets 1 site by name
    @api(version="2.0")
    def get_by_name(self, site_name: str) -> SiteItem:
        if not site_name:
            error = "Site Name undefined."
            raise ValueError(error)
        logger.info("Querying single site (Name: {0})".format(site_name))
        url = "{0}/{1}?key=name".format(self.baseurl, site_name)
        server_response = self.get_request(url)
        return SiteItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Gets 1 site by content url
    @api(version="2.0")
    def get_by_content_url(self, content_url: str) -> SiteItem:
        if content_url is None:
            error = "Content URL undefined."
            raise ValueError(error)
        if not self.parent_srv.baseurl.index(content_url) > 0:
            error = "You can only work with the site you are currently authenticated for"
            logger.debug("Querying other sites requires Server Admin permissions")
            raise ValueError(error.format(""))

        logger.info("Querying single site (Content URL: {0})".format(content_url))
        url = "{0}/{1}?key=contentUrl".format(self.baseurl, content_url)
        server_response = self.get_request(url)
        return SiteItem.from_response(server_response.content, self.parent_srv.namespace)[0]

    # Update site
    @api(version="2.0")
    def update(self, site_item: SiteItem) -> SiteItem:
        self._check_site_id(site_item.id, "update")

        if site_item.admin_mode:
            if site_item.admin_mode == SiteItem.AdminMode.ContentOnly and site_item.user_quota:
                error = "You cannot set admin_mode to ContentOnly and also set a user quota"
                raise ValueError(error)

        url = "{0}/{1}".format(self.baseurl, site_item.id)
        update_req = RequestFactory.Site.update_req(site_item, self.parent_srv)
        server_response = self.put_request(url, update_req)
        logger.info("Updated site item (ID: {0})".format(site_item.id))
        update_site = copy.copy(site_item)
        return update_site._parse_common_tags(server_response.content, self.parent_srv.namespace)

    # Delete 1 site object
    @api(version="2.0")
    def delete(self, site_id: str) -> None:
        self._check_site_id(site_id, "delete")
        url = "{0}/{1}".format(self.baseurl, site_id)
        if not site_id == self.parent_srv.site_id:
            error = "You can only delete the site you are currently authenticated for"
            raise ValueError(error)
        self.delete_request(url)
        Auth(self.parent_srv).sign_out()
        logger.info("Deleted single site (ID: {0}) and signed out".format(site_id))

    # Create new site
    @api(version="2.0")
    def create(self, site_item: SiteItem) -> SiteItem:
        if site_item.admin_mode:
            if site_item.admin_mode == SiteItem.AdminMode.ContentOnly and site_item.user_quota:
                error = "You cannot set admin_mode to ContentOnly and also set a user quota"
                raise ValueError(error)

        url = self.baseurl
        create_req = RequestFactory.Site.create_req(site_item, self.parent_srv)
        server_response = self.post_request(url, create_req)
        new_site = SiteItem.from_response(server_response.content, self.parent_srv.namespace)[0]
        logger.info("Created new site (ID: {0})".format(new_site.id))
        return new_site

    @api(version="3.5")
    def encrypt_extracts(self, site_id: str) -> None:
        self._check_site_id(site_id)
        url = "{0}/{1}/encrypt-extracts".format(self.baseurl, site_id)
        empty_req = RequestFactory.Empty.empty_req()
        self.post_request(url, empty_req)

    @api(version="3.5")
    def decrypt_extracts(self, site_id: str) -> None:
        self._check_site_id(site_id)
        url = "{0}/{1}/decrypt-extracts".format(self.baseurl, site_id)
        empty_req = RequestFactory.Empty.empty_req()
        self.post_request(url, empty_req)

    @api(version="3.5")
    def re_encrypt_extracts(self, site_id: str) -> None:
        self._check_site_id(site_id)
        url = "{0}/{1}/reencrypt-extracts".format(self.baseurl, site_id)
        empty_req = RequestFactory.Empty.empty_req()
        self.post_request(url, empty_req)

    def _check_site_id(self, site_id, action="work with"):
        logger.debug("Logged in to site {0}, called site {1}".format(self.parent_srv.site_id, site_id))
        if not site_id:
            error = "Site ID undefined."
            raise ValueError(error)
        url = "{0}/{1}/reencrypt-extracts".format(self.baseurl, site_id)

        empty_req = RequestFactory.Empty.empty_req()
        self.post_request(url, empty_req)
