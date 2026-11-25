"""
E2E test for publishing a workbook with the bridge_refresh_embedded_files opt-in.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest -n0 test_e2e/test_publish.py -v

Use -n0 (no xdist). The repo's pytest config runs tests in parallel by default, and each worker signs in
with the same personal access token. A token allows one active session, so a parallel run fails with a 401.

This checks that the server accepts the publish request with the attribute. The server does not return
the value, so the test cannot check that it was stored.
"""

import os
import uuid
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
        name=f"tsc-e2e-bridge-refresh-{str(opt_in).lower()}-{uuid.uuid4().hex[:8]}",
        project_id=projects[0].id,
        bridge_refresh_embedded_files=opt_in,
    )
    published = server.workbooks.publish(wb_item, SAMPLE_WORKBOOK, TSC.Server.PublishMode.CreateNew)
    try:
        assert published.id, "publish returned no workbook id"
        assert published.name == wb_item.name, f"published name {published.name!r} != requested {wb_item.name!r}"
    finally:
        server.workbooks.delete(published.id)
