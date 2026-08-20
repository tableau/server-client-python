from datetime import datetime
from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import utc
from tableauserverclient.server.endpoint.exceptions import JobFailedException
from ._utils import mocked_time

TEST_ASSET_DIR = Path(__file__).parent / "assets"
GET_XML = TEST_ASSET_DIR / "job_get.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "job_get_by_id.xml"
GET_BY_ID_COMPLETED_XML = TEST_ASSET_DIR / "job_get_by_id_completed.xml"
GET_BY_ID_FAILED_XML = TEST_ASSET_DIR / "job_get_by_id_failed.xml"
GET_BY_ID_CANCELLED_XML = TEST_ASSET_DIR / "job_get_by_id_cancelled.xml"
GET_BY_ID_INPROGRESS_XML = TEST_ASSET_DIR / "job_get_by_id_inprogress.xml"
GET_BY_ID_WORKBOOK = TEST_ASSET_DIR / "job_get_by_id_failed_workbook.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.1"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.jobs.baseurl, text=response_xml)
        all_jobs, pagination_item = server.jobs.get()
        job = all_jobs[0]
        created_at = datetime(2018, 5, 22, 13, 0, 29, tzinfo=utc)
        started_at = datetime(2018, 5, 22, 13, 0, 37, tzinfo=utc)
        ended_at = datetime(2018, 5, 22, 13, 0, 45, tzinfo=utc)

        assert 1 == pagination_item.total_available
        assert "2eef4225-aa0c-41c4-8662-a76d89ed7336" == job.id
        assert "Success" == job.status
        assert "50" == job.priority
        assert "single_subscription_notify" == job.type
        assert created_at == job.created_at
        assert started_at == job.started_at
        assert ended_at == job.ended_at


