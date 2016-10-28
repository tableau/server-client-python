from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import ViewItem, PaginationItem
import logging

logger = logging.getLogger('tableau.endpoint.views')


class Views(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    def get(self, req_options=None):
        logger.info('Querying all views on site')
        url = "{0}/views".format(self.baseurl)
        server_response = self.get_request(url, req_options)
        pagination_item = PaginationItem.from_response(server_response.content)
        all_view_items = ViewItem.from_response(server_response.content)
        return all_view_items, pagination_item

    def populate_preview_image(self, view_item):
        if not view_item.id or not view_item.workbook_id:
            error = "View item missing ID or workbook ID."
            raise MissingRequiredFieldError(error)
        url = "{0}/workbooks/{1}/views/{2}/previewImage".format(self.baseurl,
                                                                view_item.workbook_id,
                                                                view_item.id)
        server_response = self.get_request(url)
        view_item._preview_image = server_response.content
        logger.info('Populated preview image for view (ID: {0})'.format(view_item.id))
