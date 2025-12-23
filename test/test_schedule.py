from pathlib import Path
from datetime import time

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "schedule_get.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "schedule_get_by_id.xml"
GET_HOURLY_ID_XML = TEST_ASSET_DIR / "schedule_get_hourly_id.xml"
GET_DAILY_ID_XML = TEST_ASSET_DIR / "schedule_get_daily_id.xml"
GET_MONTHLY_ID_XML = TEST_ASSET_DIR / "schedule_get_monthly_id.xml"
GET_MONTHLY_ID_2_XML = TEST_ASSET_DIR / "schedule_get_monthly_id_2.xml"
GET_EMPTY_XML = TEST_ASSET_DIR / "schedule_get_empty.xml"
CREATE_HOURLY_XML = TEST_ASSET_DIR / "schedule_create_hourly.xml"
CREATE_DAILY_XML = TEST_ASSET_DIR / "schedule_create_daily.xml"
CREATE_WEEKLY_XML = TEST_ASSET_DIR / "schedule_create_weekly.xml"
CREATE_MONTHLY_XML = TEST_ASSET_DIR / "schedule_create_monthly.xml"
UPDATE_XML = TEST_ASSET_DIR / "schedule_update.xml"
ADD_WORKBOOK_TO_SCHEDULE = TEST_ASSET_DIR / "schedule_add_workbook.xml"
ADD_WORKBOOK_TO_SCHEDULE_WITH_WARNINGS = TEST_ASSET_DIR / "schedule_add_workbook_with_warnings.xml"
ADD_DATASOURCE_TO_SCHEDULE = TEST_ASSET_DIR / "schedule_add_datasource.xml"
ADD_FLOW_TO_SCHEDULE = TEST_ASSET_DIR / "schedule_add_flow.xml"
GET_EXTRACT_TASKS_XML = TEST_ASSET_DIR / "schedule_get_extract_refresh_tasks.xml"
BATCH_UPDATE_STATE = TEST_ASSET_DIR / "schedule_batch_update_state.xml"

WORKBOOK_GET_BY_ID_XML = TEST_ASSET_DIR / "workbook_get_by_id.xml"
DATASOURCE_GET_BY_ID_XML = TEST_ASSET_DIR / "datasource_get_by_id.xml"
FLOW_GET_BY_ID_XML = TEST_ASSET_DIR / "flow_get_by_id.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.schedules.baseurl, text=response_xml)
        all_schedules, pagination_item = server.schedules.get()

    extract = all_schedules[0]
    subscription = all_schedules[1]
    flow = all_schedules[2]
    system = all_schedules[3]

    assert 2 == pagination_item.total_available
    assert "c9cff7f9-309c-4361-99ff-d4ba8c9f5467" == extract.id
    assert "Weekday early mornings" == extract.name
    assert "Active" == extract.state
    assert 50 == extract.priority
    assert "2016-07-06T20:19:00Z" == format_datetime(extract.created_at)
    assert "2016-09-13T11:00:32Z" == format_datetime(extract.updated_at)
    assert "Extract" == extract.schedule_type
    assert "2016-09-14T11:00:00Z" == format_datetime(extract.next_run_at)

    assert "bcb79d07-6e47-472f-8a65-d7f51f40c36c" == subscription.id
    assert "Saturday night" == subscription.name
    assert "Active" == subscription.state
    assert 80 == subscription.priority
    assert "2016-07-07T20:19:00Z" == format_datetime(subscription.created_at)
    assert "2016-09-12T16:39:38Z" == format_datetime(subscription.updated_at)
    assert "Subscription" == subscription.schedule_type
    assert "2016-09-18T06:00:00Z" == format_datetime(subscription.next_run_at)

    assert "f456e8f2-aeb2-4a8e-b823-00b6f08640f0" == flow.id
    assert "First of the month 1:00AM" == flow.name
    assert "Active" == flow.state
    assert 50 == flow.priority
    assert "2019-02-19T18:52:19Z" == format_datetime(flow.created_at)
    assert "2019-02-19T18:55:51Z" == format_datetime(flow.updated_at)
    assert "Flow" == flow.schedule_type
    assert "2019-03-01T09:00:00Z" == format_datetime(flow.next_run_at)

    assert "3cfa4713-ce7c-4fa7-aa2e-f752bfc8dd04" == system.id
    assert "First of the month 2:00AM" == system.name
    assert "Active" == system.state
    assert 30 == system.priority
    assert "2019-02-19T18:52:19Z" == format_datetime(system.created_at)
    assert "2019-02-19T18:55:51Z" == format_datetime(system.updated_at)
    assert "System" == system.schedule_type
    assert "2019-03-01T09:00:00Z" == format_datetime(system.next_run_at)


