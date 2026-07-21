"""
E2E tests for workbook and view permission operations against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite \
    TABLEAU_SITEADMIN_TOKEN_NAME=... TABLEAU_SITEADMIN_TOKEN=... \
    pytest test_e2e/test_workbook_permissions.py -v
"""
import os
from pathlib import Path

import pytest
import tableauserverclient as TSC

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"

pytestmark = pytest.mark.e2e_admin


@pytest.fixture(scope="module")
def workbook_and_user(server_admin):
    """Publish a workbook and create a test user for permissions tests; clean up after.

    Uses TABLEAU_PROJECT env var if set, otherwise falls back to 'Default'.
    """
    project_name = os.environ.get("TABLEAU_PROJECT", "Default")
    opts = TSC.RequestOptions()
    opts.filter.add(
        TSC.Filter(
            TSC.RequestOptions.Field.Name,
            TSC.RequestOptions.Operator.Equals,
            project_name,
        )
    )
    projects, _ = server_admin.projects.get(opts)
    if not projects:
        pytest.skip(f"Project {project_name!r} not found — set TABLEAU_PROJECT env var")
    project = projects[0]

    wb = TSC.WorkbookItem(name="tsc-e2e-permissions-test", project_id=project.id)
    wb = server_admin.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)

    try:
        user = TSC.UserItem("tsc-e2e-perm-testuser", TSC.UserItem.Roles.Viewer)
        user = server_admin.users.add(user)
    except Exception:
        server_admin.workbooks.delete(wb.id)
        raise

    yield wb, user

    # Teardown — always attempt both deletes
    try:
        server_admin.workbooks.delete(wb.id)
    finally:
        server_admin.users.remove(user.id)


def test_populate_permissions_returns_list(server_admin, workbook_and_user):
    """populate_permissions populates workbook.permissions as a list of PermissionsRule objects."""
    workbook, _ = workbook_and_user
    server_admin.workbooks.populate_permissions(workbook)
    assert workbook.permissions is not None
    assert isinstance(workbook.permissions, list)
    for rule in workbook.permissions:
        assert isinstance(rule, TSC.PermissionsRule)
        assert isinstance(rule.capabilities, dict)
        assert rule.grantee is not None


def test_update_permissions_appears_on_populate(server_admin, workbook_and_user):
    """A permission granted via update_permissions is visible after populate_permissions."""
    workbook, user = workbook_and_user

    grantee = TSC.UserItem.as_reference(user.id)
    new_rule = TSC.PermissionsRule(
        grantee,
        {TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow},
    )

    try:
        server_admin.workbooks.update_permissions(workbook, [new_rule])

        # Re-populate to get fresh permissions from the server
        server_admin.workbooks.populate_permissions(workbook)
        user_rules = [
            r for r in workbook.permissions
            if r.grantee.id == user.id and r.grantee.tag_name == "user"
        ]
        assert len(user_rules) == 1
        assert (
            user_rules[0].capabilities.get(TSC.Permission.Capability.Read)
            == TSC.Permission.Mode.Allow
        )
    finally:
        # Clean up: build the delete rule directly to avoid masking the original exception
        delete_rule = TSC.PermissionsRule(
            grantee,
            {TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow},
        )
        server_admin.workbooks.delete_permission(workbook, delete_rule)


def test_view_populate_permissions_returns_list(server_admin, workbook_and_user):
    """populate_permissions on a view returns a list of PermissionsRule objects."""
    workbook, _ = workbook_and_user

    server_admin.workbooks.populate_views(workbook)
    assert workbook.views, "Workbook has no views — cannot test view permissions"
    view = workbook.views[0]

    server_admin.views.populate_permissions(view)
    assert view.permissions is not None
    assert isinstance(view.permissions, list)
    for rule in view.permissions:
        assert isinstance(rule, TSC.PermissionsRule)


def test_delete_permission_removes_rule(server_admin, workbook_and_user):
    """A permission deleted via delete_permission is no longer returned by populate_permissions."""
    workbook, user = workbook_and_user

    grantee = TSC.UserItem.as_reference(user.id)
    new_rule = TSC.PermissionsRule(
        grantee,
        {TSC.Permission.Capability.ExportImage: TSC.Permission.Mode.Allow},
    )

    try:
        # Grant permission
        server_admin.workbooks.update_permissions(workbook, [new_rule])

        # Confirm it was granted
        server_admin.workbooks.populate_permissions(workbook)
        user_rules = [
            r for r in workbook.permissions
            if r.grantee.id == user.id and r.grantee.tag_name == "user"
        ]
        assert any(
            r.capabilities.get(TSC.Permission.Capability.ExportImage) == TSC.Permission.Mode.Allow
            for r in user_rules
        ), "ExportImage/Allow rule not found after update_permissions"

        # Delete the permission rule
        for rule in user_rules:
            server_admin.workbooks.delete_permission(workbook, rule)

        # Confirm it is gone
        server_admin.workbooks.populate_permissions(workbook)
        remaining_user_rules = [
            r for r in workbook.permissions
            if r.grantee.id == user.id and r.grantee.tag_name == "user"
        ]
        assert not any(
            r.capabilities.get(TSC.Permission.Capability.ExportImage) == TSC.Permission.Mode.Allow
            for r in remaining_user_rules
        ), "ExportImage/Allow rule still present after delete_permission"
    finally:
        # Ensure the granted permission is cleaned up even if assertions fail
        delete_rule = TSC.PermissionsRule(
            grantee,
            {TSC.Permission.Capability.ExportImage: TSC.Permission.Mode.Allow},
        )
        try:
            server_admin.workbooks.delete_permission(workbook, delete_rule)
        except Exception:
            pass  # Rule may already be deleted by the test body