def test_get_by_id(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_XML.read_text()
    job_id = "2eef4225-aa0c-41c4-8662-a76d89ed7336"
    with requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        job = server.jobs.get_by_id(job_id)
        updated_at = datetime(2020, 5, 13, 20, 25, 18, tzinfo=utc)

        assert job_id == job.id
        assert updated_at == job.updated_at
        assert job.notes == ["Job detail notes"]
        # Regression for #1850: the response also carries a <statusNotes><statusNote .../></statusNotes>
        # block per the public REST doc. Verify it now surfaces via job.status_notes.
        assert job.status_notes == [
            {
                "type": "CountOfUsersAddedToGroup",
                "value": "5",
                "text": "Description of how many users were added to the group during the import.",
            }
        ]


def test_status_notes_empty_when_absent() -> None:
    # A job element with no <statusNotes> yields an empty list, not None or an error.
    xml = (
        b"<tsResponse xmlns='http://tableau.com/api'>"
        b"<job id='j1' type='extractRefreshJob' progress='100' createdAt='2020-05-13T20:23:45Z' finishCode='0'/>"
        b"</tsResponse>"
    )
    jobs = TSC.JobItem.from_response(xml, {"t": "http://tableau.com/api"})
    assert len(jobs) == 1
    assert jobs[0].status_notes == []


def test_status_notes_multiple_entries() -> None:
    # Multiple statusNote elements yield an ordered list of dicts. Any of type /
    # value / text may be absent on a given note; missing attributes come back as None.
    xml = (
        b"<tsResponse xmlns='http://tableau.com/api'>"
        b"<job id='j1' type='UserImport' progress='100' createdAt='2020-05-13T20:23:45Z' finishCode='1'>"
        b"<statusNotes>"
        b"<statusNote type='line' value='0'/>"
        b"<statusNote type='errorCode' value='1'/>"
        b"<statusNote type='message' value='Actor does not have permission'/>"
        b"<statusNote type='username' value='unknown'/>"
        b"</statusNotes>"
        b"</job>"
        b"</tsResponse>"
    )
    jobs = TSC.JobItem.from_response(xml, {"t": "http://tableau.com/api"})
    assert len(jobs) == 1
    notes = jobs[0].status_notes
    assert notes == [
        {"type": "line", "value": "0", "text": None},
        {"type": "errorCode", "value": "1", "text": None},
        {"type": "message", "value": "Actor does not have permission", "text": None},
        {"type": "username", "value": "unknown", "text": None},
    ]


def test_get_before_signin(server: TSC.Server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.jobs.get()


def test_cancel_id(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.put(server.jobs.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
        server.jobs.cancel("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")


def test_cancel_item(server: TSC.Server) -> None:
    created_at = datetime(2018, 5, 22, 13, 0, 29, tzinfo=utc)
    started_at = datetime(2018, 5, 22, 13, 0, 37, tzinfo=utc)
    job = TSC.JobItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "backgroundJob", "0", created_at, started_at, None, 0)
    with requests_mock.mock() as m:
        m.put(server.jobs.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
        server.jobs.cancel(job)


def test_wait_for_job_finished(server: TSC.Server) -> None:
    # Waiting for an already finished job, directly returns that job's info
    response_xml = GET_BY_ID_XML.read_text()
    job_id = "2eef4225-aa0c-41c4-8662-a76d89ed7336"
    with mocked_time(), requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        job = server.jobs.wait_for_job(job_id)

        assert job_id == job.id
        assert job.notes == ["Job detail notes"]


def test_wait_for_job_completed(server: TSC.Server) -> None:
    # Waiting for a bridge (cloud) job completion
    response_xml = GET_BY_ID_COMPLETED_XML.read_text()
    job_id = "2eef4225-aa0c-41c4-8662-a76d89ed7336"
    with mocked_time(), requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        job = server.jobs.wait_for_job(job_id)

        assert job_id == job.id
        assert job.notes == ["Job detail notes"]


def test_wait_for_job_failed(server: TSC.Server) -> None:
    # Waiting for a failed job raises an exception
    response_xml = GET_BY_ID_FAILED_XML.read_text()
    job_id = "77d5e57a-2517-479f-9a3c-a32025f2b64d"
    with mocked_time(), requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        with pytest.raises(JobFailedException):
            server.jobs.wait_for_job(job_id)


def test_wait_for_job_timeout(server: TSC.Server) -> None:
    # Waiting for a job which doesn't terminate will throw an exception
    response_xml = GET_BY_ID_INPROGRESS_XML.read_text()
    job_id = "77d5e57a-2517-479f-9a3c-a32025f2b64d"
    with mocked_time(), requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        with pytest.raises(TimeoutError):
            server.jobs.wait_for_job(job_id, timeout=30)


def test_get_job_datasource_id(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_FAILED_XML.read_text()
    job_id = "777bf7c4-421d-4b2c-a518-11b90187c545"
    with requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        job = server.jobs.get_by_id(job_id)
    assert job.datasource_id == "03b9fbec-81f6-4160-ae49-5f9f6d412758"


def test_get_job_workbook_id(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_WORKBOOK.read_text()
    job_id = "bb1aab79-db54-4e96-9dd3-461d8f081d08"
    with requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        job = server.jobs.get_by_id(job_id)
    assert job.workbook_id == "5998aaaf-1abe-4d38-b4d9-bc53e85bdd13"


def test_get_job_workbook_name(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_WORKBOOK.read_text()
    job_id = "bb1aab79-db54-4e96-9dd3-461d8f081d08"
    with requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        job = server.jobs.get_by_id(job_id)
    assert job.workbook_name == "Superstore"


def test_get_job_datasource_name(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_FAILED_XML.read_text()
    job_id = "777bf7c4-421d-4b2c-a518-11b90187c545"
    with requests_mock.mock() as m:
        m.get(f"{server.jobs.baseurl}/{job_id}", text=response_xml)
        job = server.jobs.get_by_id(job_id)
    assert job.datasource_name == "World Indicators"


def test_background_job_str() -> None:
    job = TSC.BackgroundJobItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", datetime.now(), 1, "extractRefresh", "Failed")
    assert not str(job).startswith("<<property")
    assert not repr(job).startswith("<<property")
    assert "BackgroundJobItem" in str(job)