def test_get_empty(server: TSC.Server) -> None:
    response_xml = GET_EMPTY_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.schedules.baseurl, text=response_xml)
        all_schedules, pagination_item = server.schedules.get()

    assert 0 == pagination_item.total_available
    assert [] == all_schedules


def test_get_by_id(server: TSC.Server) -> None:
    server.version = "3.8"
    response_xml = GET_BY_ID_XML.read_text()
    with requests_mock.mock() as m:
        schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
        baseurl = f"{server.baseurl}/schedules/{schedule_id}"
        m.get(baseurl, text=response_xml)
        schedule = server.schedules.get_by_id(schedule_id)
        assert schedule is not None
        assert schedule_id == schedule.id
        assert "Weekday early mornings" == schedule.name
        assert "Active" == schedule.state


def test_get_hourly_by_id(server: TSC.Server) -> None:
    server.version = "3.8"
    response_xml = GET_HOURLY_ID_XML.read_text()
    with requests_mock.mock() as m:
        schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
        baseurl = f"{server.baseurl}/schedules/{schedule_id}"
        m.get(baseurl, text=response_xml)
        schedule = server.schedules.get_by_id(schedule_id)
        assert schedule is not None
        assert schedule_id == schedule.id
        assert "Hourly schedule" == schedule.name
        assert "Active" == schedule.state
        assert ("Monday", 0.5) == schedule.interval_item.interval


def test_get_daily_by_id(server: TSC.Server) -> None:
    server.version = "3.8"
    response_xml = GET_DAILY_ID_XML.read_text()
    with requests_mock.mock() as m:
        schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
        baseurl = f"{server.baseurl}/schedules/{schedule_id}"
        m.get(baseurl, text=response_xml)
        schedule = server.schedules.get_by_id(schedule_id)
        assert schedule is not None
        assert schedule_id == schedule.id
        assert "Daily schedule" == schedule.name
        assert "Active" == schedule.state
        assert ("Monday", 2.0) == schedule.interval_item.interval


def test_get_monthly_by_id(server: TSC.Server) -> None:
    server.version = "3.8"
    response_xml = GET_MONTHLY_ID_XML.read_text()
    with requests_mock.mock() as m:
        schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
        baseurl = f"{server.baseurl}/schedules/{schedule_id}"
        m.get(baseurl, text=response_xml)
        schedule = server.schedules.get_by_id(schedule_id)
        assert schedule is not None
        assert schedule_id == schedule.id
        assert "Monthly multiple days" == schedule.name
        assert "Active" == schedule.state
        assert ("1", "2") == schedule.interval_item.interval


def test_get_monthly_by_id_2(server: TSC.Server) -> None:
    server.version = "3.15"
    response_xml = GET_MONTHLY_ID_2_XML.read_text()
    with requests_mock.mock() as m:
        schedule_id = "8c5caf33-6223-4724-83c3-ccdc1e730a07"
        baseurl = f"{server.baseurl}/schedules/{schedule_id}"
        m.get(baseurl, text=response_xml)
        schedule = server.schedules.get_by_id(schedule_id)
        assert schedule is not None
        assert schedule_id == schedule.id
        assert "Monthly First Monday!" == schedule.name
        assert "Active" == schedule.state
        assert ("Monday", "First") == schedule.interval_item.interval


def test_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.schedules.baseurl + "/c9cff7f9-309c-4361-99ff-d4ba8c9f5467", status_code=204)
        server.schedules.delete("c9cff7f9-309c-4361-99ff-d4ba8c9f5467")


def test_create_hourly(server: TSC.Server) -> None:
    response_xml = CREATE_HOURLY_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.schedules.baseurl, text=response_xml)
        hourly_interval = TSC.HourlyInterval(start_time=time(2, 30), end_time=time(23, 0), interval_value=2)
        new_schedule = TSC.ScheduleItem(
            "hourly-schedule-1",
            50,
            TSC.ScheduleItem.Type.Extract,
            TSC.ScheduleItem.ExecutionOrder.Parallel,
            hourly_interval,
        )
        new_schedule = server.schedules.create(new_schedule)

    assert "5f42be25-8a43-47ba-971a-63f2d4e7029c" == new_schedule.id
    assert "hourly-schedule-1" == new_schedule.name
    assert "Active" == new_schedule.state
    assert 50 == new_schedule.priority
    assert "2016-09-15T20:47:33Z" == format_datetime(new_schedule.created_at)
    assert "2016-09-15T20:47:33Z" == format_datetime(new_schedule.updated_at)
    assert TSC.ScheduleItem.Type.Extract == new_schedule.schedule_type
    assert "2016-09-16T01:30:00Z" == format_datetime(new_schedule.next_run_at)
    assert TSC.ScheduleItem.ExecutionOrder.Parallel == new_schedule.execution_order
    assert time(2, 30) == new_schedule.interval_item.start_time
    assert time(23) == new_schedule.interval_item.end_time  # type: ignore[union-attr]
    assert ("8",) == new_schedule.interval_item.interval  # type: ignore[union-attr]


