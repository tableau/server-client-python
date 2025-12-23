from pathlib import Path
import sys

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import FlowRunFailedException
from ._utils import mocked_time, server_response_error_factory

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "flow_runs_get.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "flow_runs_get_by_id.xml"
GET_BY_ID_FAILED_XML = TEST_ASSET_DIR / "flow_runs_get_by_id_failed.xml"
GET_BY_ID_INPROGRESS_XML = TEST_ASSET_DIR / "flow_runs_get_by_id_inprogress.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    server = TSC.Server("http://test", False)
    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.10"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.flow_runs.baseurl, text=response_xml)
        all_flow_runs = server.flow_runs.get()

    assert "cc2e652d-4a9b-4476-8c93-b238c45db968" == all_flow_runs[0].id
    assert "2021-02-11T01:42:55Z" == format_datetime(all_flow_runs[0].started_at)
    assert "2021-02-11T01:57:38Z" == format_datetime(all_flow_runs[0].completed_at)
    assert "Success" == all_flow_runs[0].status
    assert "100" == all_flow_runs[0].progress
    assert "aa23f4ac-906f-11e9-86fb-3f0f71412e77" == all_flow_runs[0].background_job_id

    assert "a3104526-c0c6-4ea5-8362-e03fc7cbd7ee" == all_flow_runs[1].id
    assert "2021-02-13T04:05:30Z" == format_datetime(all_flow_runs[1].started_at)
    assert "2021-02-13T04:05:35Z" == format_datetime(all_flow_runs[1].completed_at)
    assert "Failed" == all_flow_runs[1].status
    assert "100" == all_flow_runs[1].progress
    assert "1ad21a9d-2530-4fbf-9064-efd3c736e023" == all_flow_runs[1].background_job_id


def test_get_by_id(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.flow_runs.baseurl + "/cc2e652d-4a9b-4476-8c93-b238c45db968", text=response_xml)
        flow_run = server.flow_runs.get_by_id("cc2e652d-4a9b-4476-8c93-b238c45db968")

    assert "cc2e652d-4a9b-4476-8c93-b238c45db968" == flow_run.id
    assert "2021-02-11T01:42:55Z" == format_datetime(flow_run.started_at)
    assert "2021-02-11T01:57:38Z" == format_datetime(flow_run.completed_at)
    assert "Success" == flow_run.status
    assert "100" == flow_run.progress
    assert "1ad21a9d-2530-4fbf-9064-efd3c736e023" == flow_run.background_job_id


def test_cancel_id(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.put(server.flow_runs.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
        server.flow_runs.cancel("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")


def test_cancel_item(server: TSC.Server) -> None:
    run = TSC.FlowRunItem()
    run._id = "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
    with requests_mock.mock() as m:
        m.put(server.flow_runs.baseurl + "/ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", status_code=204)
        server.flow_runs.cancel(run)


def test_wait_for_job_finished(server: TSC.Server) -> None:
    # Waiting for an already finished job, directly returns that job's info
    response_xml = GET_BY_ID_XML.read_text()
    flow_run_id = "cc2e652d-4a9b-4476-8c93-b238c45db968"
    with mocked_time(), requests_mock.mock() as m:
        m.get(f"{server.flow_runs.baseurl}/{flow_run_id}", text=response_xml)
        flow_run = server.flow_runs.wait_for_job(flow_run_id)

        assert flow_run_id == flow_run.id
        assert flow_run.progress == "100"


def test_wait_for_job_failed(server: TSC.Server) -> None:
    # Waiting for a failed job raises an exception
    response_xml = GET_BY_ID_FAILED_XML.read_text()
    flow_run_id = "c2b35d5a-e130-471a-aec8-7bc5435fe0e7"
    with mocked_time(), requests_mock.mock() as m:
        m.get(f"{server.flow_runs.baseurl}/{flow_run_id}", text=response_xml)
        with pytest.raises(FlowRunFailedException):
            server.flow_runs.wait_for_job(flow_run_id)


def test_wait_for_job_timeout(server: TSC.Server) -> None:
    # Waiting for a job which doesn't terminate will throw an exception
    response_xml = GET_BY_ID_INPROGRESS_XML.read_text()
    flow_run_id = "71afc22c-9c06-40be-8d0f-4c4166d29e6c"
    with mocked_time(), requests_mock.mock() as m:
        m.get(f"{server.flow_runs.baseurl}/{flow_run_id}", text=response_xml)
        with pytest.raises(TimeoutError):
            server.flow_runs.wait_for_job(flow_run_id, timeout=30)


def test_queryset(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    error_response = server_response_error_factory(
        "400006", "Bad Request", "0xB4EAB088 : The start index '9900' is greater than or equal to the total count.)"
    )
    with requests_mock.mock() as m:
        m.get(f"{server.flow_runs.baseurl}?pageNumber=1", text=response_xml)
        m.get(f"{server.flow_runs.baseurl}?pageNumber=2", text=error_response)
        queryset = server.flow_runs.all()
        assert len(queryset) == sys.maxsize
