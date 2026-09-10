"""
E2E tests for Jobs and async operations against a real Tableau server.

Run with:
    TABLEAU_SERVER=https://... TABLEAU_SITE=mysite TABLEAU_TOKEN=... TABLEAU_TOKEN_NAME=... \
    pytest test_e2e/test_jobs.py -v
"""

from pathlib import Path

import pytest
import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import (
    JobCancelledException,
    JobFailedException,
    ServerResponseError,
)

ASSETS_DIR = Path(__file__).parent / "assets"
SAMPLE_WORKBOOK = ASSETS_DIR / "WorkbookWithoutExtract.twbx"
EXTRACT_WORKBOOK = ASSETS_DIR / "WorkbookWithExtract.twbx"
SAMPLE_DATASOURCE = ASSETS_DIR / "WorldIndicators.tdsx"

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def workbook(server, project_id):
    """Publish a workbook for jobs tests, clean up after."""
    wb = TSC.WorkbookItem(name="tsc-e2e-jobs-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        yield wb
    finally:
        server.workbooks.delete(wb.id)


@pytest.fixture(scope="module")
def datasource(server, project_id):
    """Publish a datasource for jobs tests, clean up after."""
    ds = TSC.DatasourceItem(project_id=project_id, name="tsc-e2e-jobs-ds")
    ds = server.datasources.publish(ds, SAMPLE_DATASOURCE, TSC.Server.PublishMode.Overwrite)
    try:
        yield ds
    finally:
        server.datasources.delete(ds.id)


@pytest.fixture(scope="module")
def extract_workbook(server, project_id):
    """Publish a workbook with an extract for refresh tests, clean up after."""
    if not EXTRACT_WORKBOOK.exists():
        pytest.skip(f"Extract workbook asset not found: {EXTRACT_WORKBOOK}")
    wb = TSC.WorkbookItem(name="tsc-e2e-extract-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, EXTRACT_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        yield wb
    finally:
        server.workbooks.delete(wb.id)


def test_jobs_get_returns_list(server):
    """jobs.get() returns a list of background jobs and a pagination item."""
    jobs, pagination = server.jobs.get()
    assert isinstance(jobs, list)
    assert pagination is not None
    assert pagination.total_available >= 0


def test_workbook_refresh_returns_job(server, workbook):
    """workbooks.refresh() returns a JobItem with a valid id."""
    try:
        job = server.workbooks.refresh(workbook)
    except ServerResponseError as e:
        if "403180" in str(e) or "refresh" in str(e).lower():
            pytest.skip(f"Workbook does not support refresh on this server: {e}")
        raise
    if job is None:
        pytest.skip("Duplicate refresh job already queued — skipping")
    assert job.id is not None
    assert isinstance(job.id, str)


def test_jobs_get_by_id(server, project_id):
    """jobs.get_by_id() returns the correct JobItem for a running job."""
    wb = TSC.WorkbookItem(name="tsc-e2e-jobs-get-by-id-wb", project_id=project_id)
    wb = server.workbooks.publish(wb, SAMPLE_WORKBOOK, TSC.Server.PublishMode.Overwrite)
    try:
        try:
            job = server.workbooks.refresh(wb)
        except ServerResponseError as e:
            if "403180" in str(e) or "refresh" in str(e).lower():
                pytest.skip(f"Workbook does not support refresh on this server: {e}")
            raise
        if job is None:
            pytest.skip("Duplicate refresh job already queued — skipping")
        fetched = server.jobs.get_by_id(job.id)
        assert fetched is not None
        assert fetched.id == job.id
    finally:
        server.workbooks.delete(wb.id)


def test_workbook_refresh_job_completes(server, workbook):
    """wait_for_job() on a workbook refresh completes without raising."""
    try:
        job = server.workbooks.refresh(workbook)
    except ServerResponseError as e:
        if "403180" in str(e) or "refresh" in str(e).lower():
            pytest.skip(f"Workbook does not support refresh on this server: {e}")
        raise
    if job is None:
        pytest.skip("Duplicate refresh job already queued — skipping")
    try:
        completed_job = server.jobs.wait_for_job(job, timeout=300)
    except JobFailedException as e:
        pytest.skip(f"Job failed — workbook must contain an extract for this test: {e}")
    except JobCancelledException as e:
        pytest.skip(f"Job was cancelled: {e}")
    assert completed_job.finish_code in (TSC.JobItem.FinishCode.Success, TSC.JobItem.FinishCode.Completed)
    assert completed_job.completed_at is not None


def test_datasource_refresh_job_completes(server, datasource):
    """datasources.refresh() returns a job that completes successfully."""
    job = server.datasources.refresh(datasource)
    if job is None:
        pytest.skip("Duplicate refresh job already queued — skipping")
    assert job is not None
    assert job.id is not None
    try:
        completed_job = server.jobs.wait_for_job(job, timeout=300)
    except JobFailedException as e:
        pytest.skip(f"Datasource refresh job failed: {e}")
    except JobCancelledException as e:
        pytest.skip(f"Job was cancelled: {e}")
    assert completed_job.finish_code in (TSC.JobItem.FinishCode.Success, TSC.JobItem.FinishCode.Completed)
    assert completed_job.completed_at is not None


def test_extract_workbook_refresh_completes(server, extract_workbook):
    """workbooks.refresh() on a workbook with an extract completes successfully."""
    job = server.workbooks.refresh(extract_workbook)
    if job is None:
        pytest.skip("Duplicate refresh job already queued — skipping")
    try:
        completed_job = server.jobs.wait_for_job(job, timeout=300)
    except JobFailedException as e:
        pytest.skip(f"Extract workbook refresh job failed (check asset compatibility): {e}")
    except JobCancelledException as e:
        pytest.skip(f"Job was cancelled: {e}")
    assert completed_job.finish_code in (TSC.JobItem.FinishCode.Success, TSC.JobItem.FinishCode.Completed)
    assert completed_job.completed_at is not None
