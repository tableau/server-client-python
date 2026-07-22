"""
E2E tests for the Metadata API (GraphQL) against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_metadata.py -v
"""
import pytest

pytestmark = pytest.mark.e2e


def test_metadata_query_published_datasources(server):
    """Metadata GraphQL API returns a valid response for publishedDatasourcesConnection."""
    result = server.metadata.query(
        """
        {
            publishedDatasourcesConnection(first: 5) {
                nodes {
                    luid
                    name
                }
            }
        }
        """
    )
    assert "data" in result
    assert "publishedDatasourcesConnection" in result["data"]
    nodes = result["data"]["publishedDatasourcesConnection"]["nodes"]
    assert isinstance(nodes, list)


def test_metadata_query_workbooks(server):
    """Metadata GraphQL API returns workbook nodes."""
    result = server.metadata.query(
        """
        {
            workbooksConnection(first: 5) {
                nodes {
                    luid
                    name
                }
            }
        }
        """
    )
    assert "data" in result
    assert "workbooksConnection" in result["data"]
