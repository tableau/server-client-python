import logging

from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory, DQWItem

logger = logging.getLogger(__name__)


class _DataQualityWarningEndpoint(Endpoint):
    def __init__(self, parent_srv, resource_type):
        super(_DataQualityWarningEndpoint, self).__init__(parent_srv)
        self.resource_type = resource_type

    @property
    def baseurl(self):
        return "{0}/sites/{1}/dataQualityWarnings/{2}".format(
            self.parent_srv.baseurl, self.parent_srv.site_id, self.resource_type
        )

    def add(self, resource, warning):
        url = "{baseurl}/{content_luid}".format(baseurl=self.baseurl, content_luid=resource.id)
        add_req = RequestFactory.DQW.add_req(warning)
        response = self.post_request(url, add_req)
        warnings = DQWItem.from_response(response.content, self.parent_srv.namespace)
        logger.info("Added dqw for resource {0}".format(resource.id))

        return warnings

    def update(self, resource, warning):
        url = "{baseurl}/{content_luid}".format(baseurl=self.baseurl, content_luid=resource.id)
        add_req = RequestFactory.DQW.update_req(warning)
        response = self.put_request(url, add_req)
        warnings = DQWItem.from_response(response.content, self.parent_srv.namespace)
        logger.info("Added dqw for resource {0}".format(resource.id))

        return warnings

    def clear(self, resource):
        url = "{baseurl}/{content_luid}".format(baseurl=self.baseurl, content_luid=resource.id)
        return self.delete_request(url)

    def populate(self, item):
        if not item.id:
            error = "Server item is missing ID. Item must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def dqw_fetcher():
            return self._get_data_quality_warnings(item)

        item._set_data_quality_warnings(dqw_fetcher)
        logger.info("Populated permissions for item (ID: {0})".format(item.id))

    def _get_data_quality_warnings(self, item, req_options=None):
        url = "{baseurl}/{content_luid}".format(baseurl=self.baseurl, content_luid=item.id)
        server_response = self.get_request(url, req_options)
        dqws = DQWItem.from_response(server_response.content, self.parent_srv.namespace)

        return dqws
