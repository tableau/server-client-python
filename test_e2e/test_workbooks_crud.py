"""
E2E tests for workbook CRUD operations against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_workbooks_crud.py -v
"""
import io
from pathlib import Path

import pytest
import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import ServerResponseError

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def published_workbook(server, project_id):
    """Publish WorkbookWithoutExtract.twbx once for all CRUD tests; delete after module."""
    wb = TSC.WorkbookItem(name="tsc-e2e-crud-test", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    yield wb
    server.workbooks.delete(wb.id)


def test_workbook_publish_returns_item_with_id(published_workbook):
    """publish() returns a WorkbookItem with a server-assigned ID and the expected name."""
    assert published_workbook.id is not None
    assert published_workbook.name == "tsc-e2e-crud-test"


def test_workbook_get_lists_published_workbook(server, published_workbook):
    """workbooks.filter() with a name filter returns the published workbook."""
    results = list(server.workbooks.filter(name="tsc-e2e-crud-test"))
    assert any(wb.id == published_workbook.id for wb in results), (
        f"Published workbook {published_workbook.id!r} not found in filter results: "
        f"{[wb.id for wb in results]}"
    )


def test_workbook_get_by_id_returns_correct_item(server, published_workbook):
    """get_by_id() returns the exact workbook that was published."""
    fetched = server.workbooks.get_by_id(published_workbook.id)
    assert fetched.id == published_workbook.id
    assert fetched.name == published_workbook.name


def test_workbook_update_description_persists(server, published_workbook):
    """update() persists a changed description on the server."""
    new_description = "tsc-e2e updated description"
    fresh = server.workbooks.get_by_id(published_workbook.id)
    fresh.description = new_description
    server.workbooks.update(fresh)
    fetched = server.workbooks.get_by_id(published_workbook.id)
    assert fetched.description == new_description


def test_workbook_populate_views_returns_at_least_one_view(server, published_workbook):
    """populate_views() sets workbook_item.views with at least one ViewItem."""
    server.workbooks.populate_views(published_workbook)
    assert published_workbook.views is not None
    assert len(published_workbook.views) >= 1


def test_workbook_populate_connections_does_not_raise(server, published_workbook):
    """populate_connections() sets the connections attribute without error."""
    server.workbooks.populate_connections(published_workbook)
    assert published_workbook.connections is not None


def test_workbook_download_returns_nonempty_bytes(server, published_workbook):
    """download() writes a non-empty file into a BytesIO buffer."""
    buffer = io.BytesIO()
    server.workbooks.download(published_workbook.id, filepath=buffer)
    assert buffer.tell() > 0


def test_workbook_delete_removes_workbook(server, project_id):
    """delete() removes a workbook; get_by_id afterwards raises ServerResponseError."""
    wb = TSC.WorkbookItem(name="tsc-e2e-delete-test", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        server.workbooks.delete(wb.id)
        with pytest.raises(ServerResponseError):
            server.workbooks.get_by_id(wb.id)
    finally:
        try:
            server.workbooks.delete(wb.id)
        except ServerResponseError:
            pass
