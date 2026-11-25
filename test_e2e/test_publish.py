"""
E2E test for publishing a workbook with the bridge_refresh_embedded_files opt-in.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_publish.py -v

This checks that the server accepts the publish request with the attribute. The server does not return
the value, so the test cannot check that it was stored.
"""

import os
from pathlib import Path

import pytest
import tableauserverclient as TSC

SAMPLE_WORKBOOK = Path(__file__).parent / "assets" / "WorkbookWithExcelExtract.twbx"

pytestmark = pytest.mark.e2e


@pytest.mark.parametrize("opt_in", [True, False])
def test_publish_with_bridge_refresh_embedded_files(server, opt_in):
    """The server must accept a publish request that carries bridgeRefreshEmbeddedFiles."""
    project_name = os.environ.get("TABLEAU_PROJECT", "Default")
    opts = TSC.RequestOptions()
    opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, project_name))
    projects, _ = server.projects.get(opts)
    if not projects:
        pytest.skip(f"Project {project_name!r} not found — set TABLEAU_PROJECT env var")

    wb_item = TSC.WorkbookItem(
        name=f"tsc-e2e-bridge-refresh-{str(opt_in).lower()}",
        project_id=projects[0].id,
        bridge_refresh_embedded_files=opt_in,
    )
    published = server.workbooks.publish(wb_item, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        assert published.id
        # Print the workbook id for debugging (pytest -s).
        print(f"published workbook_luid={published.id} bridge_refresh_embedded_files={opt_in}")
    finally:
        server.workbooks.delete(published.id)
