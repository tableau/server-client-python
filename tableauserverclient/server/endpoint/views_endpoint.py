from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError
from .resource_tagger import _ResourceTagger
from .. import RequestFactory, ViewItem, PaginationItem
from ...models.tag_item import TagItem
import logging

logger = logging.getLogger('tableau.endpoint.views')


class Views(Endpoint):
    def __init__(self, parent_srv):
        super(Views, self).__init__(parent_srv)
        self._resource_tagger = _ResourceTagger(parent_srv)

    # Used because populate_preview_image functionaliy requires workbook endpoint
    @property
    def siteurl(self):
        return "{0}/sites/{1}".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    @property
    def baseurl(self):
        return "{0}/views".format(self.siteurl)

    @api(version="2.2")
    def get(self, req_options=None):
        logger.info('Querying all views on site')
        server_response = self.get_request(self.baseurl, req_options)
        pagination_item = PaginationItem.from_response(server_response.content, self.parent_srv.namespace)
        all_view_items = ViewItem.from_response(server_response.content, self.parent_srv.namespace)
        return all_view_items, pagination_item

    @api(version="2.0")
    def populate_preview_image(self, view_item):
        if not view_item.id or not view_item.workbook_id:
            error = "View item missing ID or workbook ID."
            raise MissingRequiredFieldError(error)
        url = "{0}/workbooks/{1}/views/{2}/previewImage".format(self.siteurl,
                                                                view_item.workbook_id,
                                                                view_item.id)
        server_response = self.get_request(url)
        view_item._preview_image = server_response.content
        logger.info('Populated preview image for view (ID: {0})'.format(view_item.id))

    def populate_image(self, view_item, req_options=None):
        if not view_item.id:
            error = "View item missing ID."
            raise MissingRequiredFieldError(error)
        url = "{0}/{1}/image".format(self.baseurl, view_item.id)
        server_response = self.get_request(url, req_options)
        view_item._image = server_response.content
        logger.info("Populated image for view (ID: {0})".format(view_item.id))

    # Update view. Currently only tags can be updated
    def update(self, view_item):
        if not view_item.id:
            error = "View item missing ID. View must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        self._resource_tagger.update_tags(self.baseurl, view_item)

        # Returning view item to stay consistent with datasource/view update functions
        return view_item
