from datetime import time
from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.task_item import TaskItem

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML_NO_WORKBOOK = TEST_ASSET_DIR / "tasks_no_workbook_or_datasource.xml"
GET_XML_WITH_WORKBOOK = TEST_ASSET_DIR / "tasks_with_workbook.xml"
GET_XML_WITH_DATASOURCE = TEST_ASSET_DIR / "tasks_with_datasource.xml"
GET_XML_WITH_WORKBOOK_AND_DATASOURCE = TEST_ASSET_DIR / "tasks_with_workbook_and_datasource.xml"
GET_XML_DATAACCELERATION_TASK = TEST_ASSET_DIR / "tasks_with_dataacceleration_task.xml"
GET_XML_RUN_NOW_RESPONSE = TEST_ASSET_DIR / "tasks_run_now_response.xml"
GET_XML_CREATE_TASK_RESPONSE = TEST_ASSET_DIR / "tasks_create_extract_task.xml"
GET_XML_WITHOUT_SCHEDULE = TEST_ASSET_DIR / "tasks_without_schedule.xml"
GET_XML_WITH_INTERVAL = TEST_ASSET_DIR / "tasks_with_interval.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.19"

    return server


@pytest.fixture(scope="function")
def baseurl(server: TSC.Server) -> str:
    return f"{server.tasks.baseurl}/extractRefreshes"


def test_get_tasks_with_no_workbook(server: TSC.Server, baseurl: str) -> None:
    response_xml = GET_XML_NO_WORKBOOK.read_text()
    with requests_mock.mock() as m:
        m.get(baseurl, text=response_xml)
        all_tasks, pagination_item = server.tasks.get()

    task = all_tasks[0]
    assert task.target is None


def test_get_tasks_with_workbook(server: TSC.Server, baseurl: str) -> None:
    response_xml = GET_XML_WITH_WORKBOOK.read_text()
    with requests_mock.mock() as m:
        m.get(baseurl, text=response_xml)
        all_tasks, pagination_item = server.tasks.get()

    task = all_tasks[0]
    assert "c7a9327e-1cda-4504-b026-ddb43b976d1d" == task.target.id
    assert "workbook" == task.target.type


def test_get_tasks_with_datasource(server: TSC.Server, baseurl: str) -> None:
    response_xml = GET_XML_WITH_DATASOURCE.read_text()
    with requests_mock.mock() as m:
        m.get(baseurl, text=response_xml)
        all_tasks, pagination_item = server.tasks.get()

    task = all_tasks[0]
    assert "c7a9327e-1cda-4504-b026-ddb43b976d1d" == task.target.id
    assert "datasource" == task.target.type


def test_get_tasks_with_workbook_and_datasource(server: TSC.Server, baseurl: str) -> None:
    response_xml = GET_XML_WITH_WORKBOOK_AND_DATASOURCE.read_text()
    with requests_mock.mock() as m:
        m.get(baseurl, text=response_xml)
        all_tasks, pagination_item = server.tasks.get()

    assert "workbook" == all_tasks[0].target.type
    assert "datasource" == all_tasks[1].target.type
    assert "workbook" == all_tasks[2].target.type


def test_get_task_with_schedule(server: TSC.Server, baseurl: str) -> None:
    response_xml = GET_XML_WITH_WORKBOOK.read_text()
    with requests_mock.mock() as m:
        m.get(baseurl, text=response_xml)
        all_tasks, pagination_item = server.tasks.get()

    task = all_tasks[0]
    assert "c7a9327e-1cda-4504-b026-ddb43b976d1d" == task.target.id
    assert "workbook" == task.target.type
    assert "b60b4efd-a6f7-4599-beb3-cb677e7abac1" == task.schedule_id


def test_get_task_without_schedule(server: TSC.Server, baseurl: str) -> None:
    with requests_mock.mock() as m:
        m.get(baseurl, text=GET_XML_WITHOUT_SCHEDULE.read_text())
        all_tasks, pagination_item = server.tasks.get()

    task = all_tasks[0]
    assert "c7a9327e-1cda-4504-b026-ddb43b976d1d" == task.target.id
    assert "datasource" == task.target.type


def test_get_task_with_interval(server: TSC.Server, baseurl: str) -> None:
    with requests_mock.mock() as m:
        m.get(baseurl, text=GET_XML_WITH_INTERVAL.read_text())
        all_tasks, pagination_item = server.tasks.get()

    task = all_tasks[0]
    assert "e4de0575-fcc7-4232-5659-be09bb8e7654" == task.target.id
    assert "datasource" == task.target.type


