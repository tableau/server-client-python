"""
E2E tests for favorites operations against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_favorites.py -v
"""

from pathlib import Path

import pytest
import tableauserverclient as TSC
from tableauserverclient.models import Resource

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def workbook(server, project_id):
    wb = TSC.WorkbookItem(name="tsc-e2e-favorites-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        yield wb
    finally:
        server.workbooks.delete(wb.id)


@pytest.fixture(scope="module")
def datasource(server, project_id):
    ds = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-favorites-ds")
    ds = server.datasources.publish(ds, SAMPLE_DATASOURCE, TSC.Server.PublishMode.Overwrite)
    try:
        yield ds
    finally:
        server.datasources.delete(ds.id)


def test_favorites_workbook(server, workbook):
    """A workbook can be added to and removed from favorites."""
    user = TSC.UserItem()
    user.id = server.user_id
    server.favorites.add_favorite(user, Resource.Workbook, workbook)
    server.favorites.get(user)
    try:
        assert any(f.id == workbook.id for f in user.favorites.get("workbooks", []))
    finally:
        server.favorites.delete_favorite_workbook(user, workbook)


def test_favorites_view(server, workbook):
    """A view can be added to and removed from favorites."""
    server.workbooks.populate_views(workbook)
    view = workbook.views[0]
    user = TSC.UserItem()
    user.id = server.user_id
    server.favorites.add_favorite_view(user, view)
    server.favorites.get(user)
    try:
        assert any(f.id == view.id for f in user.favorites.get("views", []))
    finally:
        server.favorites.delete_favorite_view(user, view)


def test_favorites_datasource(server, datasource):
    """A datasource can be added to and removed from favorites."""
    user = TSC.UserItem()
    user.id = server.user_id
    server.favorites.add_favorite_datasource(user, datasource)
    server.favorites.get(user)
    try:
        assert any(f.id == datasource.id for f in user.favorites.get("datasources", []))
    finally:
        server.favorites.delete_favorite_datasource(user, datasource)
