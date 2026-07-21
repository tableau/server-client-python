import os
import pytest
import tableauserverclient as TSC


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: mark test as end-to-end (requires a real Tableau server)")
    config.addinivalue_line("markers", "e2e_admin: mark test as end-to-end requiring SiteAdmin credentials")


@pytest.fixture(scope="session")
def server():
    """
    Authenticated TSC server session for e2e tests.

    Required environment variables:
        TABLEAU_SERVER   — server URL, e.g. https://10ax.online.tableau.com
        TABLEAU_SITE     — site content URL
        TABLEAU_TOKEN    — personal access token value
        TABLEAU_TOKEN_NAME — personal access token name
    """
    url = os.environ.get("TABLEAU_SERVER")
    site = os.environ.get("TABLEAU_SITE", "")
    token = os.environ.get("TABLEAU_TOKEN")
    token_name = os.environ.get("TABLEAU_TOKEN_NAME")

    if not all([url, token, token_name]):
        pytest.skip("E2E tests require TABLEAU_SERVER, TABLEAU_TOKEN, and TABLEAU_TOKEN_NAME env vars")

    server = TSC.Server(url, use_server_version=True)
    auth = TSC.PersonalAccessTokenAuth(token_name, token, site)
    with server.auth.sign_in(auth):
        yield server


@pytest.fixture(scope="session")
def server_admin():
    """Authenticated TSC session using SiteAdmin credentials."""
    url = os.environ.get("TABLEAU_SERVER")
    site = os.environ.get("TABLEAU_SITE", "")
    token = os.environ.get("TABLEAU_SITEADMIN_TOKEN")
    token_name = os.environ.get("TABLEAU_SITEADMIN_TOKEN_NAME")

    if not all([url, token, token_name]):
        pytest.skip("Admin e2e tests require TABLEAU_SERVER, TABLEAU_SITEADMIN_TOKEN, and TABLEAU_SITEADMIN_TOKEN_NAME env vars")

    server = TSC.Server(url, use_server_version=True)
    auth = TSC.PersonalAccessTokenAuth(token_name, token, site)
    with server.auth.sign_in(auth):
        yield server


@pytest.fixture(scope="session")
def default_project(server):
    """Return a project to publish into, shared across all test modules.

    Uses TABLEAU_PROJECT env var if set (default: "Default"). Falls back to
    "Personal Work" then the first available project.
    """
    project_name = os.environ.get("TABLEAU_PROJECT", "Default")
    opts = TSC.RequestOptions()
    opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, project_name))
    projects, _ = server.projects.get(opts)
    if projects:
        return projects[0]

    for fallback in ("Personal Work",):
        opts2 = TSC.RequestOptions()
        opts2.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, fallback))
        fallback_projects, _ = server.projects.get(opts2)
        if fallback_projects:
            return fallback_projects[0]

    all_projects, _ = server.projects.get()
    if all_projects:
        return all_projects[0]

    pytest.skip(f"Project {project_name!r} not found — set TABLEAU_PROJECT env var")


@pytest.fixture(scope="session")
def project_id(default_project):
    """Convenience fixture returning just the project ID string."""
    return default_project.id
