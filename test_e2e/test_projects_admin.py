"""
E2E tests for Projects CRUD operations against a real Tableau server (SiteAdmin).

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite \
    TABLEAU_SITEADMIN_TOKEN_NAME=... TABLEAU_SITEADMIN_TOKEN=... \
    pytest test_e2e/test_projects_admin.py -v
"""
import uuid
import pytest
import tableauserverclient as TSC
from tableauserverclient.models.permissions_item import Permission, PermissionsRule
from tableauserverclient.models.reference_item import ResourceReference

pytestmark = pytest.mark.e2e_admin


def _name(base: str) -> str:
    return f"{base}-{uuid.uuid4().hex[:8]}"


def test_create_project(server_admin):
    """projects.create() returns a ProjectItem with the correct name."""
    project_name = _name("tsc-e2e-proj")
    project = TSC.ProjectItem(name=project_name)
    created = server_admin.projects.create(project)
    try:
        assert created.id is not None
        assert created.name == project_name
    finally:
        server_admin.projects.delete(created.id)


def test_get_includes_created_project(server_admin):
    """After create, filter(name=...) includes the new project's ID."""
    project_name = _name("tsc-e2e-proj-list")
    project = TSC.ProjectItem(name=project_name)
    created = server_admin.projects.create(project)
    try:
        matches = list(server_admin.projects.filter(name=project_name))
        assert any(p.id == created.id for p in matches), (
            f"Newly created project {created.id!r} not found in projects.filter(name={project_name!r}) result"
        )
    finally:
        server_admin.projects.delete(created.id)


def test_update_project_description(server_admin):
    """projects.update() with a new description persists on a subsequent get_by_id."""
    project = TSC.ProjectItem(name=_name("tsc-e2e-proj-update"))
    created = server_admin.projects.create(project)
    try:
        created.description = "updated description"
        updated = server_admin.projects.update(created)
        assert updated.description == "updated description"

        fetched = server_admin.projects.get_by_id(created.id)
        assert fetched.description == "updated description"
    finally:
        server_admin.projects.delete(created.id)


def test_create_child_project(server_admin):
    """Creating a project with parent_id set results in a child project with matching parent_id."""
    parent = TSC.ProjectItem(name=_name("tsc-e2e-parent"))
    created_parent = server_admin.projects.create(parent)
    created_child = None
    try:
        child = TSC.ProjectItem(name=_name("tsc-e2e-child"), parent_id=created_parent.id)
        created_child = server_admin.projects.create(child)
        assert created_child.parent_id == created_parent.id

        fetched_child = server_admin.projects.get_by_id(created_child.id)
        assert fetched_child.parent_id == created_parent.id
    finally:
        if created_child is not None:
            try:
                server_admin.projects.delete(created_child.id)
            except Exception:
                pass
        server_admin.projects.delete(created_parent.id)


def test_delete_projects(server_admin):
    """After deleting child then parent, neither appears in a subsequent filter."""
    parent_name = _name("tsc-e2e-del-parent")
    child_name = _name("tsc-e2e-del-child")
    parent = server_admin.projects.create(TSC.ProjectItem(name=parent_name))
    child = server_admin.projects.create(
        TSC.ProjectItem(name=child_name, parent_id=parent.id)
    )

    parent_id = parent.id
    child_id = child.id

    try:
        server_admin.projects.delete(child_id)
        server_admin.projects.delete(parent_id)

        remaining_parent = list(server_admin.projects.filter(name=parent_name))
        remaining_child = list(server_admin.projects.filter(name=child_name))

        assert not any(p.id == parent_id for p in remaining_parent), "Parent project was not deleted"
        assert not any(p.id == child_id for p in remaining_child), "Child project was not deleted"
    finally:
        try:
            server_admin.projects.delete(child_id)
        except Exception:
            pass
        try:
            server_admin.projects.delete(parent_id)
        except Exception:
            pass


def test_populate_workbook_default_permissions(server_admin):
    """populate_workbook_default_permissions() runs without error and the result is a list."""
    project = server_admin.projects.create(TSC.ProjectItem(name=_name("tsc-e2e-proj-perms")))
    try:
        server_admin.projects.populate_workbook_default_permissions(project)
        perms = project.default_workbook_permissions
        assert isinstance(perms, list)
    finally:
        server_admin.projects.delete(project.id)


def test_update_workbook_default_permissions(server_admin):
    """update_workbook_default_permissions() with a rule for All Users persists and is readable."""
    project = server_admin.projects.create(TSC.ProjectItem(name=_name("tsc-e2e-proj-update-perms")))
    try:
        all_users_groups = list(server_admin.groups.filter(name="All Users"))
        if not all_users_groups:
            pytest.skip("'All Users' group not found on this site")
        group = all_users_groups[0]

        grantee = ResourceReference(group.id, "group")
        rule = PermissionsRule(
            grantee=grantee,
            capabilities={Permission.Capability.Read: Permission.Mode.Allow},
        )

        updated_rules = server_admin.projects.update_workbook_default_permissions(project, [rule])
        assert isinstance(updated_rules, list)
        assert any(
            r.grantee.id == group.id
            and r.capabilities.get(Permission.Capability.Read) == Permission.Mode.Allow
            for r in updated_rules
        )
    finally:
        server_admin.projects.delete(project.id)