def test_create_daily(server: TSC.Server) -> None:
    response_xml = CREATE_DAILY_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.schedules.baseurl, text=response_xml)
        daily_interval = TSC.DailyInterval(time(4, 50))
        new_schedule = TSC.ScheduleItem(
            "daily-schedule-1",
            90,
            TSC.ScheduleItem.Type.Subscription,
            TSC.ScheduleItem.ExecutionOrder.Serial,
            daily_interval,
        )
        new_schedule = server.schedules.create(new_schedule)

    assert "907cae38-72fd-417c-892a-95540c4664cd" == new_schedule.id
    assert "daily-schedule-1" == new_schedule.name
    assert "Active" == new_schedule.state
    assert 90 == new_schedule.priority
    assert "2016-09-15T21:01:09Z" == format_datetime(new_schedule.created_at)
    assert "2016-09-15T21:01:09Z" == format_datetime(new_schedule.updated_at)
    assert TSC.ScheduleItem.Type.Subscription == new_schedule.schedule_type
    assert "2016-09-16T11:45:00Z" == format_datetime(new_schedule.next_run_at)
    assert TSC.ScheduleItem.ExecutionOrder.Serial == new_schedule.execution_order
    assert time(4, 45) == new_schedule.interval_item.start_time


def test_create_weekly(server: TSC.Server) -> None:
    response_xml = CREATE_WEEKLY_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.schedules.baseurl, text=response_xml)
        weekly_interval = TSC.WeeklyInterval(
            time(9, 15), TSC.IntervalItem.Day.Monday, TSC.IntervalItem.Day.Wednesday, TSC.IntervalItem.Day.Friday
        )
        new_schedule = TSC.ScheduleItem(
            "weekly-schedule-1",
            80,
            TSC.ScheduleItem.Type.Extract,
            TSC.ScheduleItem.ExecutionOrder.Parallel,
            weekly_interval,
        )
        new_schedule = server.schedules.create(new_schedule)

    assert "1adff386-6be0-4958-9f81-a35e676932bf" == new_schedule.id
    assert "weekly-schedule-1" == new_schedule.name
    assert "Active" == new_schedule.state
    assert 80 == new_schedule.priority
    assert "2016-09-15T21:12:50Z" == format_datetime(new_schedule.created_at)
    assert "2016-09-15T21:12:50Z" == format_datetime(new_schedule.updated_at)
    assert TSC.ScheduleItem.Type.Extract == new_schedule.schedule_type
    assert "2016-09-16T16:15:00Z" == format_datetime(new_schedule.next_run_at)
    assert TSC.ScheduleItem.ExecutionOrder.Parallel == new_schedule.execution_order
    assert time(9, 15) == new_schedule.interval_item.start_time
    assert ("Monday", "Wednesday", "Friday") == new_schedule.interval_item.interval
    assert 2 == len(new_schedule.warnings)
    assert "warning 1" == new_schedule.warnings[0]
    assert "warning 2" == new_schedule.warnings[1]


def test_create_monthly(server: TSC.Server) -> None:
    response_xml = CREATE_MONTHLY_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.schedules.baseurl, text=response_xml)
        monthly_interval = TSC.MonthlyInterval(time(7), 12)
        new_schedule = TSC.ScheduleItem(
            "monthly-schedule-1",
            20,
            TSC.ScheduleItem.Type.Extract,
            TSC.ScheduleItem.ExecutionOrder.Serial,
            monthly_interval,
        )
        new_schedule = server.schedules.create(new_schedule)

    assert "e06a7c75-5576-4f68-882d-8909d0219326" == new_schedule.id
    assert "monthly-schedule-1" == new_schedule.name
    assert "Active" == new_schedule.state
    assert 20 == new_schedule.priority
    assert "2016-09-15T21:16:56Z" == format_datetime(new_schedule.created_at)
    assert "2016-09-15T21:16:56Z" == format_datetime(new_schedule.updated_at)
    assert TSC.ScheduleItem.Type.Extract == new_schedule.schedule_type
    assert "2016-10-12T14:00:00Z" == format_datetime(new_schedule.next_run_at)
    assert TSC.ScheduleItem.ExecutionOrder.Serial == new_schedule.execution_order
    assert time(7) == new_schedule.interval_item.start_time
    assert ("12",) == new_schedule.interval_item.interval  # type: ignore[union-attr]


