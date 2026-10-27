"""
E2E tests for Workload Identity Federation (WIF) admin REST API.

Covers the bare-body wire shape that unit tests cannot: `enable()`,
`update()`, and `create_connector()` send bare XML roots (no `<tsRequest>`
envelope) because the admin controller binds `@RequestBody <SpecificType>`
rather than `@RequestBody TsRequest`. If the server is later aligned to its
published 3.30 schema (which nests these elements under `tsRequest`),
`enable()` / `create_connector()` would start returning HTTP 400 and
`update()` would silently become a no-op — mocked unit tests cannot catch
either regression.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite \\
    TABLEAU_TOKEN_NAME=... TABLEAU_TOKEN=... \\
    pytest test_e2e/test_auth_federation.py -v

Requires:
    * Tableau Server 2026.3+ (REST API 3.30+).
    * The `WorkloadIdentityFederation` feature flag enabled for the site.
    * The signed-in user to have the Site Administrator role.
    * WIF currently NOT enabled on the site — the test refuses to run if
      WIF is already enabled, to avoid destroying an existing configuration.
"""

import pytest

import tableauserverclient as TSC
from tableauserverclient import ServerResponseError

pytestmark = pytest.mark.e2e

TEST_CONNECTOR_CLASS = "bigquery"
TEST_AUDIENCE = (
    "//iam.googleapis.com/projects/0/locations/global/workloadIdentityPools/" "tsc-e2e-pool/providers/tsc-e2e-provider"
)


@pytest.fixture(scope="module")
def wif_site(server):
    """Guard against clobbering a live WIF config, then yield the server.

    Teardown deletes the entire WIF config (keys + connectors) so the site
    is left in the pre-test state. Fails loudly if the feature flag is off
    (403) or if WIF is already enabled, rather than silently destroying
    production state.
    """
    try:
        config = server.auth_federation.get()
    except ServerResponseError as exc:
        if getattr(exc, "code", None) == "403" or "403" in str(exc):
            pytest.skip("WIF feature flag not enabled for this site")
        raise

    if config.enabled:
        pytest.skip(
            "WIF is already enabled on this site — refusing to run destructive E2E. "
            "Point TABLEAU_SITE at a site where WIF has not been enabled."
        )

    yield server

    server.auth_federation.delete()


def test_wif_round_trip_bare_body_wire_contract(wif_site):
    """End-to-end round-trip exercising every method.

    Primarily a wire-shape regression test for the three bare-body routes:
    PUT /auth-federation/admin, PATCH /auth-federation/admin, and
    POST /auth-federation/admin/connectors. Each would surface as HTTP 400
    (enable, create_connector) or a silent no-op (update) if the server
    tightened its binding to the nested-under-<tsRequest> shape.
    """
    server = wif_site

    # --- enable: PUT with bare <authFederationAdmin enabled="true" tokenLifetimeSeconds=...>
    config = server.auth_federation.enable(token_lifetime_seconds=3600)
    assert config.enabled is True
    assert config.token_lifetime_seconds == 3600
    assert config.issuer_url is not None
    # First enable mints exactly one active key.
    assert config.active_key_id is not None
    initial_active_kid = config.active_key_id

    # --- update: PATCH with bare <authFederationAdmin tokenLifetimeSeconds=...>
    # (no `enabled` attribute — the server 400s if PATCH carries `enabled`).
    updated = server.auth_federation.update(token_lifetime_seconds=7200)
    assert updated.token_lifetime_seconds == 7200
    assert updated.enabled is True

    # --- create_connector: POST with bare <authFederationConnector connectorClass=... audience=...>
    new_connector = TSC.AuthFederationConnectorItem()
    new_connector.connector_class = TEST_CONNECTOR_CLASS
    new_connector.audience = TEST_AUDIENCE
    created = server.auth_federation.create_connector(new_connector)
    assert created.luid is not None
    assert created.connector_class == TEST_CONNECTOR_CLASS
    assert created.audience == TEST_AUDIENCE

    # --- list + get connector
    connectors = server.auth_federation.list_connectors()
    assert any(c.luid == created.luid for c in connectors)

    fetched = server.auth_federation.get_connector(created.luid)
    assert fetched.luid == created.luid
    assert fetched.connector_class == TEST_CONNECTOR_CLASS

    # --- key lifecycle: create → activate (swaps active) → deactivate → delete.
    # Per-site key limit is 3; one slot is held by the auto-minted key.
    new_key = server.auth_federation.create_key()
    assert new_key.kid is not None
    assert new_key.kid != initial_active_kid

    server.auth_federation.activate_key(new_key.kid)
    after_activate = server.auth_federation.get()
    assert after_activate.active_key_id == new_key.kid

    # The previously active key is now inactive and safe to delete.
    server.auth_federation.delete_key(initial_active_kid)

    # Deactivate the current active key, then delete it.
    server.auth_federation.deactivate_key(new_key.kid)
    server.auth_federation.delete_key(new_key.kid)

    # --- delete connector (idempotent on well-formed-but-unknown LUIDs)
    server.auth_federation.delete_connector(created.luid)
    remaining = server.auth_federation.list_connectors()
    assert all(c.luid != created.luid for c in remaining)
