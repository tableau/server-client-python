import logging

from .. import RequestFactory, PermissionsItem

from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError


logger = logging.getLogger(__name__)


class _PermissionsEndpoint(Endpoint):
    ''' Adds permission model to another endpoint

    Tableau permissions model is identical between objects but they are nested under
    the parent object endpoint (i.e. permissions for workbooks are under
    /workbooks/:id/permission).  This class is meant to be instantated inside a
    parent endpoint which has these supported endpoints
    '''
    def __init__(self, parent_srv, owner_baseurl):
        super(_PermissionsEndpoint, self).__init__(parent_srv)

        # owner_baseurl is the baseurl of the parent.  The MUST be a lambda
        # since we don't know the full site URL until we sign in.  If
        # populated without, we will get a sign-in error
        self.owner_baseurl = owner_baseurl

    def update(self, item, permission_item):
        url = '{0}/{1}/permissions'.format(self.owner_baseurl(), item.id)
        update_req = RequestFactory.Permission.add_req(item, permission_item)
        response = self.put_request(url, update_req)
        permissions = PermissionsItem.from_response(response.content,
                                                    self.parent_srv.namespace)
        breakpoint()
        logger.info('Updated permissions for item {0}'.format(item.id))

        return permissions

    def delete(self, item, capability_item):
        for capability_type, capability_mode in capability_item.map.items():
            url = '{0}/{1}/permissions/{2}/{3}/{4}/{5}'.format(
                self.owner_baseurl(), item.id,
                capability_item.type + 's',
                capability_item.object_id, capability_type,
                capability_mode)

            logger.debug('Removing {0} permission for capabilty {1}'.format(
                capability_mode, capability_type))

            self.delete_request(url)

        logger.info('Deleted permission for {0} {1} item {2}'.format(
            capability_item.type,
            capability_item.object_id,
            item.id))

    def populate(self, item):
        if not item.id:
            error = "Server item is missing ID. Item must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def permission_fetcher():
            return self._get_permissions(item)

        item._set_permissions(permission_fetcher)
        logger.info('Populated permissions for item (ID: {0})'.format(item.id))

    def _get_permissions(self, item, req_options=None):
        url = "{0}/{1}/permissions".format(self.owner_baseurl(), item.id)
        server_response = self.get_request(url, req_options)
        permissions = PermissionsItem.from_response(server_response.content,
                                                    self.parent_srv.namespace)
        return permissions