def test_delete(server: TSC.Server, baseurl: str) -> None:
    with requests_mock.mock() as m:
        m.delete(baseurl + "/c7a9327e-1cda-4504-b026-ddb43b976d1d", status_code=204)
        server.tasks.delete("c7a9327e-1cda-4504-b026-ddb43b976d1d")


def test_delete_missing_id(server: TSC.Server, baseurl: str) -> None:
    with pytest.raises(ValueError):
        server.tasks.delete("")


def test_get_materializeviews_tasks(server: TSC.Server, baseurl: str) -> None:
    response_xml = GET_XML_DATAACCELERATION_TASK.read_text()
    with requests_mock.mock() as m:
        m.get(f"{server.tasks.baseurl}/{TaskItem.Type.DataAcceleration}", text=response_xml)
        all_tasks, pagination_item = server.tasks.get(task_type=TaskItem.Type.DataAcceleration)

    task = all_tasks[0]
    assert "a462c148-fc40-4670-a8e4-39b7f0c58c7f" == task.target.id
    assert "workbook" == task.target.type
    assert "b22190b4-6ac2-4eed-9563-4afc03444413" == task.schedule_id
    assert parse_datetime("2019-12-09T22:30:00Z") == task.schedule_item.next_run_at
    assert parse_datetime("2019-12-09T20:45:04Z") == task.last_run_at
    assert TSC.TaskItem.Type.DataAcceleration == task.task_type


def test_delete_data_acceleration(server: TSC.Server, baseurl: str) -> None:
    with requests_mock.mock() as m:
        m.delete(
            "{}/{}/{}".format(
                server.tasks.baseurl, TaskItem.Type.DataAcceleration, "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
            ),
            status_code=204,
        )
        server.tasks.delete("c9cff7f9-309c-4361-99ff-d4ba8c9f5467", TaskItem.Type.DataAcceleration)


def test_get_by_id(server: TSC.Server, baseurl: str) -> None:
    response_xml = GET_XML_WITH_WORKBOOK.read_text()
    task_id = "f84901ac-72ad-4f9b-a87e-7a3500402ad6"
    with requests_mock.mock() as m:
        m.get(f"{baseurl}/{task_id}", text=response_xml)
        task = server.tasks.get_by_id(task_id)

    assert "c7a9327e-1cda-4504-b026-ddb43b976d1d" == task.target.id
    assert "workbook" == task.target.type
    assert "b60b4efd-a6f7-4599-beb3-cb677e7abac1" == task.schedule_id
    assert TSC.TaskItem.Type.ExtractRefresh == task.task_type


def test_run_now(server: TSC.Server, baseurl: str) -> None:
    task_id = "f84901ac-72ad-4f9b-a87e-7a3500402ad6"
    task = TaskItem(task_id, TaskItem.Type.ExtractRefresh, 100)
    response_xml = GET_XML_RUN_NOW_RESPONSE.read_text()
    with requests_mock.mock() as m:
        m.post(f"{baseurl}/{task_id}/runNow", text=response_xml)
        job_response_content = server.tasks.run(task).decode("utf-8")

    assert "7b6b59a8-ac3c-4d1d-2e9e-0b5b4ba8a7b6" in job_response_content
    assert "RefreshExtract" in job_response_content


def test_create_extract_task(server: TSC.Server, baseurl: str) -> None:
    monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30), interval_value=15)
    monthly_schedule = TSC.ScheduleItem(
        None,  # type: ignore[arg-type]
        None,  # type: ignore[arg-type]
        None,  # type: ignore[arg-type]
        None,  # type: ignore[arg-type]
        monthly_interval,
    )
    target_item = TSC.Target("workbook_id", "workbook")

    task = TaskItem(None, "FullRefresh", None, schedule_item=monthly_schedule, target=target_item)  # type: ignore[arg-type]

    response_xml = GET_XML_CREATE_TASK_RESPONSE.read_text()
    with requests_mock.mock() as m:
        m.post(f"{baseurl}", text=response_xml)
        create_response_content = server.tasks.create(task).decode("utf-8")

    assert "task_id" in create_response_content
    assert "workbook_id" in create_response_content
    assert "FullRefresh" in create_response_content