def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.schedules.baseurl + "/7bea1766-1543-4052-9753-9d224bc069b5", text=response_xml)
        new_interval = TSC.WeeklyInterval(time(7), TSC.IntervalItem.Day.Monday, TSC.IntervalItem.Day.Friday)
        single_schedule = TSC.ScheduleItem(
            "weekly-schedule-1",
            90,
            TSC.ScheduleItem.Type.Extract,
            TSC.ScheduleItem.ExecutionOrder.Parallel,
            new_interval,
        )
        single_schedule._id = "7bea1766-1543-4052-9753-9d224bc069b5"
        single_schedule.state = TSC.ScheduleItem.State.Suspended
        single_schedule = server.schedules.update(single_schedule)

    assert "7bea1766-1543-4052-9753-9d224bc069b5" == single_schedule.id
    assert "weekly-schedule-1" == single_schedule.name
    assert 90 == single_schedule.priority
    assert "2016-09-15T23:50:02Z" == format_datetime(single_schedule.updated_at)
    assert TSC.ScheduleItem.Type.Extract == single_schedule.schedule_type
    assert "2016-09-16T14:00:00Z" == format_datetime(single_schedule.next_run_at)
    assert TSC.ScheduleItem.ExecutionOrder.Parallel == single_schedule.execution_order
    assert time(7) == single_schedule.interval_item.start_time
    assert ("Monday", "Friday") == single_schedule.interval_item.interval  # type: ignore[union-attr]
    assert TSC.ScheduleItem.State.Suspended == single_schedule.state


# Tests calling update with a schedule item returned from the server
def test_update_after_get(server: TSC.Server) -> None:
    get_response_xml = GET_XML.read_text()
    update_response_xml = UPDATE_XML.read_text()

    # Get a schedule
    with requests_mock.mock() as m:
        m.get(server.schedules.baseurl, text=get_response_xml)
        all_schedules, pagination_item = server.schedules.get()
    schedule_item = all_schedules[0]
    assert TSC.ScheduleItem.State.Active == schedule_item.state
    assert "Weekday early mornings" == schedule_item.name

    # Update the schedule
    with requests_mock.mock() as m:
        m.put(server.schedules.baseurl + "/c9cff7f9-309c-4361-99ff-d4ba8c9f5467", text=update_response_xml)
        schedule_item.state = TSC.ScheduleItem.State.Suspended
        schedule_item.name = "newName"
        schedule_item = server.schedules.update(schedule_item)

    assert TSC.ScheduleItem.State.Suspended == schedule_item.state
    assert "weekly-schedule-1" == schedule_item.name


def test_add_workbook(server: TSC.Server) -> None:
    server.version = "2.8"
    baseurl = f"{server.baseurl}/sites/{server.site_id}/schedules"

    workbook_response = WORKBOOK_GET_BY_ID_XML.read_text()
    add_workbook_response = ADD_WORKBOOK_TO_SCHEDULE.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/bar", text=workbook_response)
        m.put(baseurl + "/foo/workbooks", text=add_workbook_response)
        workbook = server.workbooks.get_by_id("bar")
        result = server.schedules.add_to_schedule("foo", workbook=workbook)
    assert 0 == len(result), "Added properly"


def test_add_workbook_with_warnings(server: TSC.Server) -> None:
    server.version = "2.8"
    baseurl = f"{server.baseurl}/sites/{server.site_id}/schedules"

    workbook_response = WORKBOOK_GET_BY_ID_XML.read_text()
    add_workbook_response = ADD_WORKBOOK_TO_SCHEDULE_WITH_WARNINGS.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/bar", text=workbook_response)
        m.put(baseurl + "/foo/workbooks", text=add_workbook_response)
        workbook = server.workbooks.get_by_id("bar")
        result = server.schedules.add_to_schedule("foo", workbook=workbook)
    assert 1 == len(result), "Not added properly"
    assert 2 == len(result[0].warnings)


