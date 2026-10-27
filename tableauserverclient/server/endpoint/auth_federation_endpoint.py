import uuid
from typing import Protocol, TYPE_CHECKING

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


ConnectorIdentifier = str | HasLuid
KeyIdentifier = str | HasKid


def _coerce_uuid(target: object) -> str:
    """Validate ``target`` is a UUID and return its canonical string form.

    Guards every id-taking method against path injection: without this, a
    caller could pass ``"../../admin"`` and delete the entire WIF config via
    the key-delete route.
    """
    try:
        return str(uuid.UUID(str(target)))
    except (ValueError, AttributeError, TypeError) as e:
        raise ValueError(f"Invalid UUID: {target!r}") from e


class AuthFederation(Endpoint):
    """
    Workload Identity Federation (WIF) admin configuration for a Tableau Cloud
    / Tableau Server site. Lets a site admin enable WIF, manage the signing
    keys that mint JWTs for cloud-provider federation, and register the
    connectors (BigQuery, Snowflake, ...) that each JWT is scoped to. Requires
    REST API version 3.30 (Tableau Server 2026.3) or later.

    All methods require the WIF feature to be enabled on the site AND the
    caller to be a Site Administrator; the server returns HTTP 403
    (``ServerResponseError``) when either is missing — including on
    ``get()``, so a site admin on a site where WIF has not been turned on
    will see 403.

    Once WIF is available on the site, ``get()`` works immediately (returns
    a shell with ``enabled=False`` until the admin runs ``enable()``).
    ``update()`` and the four connector methods return HTTP 404 until
    ``enable()`` has run; ``delete()`` on a never-enabled site is a no-op.
    ``create_key()`` is not gated by ``enable()`` and will create an orphan
    key against the per-site key limit if called first;
    ``activate_key``/``deactivate_key``/``delete_key`` return HTTP 404 only
    if the ``kid`` does not exist on the site.

    The four key-management methods (``create_key``, ``activate_key``,
    ``deactivate_key``, ``delete_key``) are bound to ``OAuthScopes.NO_ACCESS``
    server-side, which only rejects OAuth-scope-restricted sessions
    (e.g. a connected-app JWT session) — the server returns HTTP 401,
    surfaced by TSC as ``FailedSignInError``. Password sessions and
    personal-access-token (PAT) sessions do not carry scopes and are
    accepted. The config and connector methods additionally accept the
    ``tableau:connectivity_auth_federation:*`` OAuth scopes.

    ``delete()`` permanently removes the config, every signing key, and every
    connector on the site; re-enabling with ``enable()`` starts from a clean
    slate — prior connectors and keys are not restored, and any existing
    datasource / workbook connections that reference WIF stay broken until
    each connector is re-created.
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
        Get the WIF admin config for the currently authenticated site. A site
        that has never enabled WIF returns a default item with
        ``enabled=False`` rather than raising a 404.

        Returns
        -------
        AuthFederationItem
        """
        response = self.get_request(self.baseurl)
        return AuthFederationItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def enable(self, token_lifetime_seconds: int | None = None) -> AuthFederationItem:
        """
        Enable WIF for the currently authenticated site. Idempotent: calling
        enable on an already-enabled site returns the current config.

        On first enable (not on subsequent idempotent calls), the server
        auto-generates one active signing key and populates ``active_key_id``
        on the returned item, so a caller does not need to immediately
        ``create_key`` + ``activate_key``.

        Parameters
        ----------
        token_lifetime_seconds : int | None
            Optional JWT lifetime in seconds. ``None`` leaves the server
            default in place (or, on an already-enabled site, keeps whatever
            lifetime is currently configured).

        Returns
        -------
        AuthFederationItem
            The current WIF admin config.
        """
        req = RequestFactory.AuthFederation.enable_req(token_lifetime_seconds=token_lifetime_seconds)
        response = self.put_request(self.baseurl, req)
        return AuthFederationItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def update(self, token_lifetime_seconds: int) -> AuthFederationItem:
        """
        Merge-patch the mutable fields of the WIF admin config. Only
        ``token_lifetime_seconds`` is mutable; ``enabled``, ``issuer_url``,
        ``active_key_id``, and ``connectors`` are not — use ``enable()`` /
        ``delete()`` to change WIF state and the connector / key endpoints
        to manage those resources. Returns HTTP 404 if WIF has never been
        enabled on the site.

        Parameters
        ----------
        token_lifetime_seconds : int
            New JWT lifetime in seconds. Required — there is nothing else to
            patch, so a call with no fields to change is not a meaningful
            operation.

        Returns
        -------
        AuthFederationItem
            The updated WIF admin config.
        """
        req = RequestFactory.AuthFederation.update_req(token_lifetime_seconds=token_lifetime_seconds)
        response = self.patch_request(self.baseurl, req)
        return AuthFederationItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def delete(self) -> None:
        """
        Delete the WIF admin config, every signing key, and every connector
        on the site. Any datasource or workbook connections that reference a
        WIF connector will no longer be able to authenticate until WIF is
        re-enabled; the removed connectors and keys are not restored.
        """
        self.delete_request(self.baseurl)

    # -- Connectors ----------------------------------------------------------

    @api(version="3.30")
    def create_connector(self, connector: AuthFederationConnectorItem) -> AuthFederationConnectorItem:
        """
        Register a new WIF connector on the site. The server assigns the
        connector's LUID. Fails with 409 if a connector with the same
        ``connector_class`` already exists on the site.

        Parameters
        ----------
        connector : AuthFederationConnectorItem
            ``connector_class`` and ``audience`` are required.
            ``connector_class`` must equal the Tableau connection class
            exactly — what ``ConnectionItem.connection_type`` reports for the
            connector (e.g. ``"bigquery"``, ``"snowflake"``). Class names
            are case-sensitive; use the exact lowercase class name of the
            connector.

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
        target = _coerce_uuid(getattr(connector, "luid", connector))
        url = f"{self.baseurl}/connectors/{target}"
        response = self.get_request(url)
        return AuthFederationConnectorItem.from_response(response.content, self.parent_srv.namespace)

    @api(version="3.30")
    def delete_connector(self, connector: ConnectorIdentifier) -> None:
        """
        Delete a WIF connector by LUID. Idempotent on an unknown but
        well-formed LUID (the server returns 204 even if no such connector
        exists) — but only when WIF is enabled on the site; otherwise the
        server returns a WIF-not-enabled error. Client-side UUID validation
        rejects a malformed id before any HTTP call.

        Existing site connections that reference the removed connector are
        orphaned, not cascade-deleted.

        Parameters
        ----------
        connector : str | HasLuid
            The connector LUID, or an ``AuthFederationConnectorItem`` whose
            ``luid`` is set.
        """
        target = _coerce_uuid(getattr(connector, "luid", connector))
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
        target = _coerce_uuid(getattr(key, "kid", key))
        url = f"{self.baseurl}/keys/{target}/activate"
        self.put_request(url)

    @api(version="3.30")
    def deactivate_key(self, key: KeyIdentifier) -> None:
        """
        Deactivate the given key. A deactivated key stays on the site (and in
        the public JWKS) so that already-issued JWTs can still be verified
        during their validity window, but no new JWTs will be signed with it.
        Deactivating the active key before another is activated leaves the
        site with no active key, and no new WIF tokens can be minted until
        a replacement is activated.

        Parameters
        ----------
        key : str | HasKid
            The key ID (``kid``), or an ``AuthFederationKeyItem`` whose ``kid``
            is set.
        """
        target = _coerce_uuid(getattr(key, "kid", key))
        url = f"{self.baseurl}/keys/{target}/deactivate"
        self.put_request(url)

    @api(version="3.30")
    def delete_key(self, key: KeyIdentifier) -> None:
        """
        Delete a WIF signing key. Fails with 400 if the key is active.

        Unlike ``deactivate_key``, which keeps the (now-inactive) key
        published in the site's JWKS so that already-issued JWTs can still
        be verified, ``delete_key`` removes the key from the JWKS entirely —
        any verifier that fetches the key set afterwards will reject still-
        unexpired tokens signed with it. For a safe rotation, keep the old
        key deactivated-but-published until every JWT it signed has expired
        (upper bound: the site's current ``token_lifetime_seconds``, default
        7200 s / 2 h), and only then delete it.

        Parameters
        ----------
        key : str | HasKid
            The key ID (``kid``), or an ``AuthFederationKeyItem`` whose ``kid``
            is set.
        """
        target = _coerce_uuid(getattr(key, "kid", key))
        url = f"{self.baseurl}/keys/{target}"
        self.delete_request(url)
