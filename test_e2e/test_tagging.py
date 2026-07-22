"""
E2E tests for tag operations against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_tagging.py -v
"""
from pathlib import Path

import pytest
import tableauserverclient as TSC

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def workbook(server, project_id):
    """Publish a workbook for tagging tests, clean up after."""
    wb = TSC.WorkbookItem(name="tsc-e2e-tagging-test", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    yield wb
    server.workbooks.delete(wb.id)


@pytest.fixture(scope="module")
def datasource(server, project_id):
    """Publish a datasource for tagging tests, clean up after."""
    if not SAMPLE_DATASOURCE.exists():
        pytest.skip(f"Datasource asset not found: {SAMPLE_DATASOURCE}")

    ds = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-tagging-test-ds")
    ds = server.datasources.publish(ds, SAMPLE_DATASOURCE, TSC.Server.PublishMode.Overwrite)
    yield ds
    server.datasources.delete(ds.id)


def test_multiple_tags_including_spaced(server, workbook):
    """Adding multiple tags where one has a space should all round-trip correctly."""
    tags = ["simple", "Yearly Sales", "another tag"]
    server.workbooks.add_tags(workbook, tags)
    updated = server.workbooks.get_by_id(workbook.id)
    try:
        for tag in tags:
            assert tag in updated.tags, f"Tag '{tag}' not found in {updated.tags!r}"
    finally:
        server.workbooks.delete_tags(workbook, tags)


def test_add_tag_with_space(server, workbook):
    """add_tags with a space-containing tag round-trips as a single tag (not split)."""
    tag = "Yearly Sales"
    server.workbooks.add_tags(workbook, tag)
    updated = server.workbooks.get_by_id(workbook.id)
    try:
        assert tag in updated.tags, (
            f"Tag {tag!r} not found in {updated.tags!r} — was it split on the space?"
        )
        assert '"Yearly Sales"' not in updated.tags, (
            "Tag was stored with literal surrounding quotes — double-quoting leaked into the label"
        )
        assert "Yearly" not in updated.tags, "Tag was split — 'Yearly' must not be a standalone tag"
        assert "Sales" not in updated.tags, "Tag was split — 'Sales' must not be a standalone tag"
    finally:
        server.workbooks.delete_tags(workbook, tag)


def test_add_tag_with_comma(server, workbook):
    """add_tags with a comma-containing tag is stored as exactly one tag, not split on the comma."""
    tag = "Sales, Revenue"
    server.workbooks.add_tags(workbook, tag)
    updated = server.workbooks.get_by_id(workbook.id)
    try:
        assert tag in updated.tags, (
            f"Tag {tag!r} not found in {updated.tags!r} — was it split on the comma?"
        )
        assert "Sales" not in updated.tags, "Tag was split — 'Sales' must not be a standalone tag"
        assert "Revenue" not in updated.tags, "Tag was split — 'Revenue' must not be a standalone tag"
    finally:
        server.workbooks.delete_tags(workbook, tag)


def test_delete_tag_with_space(server, workbook):
    """A space-containing tag added then deleted must no longer appear on the workbook."""
    tag = "Yearly Sales"
    server.workbooks.add_tags(workbook, tag)
    try:
        after_add = server.workbooks.get_by_id(workbook.id)
        assert tag in after_add.tags, (
            f"Precondition failed: tag {tag!r} not in {after_add.tags!r} after add_tags"
        )
        server.workbooks.delete_tags(workbook, tag)
        after_delete = server.workbooks.get_by_id(workbook.id)
        assert tag not in after_delete.tags, (
            f"Tag {tag!r} still present in {after_delete.tags!r} after delete_tags — "
            "delete may have failed to match the space-quoting used at write time"
        )
    finally:
        try:
            server.workbooks.delete_tags(workbook, tag)
        except Exception:
            pass


def test_delete_tag_with_comma(server, workbook):
    """A comma-containing tag added then deleted must no longer appear on the workbook."""
    tag = "Sales, Revenue"
    server.workbooks.add_tags(workbook, tag)
    try:
        after_add = server.workbooks.get_by_id(workbook.id)
        assert tag in after_add.tags, (
            f"Precondition failed: tag {tag!r} not in {after_add.tags!r} after add_tags"
        )
        server.workbooks.delete_tags(workbook, tag)
        after_delete = server.workbooks.get_by_id(workbook.id)
        assert tag not in after_delete.tags, (
            f"Tag {tag!r} still present in {after_delete.tags!r} after delete_tags — "
            "delete may have failed to URL-encode the comma in the delete path"
        )
    finally:
        try:
            server.workbooks.delete_tags(workbook, tag)
        except Exception:
            pass


def test_add_space_tag_to_datasource(server, datasource):
    """A space-containing tag round-trips correctly when applied to a datasource (not a workbook)."""
    tag = "Yearly Sales"
    server.datasources.add_tags(datasource, tag)
    updated = server.datasources.get_by_id(datasource.id)
    try:
        assert tag in updated.tags, (
            f"Tag {tag!r} not found in datasource tags {updated.tags!r} — was it split on the space?"
        )
        assert '"Yearly Sales"' not in updated.tags, (
            "Tag was stored with literal surrounding quotes on the datasource"
        )
        assert "Yearly" not in updated.tags, "Tag was split — 'Yearly' must not be a standalone datasource tag"
        assert "Sales" not in updated.tags, "Tag was split — 'Sales' must not be a standalone datasource tag"
    finally:
        server.datasources.delete_tags(datasource, tag)