def test_add_datasource(server: TSC.Server) -> None:
    server.version = "2.8"
    baseurl = f"{server.baseurl}/sites/{server.site_id}/schedules"

    datasource_response = DATASOURCE_GET_BY_ID_XML.read_text()
    add_datasource_response = ADD_DATASOURCE_TO_SCHEDULE.read_text()
    with requests_mock.mock() as m:
        m.get(server.datasources.baseurl + "/bar", text=datasource_response)
        m.put(baseurl + "/foo/datasources", text=add_datasource_response)
        datasource = server.datasources.get_by_id("bar")
        result = server.schedules.add_to_schedule("foo", datasource=datasource)
    assert 0 == len(result), "Added properly"


def test_add_flow(server: TSC.Server) -> None:
    server.version = "3.3"
    baseurl = f"{server.baseurl}/sites/{server.site_id}/schedules"

    flow_response = FLOW_GET_BY_ID_XML.read_text()
    add_flow_response = ADD_FLOW_TO_SCHEDULE.read_text()
    with requests_mock.mock() as m:
        m.get(server.flows.baseurl + "/bar", text=flow_response)
        m.put(baseurl + "/foo/flows", text=flow_response)
        flow = server.flows.get_by_id("bar")
        result = server.schedules.add_to_schedule("foo", flow=flow)
    assert 0 == len(result), "Added properly"


def test_get_extract_refresh_tasks(server: TSC.Server) -> None:
    server.version = "2.3"

    response_xml = GET_EXTRACT_TASKS_XML.read_text()
    with requests_mock.mock() as m:
        schedule_id = "c9cff7f9-309c-4361-99ff-d4ba8c9f5467"
        baseurl = f"{server.baseurl}/sites/{server.site_id}/schedules/{schedule_id}/extracts"
        m.get(baseurl, text=response_xml)

        extracts = server.schedules.get_extract_refresh_tasks(schedule_id)

        assert extracts is not None
        assert isinstance(extracts[0], list)
        assert 2 == len(extracts[0])
        assert "task1" == extracts[0][0].id


def test_batch_update_state_items(server: TSC.Server) -> None:
    server.version = "3.27"
    hourly_interval = TSC.HourlyInterval(start_time=time(2, 30), end_time=time(23, 0), interval_value=2)
    args = ("hourly", 50, TSC.ScheduleItem.Type.Extract, TSC.ScheduleItem.ExecutionOrder.Parallel, hourly_interval)
    new_schedules = [TSC.ScheduleItem(*args), TSC.ScheduleItem(*args), TSC.ScheduleItem(*args)]
    new_schedules[0]._id = "593d2ebf-0d18-4deb-9d21-b113a4902583"
    new_schedules[1]._id = "cecbb71e-def0-4030-8068-5ae50f51db1c"
    new_schedules[2]._id = "f39a6e7d-405e-4c07-8c18-95845f9da80e"

    state = "active"
    with requests_mock.mock() as m:
        m.put(f"{server.schedules.baseurl}?state={state}", text=BATCH_UPDATE_STATE.read_text())
        resp = server.schedules.batch_update_state(new_schedules, state)

    assert len(resp) == 3
    for sch, r in zip(new_schedules, resp):
        assert sch.id == r


def test_batch_update_state_str(server: TSC.Server) -> None:
    server.version = "3.27"
    new_schedules = [
        "593d2ebf-0d18-4deb-9d21-b113a4902583",
        "cecbb71e-def0-4030-8068-5ae50f51db1c",
        "f39a6e7d-405e-4c07-8c18-95845f9da80e",
    ]

    state = "suspended"
    with requests_mock.mock() as m:
        m.put(f"{server.schedules.baseurl}?state={state}", text=BATCH_UPDATE_STATE.read_text())
        resp = server.schedules.batch_update_state(new_schedules, state)

    assert len(resp) == 3
    for sch, r in zip(new_schedules, resp):
        assert sch == r


def test_batch_update_state_all(server: TSC.Server) -> None:
    server.version = "3.27"
    new_schedules = [
        "593d2ebf-0d18-4deb-9d21-b113a4902583",
        "cecbb71e-def0-4030-8068-5ae50f51db1c",
        "f39a6e7d-405e-4c07-8c18-95845f9da80e",
    ]

    state = "suspended"
    with requests_mock.mock() as m:
        m.put(f"{server.schedules.baseurl}?state={state}&updateAll=true", text=BATCH_UPDATE_STATE.read_text())
        _ = server.schedules.batch_update_state(new_schedules, state, True)

        history = m.request_history[0]

    assert history.text == "<tsRequest />"
