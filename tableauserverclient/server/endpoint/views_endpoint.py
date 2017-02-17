from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, ViewItem, PaginationItem
from ...models.tag_item import TagItem
import logging
import copy

logger = logging.getLogger('tableau.endpoint.views')


class Views(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}".format(self.parent_srv.baseurl, self.parent_srv.site_id)

    # Add new tags to view
    def _add_tags(self, view_id, tag_set):
        url = "{0}/views/{1}/tags".format(self.baseurl, view_id)
        add_req = RequestFactory.Tag.add_req(tag_set)
        server_response = self.put_request(url, add_req)
        return TagItem.from_response(server_response.content)

    # Delete a view's tag by name
    def _delete_tag(self, view_id, tag_name):
        url = "{0}/views/{1}/tags/{2}".format(self.baseurl, view_id, tag_name)
        self.delete_request(url)

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

    def populate_image(self, view_item, req_options=None):
        if not view_item.id:
            error = "View item missing ID."
            raise MissingRequiredFieldError(error)
        url = "{0}/views/{1}/image".format(self.baseurl,
                                           view_item.id)
        server_response = self.get_request(url, req_options)
        view_item._image = server_response.content
        logger.info("Populated image for view (ID: {0})".format(view_item.id))

    # Update view. Currently only tags can be updated
    def update(self, view_item):
        if not view_item.id:
            error = "View item missing ID. View must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        # Remove and add tags to match the view item's tag set
        if view_item.tags != view_item._initial_tags:
            add_set = view_item.tags - view_item._initial_tags
            remove_set = view_item._initial_tags - view_item.tags
            for tag in remove_set:
                self._delete_tag(view_item.id, tag)
            if add_set:
                view_item.tags = self._add_tags(view_item.id, add_set)
            view_item._initial_tags = copy.copy(view_item.tags)
        logger.info('Updated view tags to {0}'.format(view_item.tags))

        # Returning view item to stay consistent with datasource/view update functions
        return view_item