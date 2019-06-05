import logging

from .. import RequestFactory
from ...models import ExplicitPermissions, PermissionsRule

from .endpoint import Endpoint, api
from .exceptions import MissingRequiredFieldError


logger = logging.getLogger(__name__)


class _DefaultPermissionsEndpoint(Endpoint):
    ''' Adds default-permission model to another endpoint

    Tableau default-permissions model applies only to databases and projects
    and then takes an object type in the uri to set the defaults.
    This class is meant to be instantated inside a parent endpoint which
    has these supported endpoints
    '''
    def __init__(self, parent_srv, owner_baseurl):
        super(_DefaultPermissionsEndpoint, self).__init__(parent_srv)

        # owner_baseurl is the baseurl of the parent.  The MUST be a lambda
        # since we don't know the full site URL until we sign in.  If
        # populated without, we will get a sign-in error
        self.owner_baseurl = owner_baseurl

    def update_default_permissions(self, resource, template_type, permissions):
        url = '{0}/{1}/default-permissions/{2}'.format(self.owner_baseurl(), resource.id, template_type)
        update_req = RequestFactory.Permission.add_req(permissions)
        response = self.put_request(url, update_req)
        permissions = ExplicitPermissions.from_response(response.content,
                                                        self.parent_srv.namespace)
        logger.info('Updated permissions for resource {0}'.format(resource.id))

        return permissions

    def delete_default_permission(self, resource, template_type, rule):
        for capability, mode in rule.capabilities.items():
            url = '{0}/{1}/default-permissions/{2}/{3}/{4}/{5}/{6}'.format(
                self.owner_baseurl(),
                resource.id,
                template_type,
                rule.grantee.permissions_grantee_type + 's',
                rule.grantee.id,
                capability,
                mode)

            logger.debug('Removing {0} permission for capabilty {1}'.format(
                mode, capability))

            self.delete_request(url)

        logger.info('Deleted permission for {0} {1} item {2}'.format(
            rule.grantee.permissions_grantee_type,
            rule.grantee.id,
            resource.id))

    def populate(self, item):
        if not item.id:
            error = "Server item is missing ID. Item must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def permission_fetcher():
            return self._get_default_permissions(item)

        item._set_permissions(permission_fetcher)
        logger.info('Populated permissions for item (ID: {0})'.format(item.id))

    def _get_default_permissions(self, item, template_type, req_options=None):
        url = "{0}/{1}/default-permissions/{2}".format(self.owner_baseurl(), item.id, template_type)
        server_response = self.get_request(url, req_options)
        permissions = ExplicitPermissions.from_response(server_response.content,
                                                        self.parent_srv.namespace)

        return permissions
