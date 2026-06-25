"""
E2E tests for tag operations against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_tagging.py -v
"""
import os
from pathlib import Path

import pytest
import tableauserverclient as TSC

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def workbook(server):
    """Publish a workbook for tagging tests, clean up after.

    Uses TABLEAU_PROJECT env var if set, otherwise falls back to the first
    project named 'Default' or 'Personal Work', then the first available project.
    """
    project_name = os.environ.get("TABLEAU_PROJECT", "Default")
    opts = TSC.RequestOptions()
    opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, project_name))
    projects, _ = server.projects.get(opts)
    if not projects:
        pytest.skip(f"Project {project_name!r} not found — set TABLEAU_PROJECT env var")
    project = projects[0]

    wb = TSC.WorkbookItem(name="tsc-e2e-tagging-test", project_id=project.id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    yield wb
    server.workbooks.delete(wb.id)


def test_tag_with_spaces_stored_as_single_tag(server, workbook):
    """A tag containing a space must be stored as one tag, not split on the space."""
    spaced_tag = "Yearly Sales"
    server.workbooks.add_tags(workbook, spaced_tag)
    updated = server.workbooks.get_by_id(workbook.id)
    try:
        assert spaced_tag in updated.tags, (
            f"Tag '{spaced_tag}' not found in {updated.tags!r} — was it split on the space?"
        )
        assert "Yearly" not in updated.tags, "Tag was incorrectly split — 'Yearly' should not be a separate tag"
        assert "Sales" not in updated.tags, "Tag was incorrectly split — 'Sales' should not be a separate tag"
    finally:
        server.workbooks.delete_tags(workbook, spaced_tag)


def test_tag_with_comma_stored_as_single_tag(server, workbook):
    """A tag containing a comma must be stored as one tag, not split on the comma."""
    comma_tag = "Sales,Marketing"
    server.workbooks.add_tags(workbook, comma_tag)
    updated = server.workbooks.get_by_id(workbook.id)
    try:
        assert comma_tag in updated.tags, (
            f"Tag '{comma_tag}' not found in {updated.tags!r} — was it split on the comma?"
        )
    finally:
        server.workbooks.delete_tags(workbook, comma_tag)


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
