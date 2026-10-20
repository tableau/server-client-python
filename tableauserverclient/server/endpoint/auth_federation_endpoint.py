from typing import Protocol, TYPE_CHECKING, Union

from tableauserverclient.models.auth_federation_item import (
    AuthFederationConnectorItem,
    AuthFederationItem,
    AuthFederationKeyItem,
)
from tableauserverclient.server.endpoint.endpoint import Endpoint, api
from tableauserverclient.server.request_factory import RequestFactory

if TYPE_CHECKING:
    from tableauserverclient.server.server import Server


class HasLuid(Protocol):
    @property
    def luid(self) -> str | None: ...


class HasKid(Protocol):
    @property
    def kid(self) -> str | None: ...


ConnectorIdentifier = Union[str, HasLuid]
KeyIdentifier = Union[str, HasKid]


class AuthFederation(Endpoint):
    """
    Workload Identity Federation (WIF) admin configuration for a Tableau Cloud
    site. Lets a site admin enable WIF, manage the signing keys that mint JWTs
    for cloud-provider federation, and register the connectors (BigQuery,
    Snowflake, ...) that each JWT is scoped to. Requires REST API version 3.30
    (Tableau Server 2026.3) or later.

    REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_auth_federation.htm
    """

    def __init__(self, server: "Server") -> None:
        self.parent_srv = server

    @property
    def baseurl(self) -> str:
        return f"{self.parent_srv.baseurl}/sites/{self.parent_srv.site_id}/auth-federation/admin"

    # -- Admin config --------------------------------------------------------

    @api(version="3.30")
    def get(self) -> AuthFederationItem:
        """
        Get the WIF admin config for the currently authenticated Tableau Cloud
        site. A site that has never enabled WIF returns a default item with
        enabled=False rather than raising a 404.

        Returns
        -------
        AuthFederationItem
        """
        response = self.get_request(self.baseurl)
        return AuthFederationItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def enable(self, config: AuthFederationItem) -> AuthFederationItem:
        """
        Enable WIF for the currently authenticated Tableau Cloud site. The
        operation is idempotent: calling enable on an already-enabled site
        returns the current config. The request body must set enabled=True;
        use delete() to turn WIF off.

        On first enable (not on subsequent idempotent calls), the server
        auto-generates one active signing key and populates
        ``active_key_id`` on the returned item, so a caller does not need
        to immediately ``create_key`` + ``activate_key``.

        Parameters
        ----------
        config : AuthFederationItem
            Must have enabled=True. ``token_lifetime_seconds`` is optional and
            applied if provided. All other fields on the item are ignored on
            enable (issuer_url and active_key_id are server-assigned).

        Returns
        -------
        AuthFederationItem
            The current WIF admin config.
        """
        if not config.enabled:
            raise ValueError("AuthFederation.enable requires config.enabled=True; use delete() to disable WIF.")
        req = RequestFactory.AuthFederation.enable_req(config)
        response = self.put_request(self.baseurl, req)
        return AuthFederationItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def update(self, config: AuthFederationItem) -> AuthFederationItem:
        """
        Merge-patch the mutable fields of the WIF admin config. Only
        ``token_lifetime_seconds`` is mutable; any other fields set on the
        item (``issuer_url``, ``active_key_id``, ``connectors``) are silently
        ignored by the server. ``enabled`` is also silently dropped on the
        wire — use ``enable()`` / ``delete()`` to change WIF state.

        Parameters
        ----------
        config : AuthFederationItem
            Patch document. Fields set to None are not sent.

        Returns
        -------
        AuthFederationItem
            The updated WIF admin config.
        """
        req = RequestFactory.AuthFederation.update_req(config)
        response = self.patch_request(self.baseurl, req)
        return AuthFederationItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def delete(self) -> None:
        """
        Delete the WIF admin config, all signing keys, and all connectors for
        the currently authenticated site. Any datasource or workbook connections
        on the site that reference a WIF connector will no longer be able to
        authenticate until WIF is re-enabled.
        """
        self.delete_request(self.baseurl)

    # -- Connectors ----------------------------------------------------------

    @api(version="3.30")
    def create_connector(self, connector: AuthFederationConnectorItem) -> AuthFederationConnectorItem:
        """
        Register a new WIF connector on the site. The server assigns the
        connector's LUID. Fails with 409 if a connector with the same
        connector_class already exists on the site.

        Parameters
        ----------
        connector : AuthFederationConnectorItem
            ``connector_class`` and ``audience`` are required.

        Returns
        -------
        AuthFederationConnectorItem
            The created connector, with the server-assigned ``luid`` populated.
        """
        url = f"{self.baseurl}/connectors"
        req = RequestFactory.AuthFederation.create_connector_req(connector)
        response = self.post_request(url, req)
        return AuthFederationConnectorItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def list_connectors(self) -> list[AuthFederationConnectorItem]:
        """
        List every WIF connector registered on the site. Returns an empty list
        if WIF is enabled but has no connectors. If WIF is not enabled on the
        site, the server returns HTTP 404 (surfaced as ``ServerResponseError``)
        — call ``enable()`` first.

        Returns
        -------
        list[AuthFederationConnectorItem]
        """
        url = f"{self.baseurl}/connectors"
        response = self.get_request(url)
        return AuthFederationConnectorItem.list_from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def get_connector(self, connector: ConnectorIdentifier) -> AuthFederationConnectorItem:
        """
        Get a single WIF connector by LUID.

        Parameters
        ----------
        connector : str | HasLuid
            The connector LUID, or an ``AuthFederationConnectorItem`` whose
            ``luid`` is set.

        Returns
        -------
        AuthFederationConnectorItem
        """
        target = getattr(connector, "luid", connector)
        url = f"{self.baseurl}/connectors/{target}"
        response = self.get_request(url)
        return AuthFederationConnectorItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def delete_connector(self, connector: ConnectorIdentifier) -> None:
        """
        Delete a WIF connector by LUID. Idempotent: returns normally even if
        the connector does not exist. Existing site connections that reference
        the removed connector are orphaned, not cascade-deleted.

        Parameters
        ----------
        connector : str | HasLuid
            The connector LUID, or an ``AuthFederationConnectorItem`` whose
            ``luid`` is set.
        """
        target = getattr(connector, "luid", connector)
        url = f"{self.baseurl}/connectors/{target}"
        self.delete_request(url)

    # -- Keys ----------------------------------------------------------------

    @api(version="3.30")
    def create_key(self) -> AuthFederationKeyItem:
        """
        Generate a new WIF signing key. Keys are created in the inactive state;
        use ``activate_key`` to promote one to the site's active signing key.
        Fails with 400 (``ServerResponseError``) if the site is already at the
        maximum number of keys.

        Returns
        -------
        AuthFederationKeyItem
            The created key's JWK metadata (``kid``, ``kty``, ``alg``, ``use``,
            ``n``, ``e``). The private key is never exposed by the REST API.
        """
        url = f"{self.baseurl}/keys"
        req = RequestFactory.Empty.empty_req()
        response = self.post_request(url, req)
        return AuthFederationKeyItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def activate_key(self, key: KeyIdentifier) -> None:
        """
        Promote the given key to the site's active signing key. Atomic:
        deactivates whichever key was previously active in the same operation.

        Parameters
        ----------
        key : str | HasKid
            The key ID (``kid``), or an ``AuthFederationKeyItem`` whose ``kid``
            is set.
        """
        target = getattr(key, "kid", key)
        url = f"{self.baseurl}/keys/{target}/activate"
        self.put_request(url)

    @api(version="3.30")
    def deactivate_key(self, key: KeyIdentifier) -> None:
        """
        Deactivate the given key. A deactivated key stays on the site (and in
        the public JWKS) so that already-issued JWTs can still be verified
        during their validity window, but no new JWTs will be signed with it.

        Parameters
        ----------
        key : str | HasKid
            The key ID (``kid``), or an ``AuthFederationKeyItem`` whose ``kid``
            is set.
        """
        target = getattr(key, "kid", key)
        url = f"{self.baseurl}/keys/{target}/deactivate"
        self.put_request(url)

    @api(version="3.30")
    def delete_key(self, key: KeyIdentifier) -> None:
        """
        Delete a WIF signing key. Fails with 400 if the key is active;
        deactivate it first.

        Parameters
        ----------
        key : str | HasKid
            The key ID (``kid``), or an ``AuthFederationKeyItem`` whose ``kid``
            is set.
        """
        target = getattr(key, "kid", key)
        url = f"{self.baseurl}/keys/{target}"
        self.delete_request(url)
