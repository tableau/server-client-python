from datetime import time
from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.models.task_item import TaskItem

TEST_ASSET_DIR = Path(__file__).parent / "assets"
GET_XML_CREATE_FLOW_TASK_RESPONSE = TEST_ASSET_DIR / "tasks_create_flow_task.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.22"

    return server


def test_create_flow_task(server: TSC.Server) -> None:
    monthly_interval = TSC.MonthlyInterval(start_time=time(23, 30), interval_value=15)
    monthly_schedule = TSC.ScheduleItem(
        "Monthly Schedule",
        50,
        TSC.ScheduleItem.Type.Flow,
        TSC.ScheduleItem.ExecutionOrder.Parallel,
        monthly_interval,
    )
    target_item = TSC.Target("flow_id", "flow")

    task = TaskItem("", "RunFlow", 0, schedule_item=monthly_schedule, target=target_item)

    response_xml = GET_XML_CREATE_FLOW_TASK_RESPONSE.read_text()
    with requests_mock.mock() as m:
        m.post(f"{server.flow_tasks.baseurl}", text=response_xml)
        create_response_content = server.flow_tasks.create(task).decode("utf-8")

    assert "schedule_id" in create_response_content
    assert "flow_id" in create_response_content
