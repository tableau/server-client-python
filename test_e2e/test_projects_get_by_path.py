"""
E2E tests for server.projects.get_by_path() against a real Tableau server.

Run publisher-level tests with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite \
    TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_projects_get_by_path.py -m e2e -v

Run admin-level tests additionally with:
    TABLEAU_SITEADMIN_TOKEN=... TABLEAU_SITEADMIN_TOKEN_NAME=... \
    pytest test_e2e/test_projects_get_by_path.py -m e2e_admin -v
"""
import pytest
import tableauserverclient as TSC

# pytestmark is intentionally NOT set at module level because this file mixes
# @pytest.mark.e2e (publisher credentials) and @pytest.mark.e2e_admin (site-admin
# credentials) tests.  A module-wide pytestmark would apply the same mark to every
# test, making it impossible to skip one class independently of the other.


def test_get_by_path_raises_for_empty_or_root_path():
    """get_by_path must raise ValueError for '' or '/' (both normalise to empty)."""
    server = TSC.Server("https://example.com")
    with pytest.raises(ValueError):
        server.projects.get_by_path("")
    with pytest.raises(ValueError):
        server.projects.get_by_path("/")


@pytest.mark.e2e
def test_get_default_project_by_path(server, default_project):
    """get_by_path('Default') returns the Default top-level project."""
    result = server.projects.get_by_path("Default")
    assert result is not None, "Expected to find 'Default' project, got None"
    assert result.id == default_project.id
    assert result.name.lower() == "default"


@pytest.mark.e2e
def test_get_by_path_strips_leading_trailing_slashes(server, default_project):
    """get_by_path('/Default/') must resolve to the same project as 'Default'."""
    result = server.projects.get_by_path("/Default/")
    assert result is not None, "Expected to find project via path '/Default/', got None"
    assert result.id == default_project.id, (
        f"Path '/Default/' resolved to project {result.id!r} "
        f"but expected {default_project.id!r}"
    )


@pytest.mark.e2e
def test_get_by_path_returns_none_for_missing_project(server):
    """get_by_path for a non-existent project must return None, not raise."""
    result = server.projects.get_by_path("DoesNotExistAtAll999")
    assert result is None, f"Expected None for missing project, got {result!r}"


@pytest.mark.e2e_admin
def test_get_child_project_by_path(server_admin):
    """get_by_path('Parent/Child') resolves to the correct nested child project."""
    parent_name = "tsc-e2e-gbp-parent"
    child_name = "tsc-e2e-gbp-child"
    parent = None
    child = None
    try:
        parent = server_admin.projects.create(TSC.ProjectItem(name=parent_name))
        child = server_admin.projects.create(
            TSC.ProjectItem(name=child_name, parent_id=parent.id)
        )

        result = server_admin.projects.get_by_path(f"{parent_name}/{child_name}")

        assert result is not None, (
            f"Expected to find child project at path '{parent_name}/{child_name}', got None"
        )
        assert result.id == child.id, (
            f"get_by_path returned project {result.id!r} but expected child {child.id!r}"
        )
        assert result.parent_id == parent.id, (
            f"Child project parent_id {result.parent_id!r} does not match parent {parent.id!r}"
        )
    finally:
        if child is not None:
            server_admin.projects.delete(child.id)
        if parent is not None:
            server_admin.projects.delete(parent.id)


@pytest.mark.e2e_admin
def test_get_by_path_with_spaces_in_name(server_admin):
    """get_by_path works correctly when the project name contains spaces."""
    project_name = "TSC E2E Spaced Project"
    project = None
    try:
        project = server_admin.projects.create(TSC.ProjectItem(name=project_name))
        result = server_admin.projects.get_by_path(project_name)
        assert result is not None, (
            f"Expected to find project '{project_name}' by path, got None"
        )
        assert result.name == project_name, (
            f"Project name mismatch: expected {project_name!r}, got {result.name!r}"
        )
        assert result.id == project.id
    finally:
        if project is not None:
            server_admin.projects.delete(project.id)
