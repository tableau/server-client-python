import os
import pytest
import tableauserverclient as TSC


def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: mark test as end-to-end (requires a real Tableau server)")


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
