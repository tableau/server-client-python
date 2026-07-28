"""
E2E tests for view export operations (PDF, PNG, CSV) against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_views_export.py -v
"""

from pathlib import Path

import pytest
import tableauserverclient as TSC

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def workbook_with_view(server, project_id):
    """Publish a workbook for export tests, clean up after."""
    wb = TSC.WorkbookItem(name="tsc-e2e-views-export-test", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        yield wb
    finally:
        server.workbooks.delete(wb.id)


@pytest.fixture(scope="module")
def a_view(server, workbook_with_view):
    """Return the first view from the published workbook."""
    server.workbooks.populate_views(workbook_with_view)
    views = workbook_with_view.views
    if not views:
        pytest.fail("Published workbook has no views")
    return views[0]


def test_views_get_returns_views(server, workbook_with_view):
    """server.views.get() returns at least one view after a workbook is published."""
    all_views, pagination = server.views.get()
    assert pagination.total_available >= 1
    assert len(all_views) >= 1


def test_populate_pdf_default_options(server, a_view):
    """populate_pdf() with no options produces non-empty PDF bytes."""
    server.views.populate_pdf(a_view)
    pdf_bytes = a_view.pdf
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF", "Response does not have PDF magic bytes"


def test_populate_pdf_with_page_options(server, a_view):
    """populate_pdf() with A4/Landscape options produces non-empty PDF bytes."""
    opts = TSC.PDFRequestOptions(
        page_type=TSC.PDFRequestOptions.PageType.A4,
        orientation=TSC.PDFRequestOptions.Orientation.Landscape,
    )
    server.views.populate_pdf(a_view, opts)
    pdf_bytes = a_view.pdf
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF", "Response does not have PDF magic bytes"


def test_populate_image_default_options(server, a_view):
    """populate_image() with no options produces non-empty PNG bytes."""
    server.views.populate_image(a_view)
    image_bytes = a_view.image
    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
    assert image_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Response does not have PNG magic bytes"


def test_populate_image_high_resolution(server, a_view):
    """populate_image() with high-resolution option produces non-empty PNG bytes."""
    opts = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High)
    server.views.populate_image(a_view, opts)
    image_bytes = a_view.image
    assert isinstance(image_bytes, bytes)
    assert len(image_bytes) > 0
    assert image_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Response does not have PNG magic bytes"


def test_populate_csv(server, a_view):
    """populate_csv() produces non-empty CSV bytes."""
    server.views.populate_csv(a_view)
    csv_bytes = b"".join(a_view.csv)
    assert isinstance(csv_bytes, bytes)
    assert len(csv_bytes) > 0
