import logging

from .. import RequestFactory, DQWItem

from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError


logger = logging.getLogger(__name__)


class _DQWEndpoint(Endpoint):
    """ adds data quality warnings
    """

    def __init__(self, parent_srv, resource_type):
        super(_DQWEndpoint, self).__init__(parent_srv)

        # owner_baseurl is the baseurl of the parent.  The MUST be a lambda
        # since we don't know the full site URL until we sign in.  If
        # populated without, we will get a sign-in error

        self.resource_type = resource_type

    @property
    def baseurl(self):
        return "{0}/sites/{1}/dataQualityWarnings/{2}".format(self.parent_srv.baseurl, self.parent_srv.site_id, self.resource_type)

    def add_dqw(self, resource, warning):
        url = '{baseurl}/{content_luid}'.format(baseurl=self.baseurl, content_luid=resource.id)
        add_req = RequestFactory.DQW.add_req(warning)
        response = self.post_request(url, add_req)
        warnings = DQWItem.from_response(response.content,
                                                    self.parent_srv.namespace)
        logger.info('Added dqw for resource {0}'.format(resource.id))

        return warnings

    def delete(self, resource, warning):
        url = '/{content_luid}'.format(content_luid=resource.id)
        return self.delete_request(url)

    def populate(self, item):
        if not item.id:
            error = "Server item is missing ID. Item must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def dqw_fetcher():
            return self._get_dqws(item)

        item._set_dqws(dqw_fetcher)
        logger.info('Populated permissions for item (ID: {0})'.format(item.id))

    def _get_dqws(self, item, req_options=None):
        url = "{baseurl}/{content_luid}".format(baseurl=self.baseurl, content_luid=item.id)
        server_response = self.get_request(url, req_options)
        dqws = DQWItem.from_response(server_response.content,
                                                    self.parent_srv.namespace)

        return dqws
