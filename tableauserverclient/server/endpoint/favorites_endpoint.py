from endpoint import Endpoint
from exceptions import MissingRequiredFieldError
from .. import RequestFactory, FavoriteItem
import logging

logger = logging.getLogger('tableau.endpoint.favorites')


class Favorites(Endpoint):
    def __init__(self, parent_srv):
        super(Endpoint, self).__init__()
        self.baseurl = "{0}/sites/{1}/favorites"
        self.parent_srv = parent_srv

    def _construct_url(self):
        return self.baseurl.format(self.parent_srv.baseurl, self.parent_srv.site_id)

    def add(self, favorite_item, user_item):
        url = "{0}/{1}".format(self._construct_url(), user_item.id)
        add_req = RequestFactory().favorite.add_req(favorite_item)
        server_response = self.put_request(url, add_req)
        logger.info('Added {0} (ID: {1}) to {2}\'s favorites'.format(favorite_item.type,
                                                                     favorite_item.id, user_item.name))
        return FavoriteItem.from_response(server_response.text)

    def delete(self, favorite_item, user_item):
        if not user_item.id:
            error = "User item missing ID."
            raise MissingRequiredFieldError(error)

        url = "{0}/{1}/{2}s/{3}".format(self._construct_url(), user_item.id,
                                       favorite_item.type.lower(), favorite_item.id)
        self.delete_request(url)
        logger.info('Deleted {0} (ID: {1}) from {2}\'s favorites'.format(favorite_item.type,
                                                                         favorite_item.id, user_item.name))
