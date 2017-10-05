from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError
from .. import SubscriptionItem, PaginationItem
import logging

logger = logging.getLogger('tableau.endpoint.subscriptions')


class Subscriptions(Endpoint):
    @property
    def baseurl(self):
        return "{0}/sites/{1}/subscriptions".format(self.parent_srv.baseurl,
                                                             self.parent_srv.site_id)

    @api(version='2.3')
    def get(self, req_options=None):
        logger.info('Querying all subscriptions for the site')
        url = self.baseurl
        server_response = self.get_request(url, req_options)

        pagination_item = PaginationItem.from_response(server_response.content)
        all_subscriptions = SubscriptionItem.from_response(server_response.content)
        return all_subscriptions, pagination_item

    @api(version='2.3')
    def get_by_id(self, subscription_id):
        if not subscription_id:
            error = "No Subscription ID provided"
            raise ValueError(error)
        logger.info("Querying a single subscription by id ({})".format(subscription_id))
        url = "{}/{}".format(self.baseurl, subscription_id)
        server_response = self.get_request(url)
        return SubscriptionItem.from_response(server_response.content)[0]
