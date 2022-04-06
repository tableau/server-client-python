import logging

from .endpoint import Endpoint
from .exceptions import MissingRequiredFieldError
from .. import RequestFactory
from ...models import PermissionsRule

logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Callable, List, Optional, Sequence, Union

if TYPE_CHECKING:
    from ...models import (
        DatasourceItem,
        FlowItem,
        ProjectItem,
        ViewItem,
        WorkbookItem,
    )

    from ..server import Server
    from ..request_options import RequestOptions

    TableauItem = Union[DatasourceItem, FlowItem, ProjectItem, ViewItem, WorkbookItem]


class _DefaultPermissionsEndpoint(Endpoint):
    """Adds default-permission model to another endpoint

    Tableau default-permissions model applies only to databases and projects
    and then takes an object type in the uri to set the defaults.
    This class is meant to be instantated inside a parent endpoint which
    has these supported endpoints
    """

    def __init__(self, parent_srv: "Server", owner_baseurl: Callable[[], str]) -> None:
        super(_DefaultPermissionsEndpoint, self).__init__(parent_srv)

        # owner_baseurl is the baseurl of the parent.  The MUST be a lambda
        # since we don't know the full site URL until we sign in.  If
        # populated without, we will get a sign-in error
        self.owner_baseurl = owner_baseurl

    def update_default_permissions(
        self, resource: "TableauItem", permissions: Sequence[PermissionsRule], content_type: str
    ) -> List[PermissionsRule]:
        url = "{0}/{1}/default-permissions/{2}".format(self.owner_baseurl(), resource.id, content_type + "s")
        update_req = RequestFactory.Permission.add_req(permissions)
        response = self.put_request(url, update_req)
        permissions = PermissionsRule.from_response(response.content, self.parent_srv.namespace)
        logger.info("Updated permissions for resource {0}".format(resource.id))

        return permissions

    def delete_default_permission(self, resource: "TableauItem", rule: PermissionsRule, content_type: str) -> None:
        for capability, mode in rule.capabilities.items():
            # Made readability better but line is too long, will make this look better
            url = (
                "{baseurl}/{content_id}/default-permissions/"
                "{content_type}/{grantee_type}/{grantee_id}/{cap}/{mode}".format(
                    baseurl=self.owner_baseurl(),
                    content_id=resource.id,
                    content_type=content_type + "s",
                    grantee_type=rule.grantee.tag_name + "s",
                    grantee_id=rule.grantee.id,
                    cap=capability,
                    mode=mode,
                )
            )

            logger.debug("Removing {0} permission for capabilty {1}".format(mode, capability))

            self.delete_request(url)

        logger.info(
            "Deleted permission for {0} {1} item {2}".format(rule.grantee.tag_name, rule.grantee.id, resource.id)
        )

    def populate_default_permissions(self, item: "ProjectItem", content_type: str) -> None:
        if not item.id:
            error = "Server item is missing ID. Item must be retrieved from server first."
            raise MissingRequiredFieldError(error)

        def permission_fetcher() -> List[PermissionsRule]:
            return self._get_default_permissions(item, content_type)

        item._set_default_permissions(permission_fetcher, content_type)
        logger.info("Populated {0} permissions for item (ID: {1})".format(item.id, content_type))

    def _get_default_permissions(
        self, item: "TableauItem", content_type: str, req_options: Optional["RequestOptions"] = None
    ) -> List[PermissionsRule]:
        url = "{0}/{1}/default-permissions/{2}".format(self.owner_baseurl(), item.id, content_type + "s")
        server_response = self.get_request(url, req_options)
        permissions = PermissionsRule.from_response(server_response.content, self.parent_srv.namespace)

        return permissions
