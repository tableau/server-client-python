"""
E2E tests for datasource CRUD operations against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_datasources_crud.py -v
"""

import os
import warnings
from pathlib import Path

import pytest
import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import ServerResponseError

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def datasource(server, project_id):
    """Publish a datasource for CRUD tests; clean up after."""
    ds_item = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-datasource-crud")
    ds_item = server.datasources.publish(ds_item, SAMPLE_DATASOURCE, TSC.Server.PublishMode.Overwrite)
    yield ds_item
    server.datasources.delete(ds_item.id)


def test_datasource_publish(server, datasource):
    """datasources.publish() returns a DatasourceItem with an id."""
    assert datasource.id is not None
    assert datasource.name == "tsc-e2e-datasource-crud"


def test_datasources_get(server, datasource):
    """datasources.get() with a name filter returns the published datasource."""
    opts = TSC.RequestOptions()
    opts.filter.add(
        TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "tsc-e2e-datasource-crud")
    )
    results, pagination = server.datasources.get(opts)
    assert len(results) >= 1
    assert any(ds.id == datasource.id for ds in results)


def test_datasources_get_by_id(server, datasource):
    """datasources.get_by_id() returns the correct DatasourceItem."""
    fetched = server.datasources.get_by_id(datasource.id)
    assert fetched.id == datasource.id
    assert fetched.name == datasource.name


def test_datasources_update_description(server, datasource):
    """datasources.update() persists a description change."""
    original_description = datasource.description
    datasource.description = "e2e-test description"
    server.datasources.update(datasource)
    fetched = server.datasources.get_by_id(datasource.id)
    try:
        assert fetched.description == "e2e-test description"
    finally:
        datasource.description = original_description
        server.datasources.update(datasource)


def test_datasources_populate_connections(server, datasource):
    """datasources.populate_connections() populates the connections list without error."""
    fetched = server.datasources.get_by_id(datasource.id)
    server.datasources.populate_connections(fetched)
    connections = fetched.connections
    assert isinstance(connections, list)


def test_datasources_add_tags(server, datasource):
    """datasources.add_tags() adds a tag that is visible via get_by_id()."""
    server.datasources.add_tags(datasource, ["e2e-test"])
    try:
        fetched = server.datasources.get_by_id(datasource.id)
        assert "e2e-test" in fetched.tags
    finally:
        server.datasources.delete_tags(datasource, ["e2e-test"])


def test_datasources_delete_tags(server, datasource):
    """datasources.delete_tags() removes a previously added tag."""
    server.datasources.add_tags(datasource, ["e2e-test-delete"])
    server.datasources.delete_tags(datasource, ["e2e-test-delete"])
    fetched = server.datasources.get_by_id(datasource.id)
    assert "e2e-test-delete" not in fetched.tags


def test_datasources_download(server, datasource, tmp_path):
    """datasources.download() writes a non-empty file."""
    result_path = server.datasources.download(datasource.id, filepath=str(tmp_path))
    assert os.path.isfile(result_path)
    assert os.path.getsize(result_path) > 0


def test_datasources_delete(server, project_id):
    """datasources.delete() removes a datasource; subsequent get_by_id raises ServerResponseError."""
    ds_item = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-datasource-delete")
    published = server.datasources.publish(ds_item, SAMPLE_DATASOURCE, TSC.Server.PublishMode.Overwrite)
    ds_id = published.id
    try:
        server.datasources.delete(ds_id)
        with pytest.raises(ServerResponseError):
            server.datasources.get_by_id(ds_id)
    finally:
        try:
            server.datasources.delete(ds_id)
        except Exception as exc:
            warnings.warn(f"Failed to delete datasource: {exc}")
