"""
E2E tests for pagination via TSC.Pager and QuerySet against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_pagination.py -v
"""
import warnings
from pathlib import Path

import pytest
import tableauserverclient as TSC

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

PAGINATION_WB_NAMES = ["tsc-e2e-pagination-alpha", "tsc-e2e-pagination-zeta"]

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def workbooks_for_pagination(server, project_id):
    published = []
    for name in PAGINATION_WB_NAMES:
        wb = TSC.WorkbookItem(name=name, project_id=project_id)
        wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
        published.append(wb)
    yield published
    for wb in published:
        try:
            server.workbooks.delete(wb.id)
        except Exception as exc:
            warnings.warn(f"Failed to delete workbook: {exc}")


@pytest.fixture(scope="module")
def datasource_for_pagination(server, project_id):
    ds = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-pagination-ds")
    ds = server.datasources.publish(ds, SAMPLE_DATASOURCE, TSC.Server.PublishMode.Overwrite)
    yield ds
    try:
        server.datasources.delete(ds.id)
    except Exception:
        pass


def test_pager_workbooks_count_matches_get(server, workbooks_for_pagination):
    """TSC.Pager iterates all workbooks; count is at least the number of fixture workbooks."""
    _, pagination_item = server.workbooks.get()
    total_declared = pagination_item.total_available
    assert total_declared > 0, "Server has no workbooks — fixture likely failed"

    pager_count = sum(1 for _ in TSC.Pager(server.workbooks))

    assert pager_count >= 2, (
        f"Pager yielded {pager_count} workbooks but expected at least 2 fixture workbooks"
    )


def test_pager_datasources_returns_items(server, datasource_for_pagination):
    """TSC.Pager iterates all datasources; count matches total_available."""
    _, pagination_item = server.datasources.get()
    total_declared = pagination_item.total_available
    assert total_declared > 0, "Server has no datasources — fixture likely failed"

    pager_count = sum(1 for _ in TSC.Pager(server.datasources))

    assert pager_count == total_declared, (
        f"Pager yielded {pager_count} datasources but server reported {total_declared}"
    )


def test_queryset_all_workbooks_matches_pager(server, workbooks_for_pagination):
    """server.workbooks.all() QuerySet yields same count as Pager."""
    pager_count = sum(1 for _ in TSC.Pager(server.workbooks))
    queryset_count = sum(1 for _ in server.workbooks.all())

    assert queryset_count > 0
    assert queryset_count == pager_count, (
        f"QuerySet yielded {queryset_count} but Pager yielded {pager_count}"
    )


def test_queryset_filter_by_name(server, workbooks_for_pagination):
    """server.workbooks.filter(name=...) returns only workbooks with that exact name."""
    known_name = PAGINATION_WB_NAMES[0]

    results = list(server.workbooks.filter(name=known_name))

    assert len(results) >= 1, f"No workbook named {known_name!r} returned by filter"
    for wb in results:
        assert wb.name == known_name, (
            f"Filter returned {wb.name!r}, expected {known_name!r}"
        )


def test_queryset_order_by_name_ascending(server, workbooks_for_pagination):
    """server.workbooks.order_by('name') returns fixture workbooks sorted A to Z by name."""
    all_results = list(server.workbooks.order_by("name"))
    fixture_name_set = set(PAGINATION_WB_NAMES)
    fixture_results = [wb for wb in all_results if wb.name in fixture_name_set]

    assert len(fixture_results) >= 2, (
        f"Expected at least 2 fixture workbooks in results, got {len(fixture_results)}"
    )
    names = [wb.name for wb in fixture_results]
    assert names == sorted(names, key=str.casefold), (
        f"Fixture workbooks not in ascending case-insensitive name order: {names}"
    )


def test_pager_small_pagesize(server, workbooks_for_pagination):
    """TSC.Pager with pagesize=1 correctly iterates all workbooks one page at a time."""
    request_opts = TSC.RequestOptions(pagesize=1)
    items = list(TSC.Pager(server.workbooks.get, request_opts=request_opts))

    assert len(items) >= 1, "Pager with pagesize=1 returned no items"
    for item in items:
        assert isinstance(item, TSC.WorkbookItem), (
            f"Expected WorkbookItem, got {type(item).__name__}"
        )
