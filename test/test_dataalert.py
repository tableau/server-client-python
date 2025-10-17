from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "data_alerts_get.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "data_alerts_get_by_id.xml"
ADD_USER_TO_ALERT = TEST_ASSET_DIR / "data_alerts_add_user.xml"
UPDATE_XML = TEST_ASSET_DIR / "data_alerts_update.xml"


@pytest.fixture(scope="function")
def server():
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.2"

    return server


def test_get(server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.data_alerts.baseurl, text=response_xml)
        all_alerts, pagination_item = server.data_alerts.get()

    assert 1 == pagination_item.total_available
    assert "5ea59b45-e497-5673-8809-bfe213236f75" == all_alerts[0].id
    assert "Data Alert test" == all_alerts[0].subject
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_alerts[0].creatorId
    assert "2020-08-10T23:17:06Z" == all_alerts[0].createdAt
    assert "2020-08-10T23:17:06Z" == all_alerts[0].updatedAt
    assert "Daily" == all_alerts[0].frequency
    assert "true" == all_alerts[0].public
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_alerts[0].owner_id
    assert "Bob" == all_alerts[0].owner_name
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff5" == all_alerts[0].view_id
    assert "ENDANGERED SAFARI" == all_alerts[0].view_name
    assert "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00" == all_alerts[0].workbook_id
    assert "Safari stats" == all_alerts[0].workbook_name
    assert "5241e88d-d384-4fd7-9c2f-648b5247efc5" == all_alerts[0].project_id
    assert "Default" == all_alerts[0].project_name


def test_get_by_id(server) -> None:
    response_xml = GET_BY_ID_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.data_alerts.baseurl + "/5ea59b45-e497-5673-8809-bfe213236f75", text=response_xml)
        alert = server.data_alerts.get_by_id("5ea59b45-e497-5673-8809-bfe213236f75")

    assert isinstance(alert.recipients, list)
    assert len(alert.recipients) == 1
    assert alert.recipients[0] == "dd2239f6-ddf1-4107-981a-4cf94e415794"


def test_update(server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.data_alerts.baseurl + "/5ea59b45-e497-5673-8809-bfe213236f75", text=response_xml)
        single_alert = TSC.DataAlertItem()
        single_alert._id = "5ea59b45-e497-5673-8809-bfe213236f75"
        single_alert._subject = "Data Alert test"
        single_alert._frequency = "Daily"
        single_alert._public = True
        single_alert._owner_id = "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"
        single_alert = server.data_alerts.update(single_alert)

    assert "5ea59b45-e497-5673-8809-bfe213236f75" == single_alert.id
    assert "Data Alert test" == single_alert.subject
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == single_alert.creatorId
    assert "2020-08-10T23:17:06Z" == single_alert.createdAt
    assert "2020-08-10T23:17:06Z" == single_alert.updatedAt
    assert "Daily" == single_alert.frequency
    assert "true" == single_alert.public
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == single_alert.owner_id
    assert "Bob" == single_alert.owner_name
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff5" == single_alert.view_id
    assert "ENDANGERED SAFARI" == single_alert.view_name
    assert "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00" == single_alert.workbook_id
    assert "Safari stats" == single_alert.workbook_name
    assert "5241e88d-d384-4fd7-9c2f-648b5247efc5" == single_alert.project_id
    assert "Default" == single_alert.project_name


def test_add_user_to_alert(server) -> None:
    response_xml = ADD_USER_TO_ALERT.read_text()
    single_alert = TSC.DataAlertItem()
    single_alert._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"
    in_user = TSC.UserItem("Bob", TSC.UserItem.Roles.Explorer)
    in_user._id = "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"

    with requests_mock.mock() as m:
        m.post(server.data_alerts.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/users", text=response_xml)

        out_user = server.data_alerts.add_user_to_alert(single_alert, in_user)

        assert out_user.id == in_user.id
        assert out_user.name == in_user.name
        assert out_user.site_role == in_user.site_role


def test_delete(server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.data_alerts.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5", status_code=204)
        server.data_alerts.delete("0448d2ed-590d-4fa0-b272-a2a8a24555b5")


def test_delete_user_from_alert(server) -> None:
    alert_id = "5ea59b45-e497-5673-8809-bfe213236f75"
    user_id = "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"
    with requests_mock.mock() as m:
        m.delete(server.data_alerts.baseurl + f"/{alert_id}/users/{user_id}", status_code=204)
        server.data_alerts.delete_user_from_alert(alert_id, user_id)
