from pathlib import Path
import requests_mock

import pytest

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_BY_ID_ACCELERATION_STATUS_XML = TEST_ASSET_DIR / "workbook_get_by_id_acceleration_status.xml"
POPULATE_VIEWS_XML = TEST_ASSET_DIR / "workbook_populate_views.xml"
UPDATE_VIEWS_ACCELERATION_STATUS_XML = TEST_ASSET_DIR / "workbook_update_views_acceleration_status.xml"
UPDATE_WORKBOOK_ACCELERATION_STATUS_XML = TEST_ASSET_DIR / "workbook_update_acceleration_status.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_get_by_id(server: TSC.Server) -> None:
    response_xml = GET_BY_ID_ACCELERATION_STATUS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42", text=response_xml)
        single_workbook = server.workbooks.get_by_id("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    assert "3cc6cd06-89ce-4fdc-b935-5294135d6d42" == single_workbook.id
    assert "SafariSample" == single_workbook.name
    assert "SafariSample" == single_workbook.content_url
    assert "http://tableauserver/#/workbooks/2/views" == single_workbook.webpage_url
    assert single_workbook.show_tabs is False
    assert 26 == single_workbook.size
    assert "2016-07-26T20:34:56Z" == format_datetime(single_workbook.created_at)
    assert "description for SafariSample" == single_workbook.description
    assert "2016-07-26T20:35:05Z" == format_datetime(single_workbook.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == single_workbook.project_id
    assert "default" == single_workbook.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == single_workbook.owner_id
    assert {"Safari", "Sample"} == single_workbook.tags
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff5" == single_workbook.views[0].id
    assert "ENDANGERED SAFARI" == single_workbook.views[0].name
    assert "SafariSample/sheets/ENDANGEREDSAFARI" == single_workbook.views[0].content_url
    assert single_workbook.views[0].data_acceleration_config["acceleration_enabled"]
    assert "Enabled" == single_workbook.views[0].data_acceleration_config["acceleration_status"]
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff9" == single_workbook.views[1].id
    assert "ENDANGERED SAFARI 2" == single_workbook.views[1].name
    assert "SafariSample/sheets/ENDANGEREDSAFARI2" == single_workbook.views[1].content_url
    assert single_workbook.views[1].data_acceleration_config["acceleration_enabled"] is False
    assert "Suspended" == single_workbook.views[1].data_acceleration_config["acceleration_status"]


def test_update_workbook_acceleration(server: TSC.Server) -> None:
    response_xml = UPDATE_WORKBOOK_ACCELERATION_STATUS_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_acceleration_config = {
            "acceleration_enabled": True,
            "accelerate_now": False,
            "last_updated_at": None,
            "acceleration_status": None,
        }
        # update with parameter includeViewAccelerationStatus=True
        single_workbook = server.workbooks.update(single_workbook, True)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert "1d0304cd-3796-429f-b815-7258370b9b74" == single_workbook.project_id
    assert "SafariSample/sheets/ENDANGEREDSAFARI" == single_workbook.views[0].content_url
    assert single_workbook.views[0].data_acceleration_config["acceleration_enabled"]
    assert "Pending" == single_workbook.views[0].data_acceleration_config["acceleration_status"]
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff9" == single_workbook.views[1].id
    assert "ENDANGERED SAFARI 2" == single_workbook.views[1].name
    assert "SafariSample/sheets/ENDANGEREDSAFARI2" == single_workbook.views[1].content_url
    assert single_workbook.views[1].data_acceleration_config["acceleration_enabled"]
    assert "Pending" == single_workbook.views[1].data_acceleration_config["acceleration_status"]


def test_update_views_acceleration(server: TSC.Server) -> None:
    views_xml = POPULATE_VIEWS_XML.read_text()
    response_xml = UPDATE_VIEWS_ACCELERATION_STATUS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/views", text=views_xml)
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.data_acceleration_config = {
            "acceleration_enabled": False,
            "accelerate_now": False,
            "last_updated_at": None,
            "acceleration_status": None,
        }
        server.workbooks.populate_views(single_workbook)
        single_workbook.views = [single_workbook.views[1], single_workbook.views[2]]
        # update with parameter includeViewAccelerationStatus=True
        single_workbook = server.workbooks.update(single_workbook, True)

    views_list = single_workbook.views
    assert "097dbe13-de89-445f-b2c3-02f28bd010c1" == views_list[0].id
    assert "GDP per capita" == views_list[0].name
    assert views_list[0].data_acceleration_config["acceleration_enabled"] is False
    assert "Disabled" == views_list[0].data_acceleration_config["acceleration_status"]

    assert "2c1ab9d7-8d64-4cc6-b495-52e40c60c330" == views_list[1].id
    assert "Country ranks" == views_list[1].name
    assert views_list[1].data_acceleration_config["acceleration_enabled"]
    assert "Pending" == views_list[1].data_acceleration_config["acceleration_status"]

    assert "0599c28c-6d82-457e-a453-e52c1bdb00f5" == views_list[2].id
    assert "Interest rates" == views_list[2].name
    assert views_list[2].data_acceleration_config["acceleration_enabled"]
    assert "Pending" == views_list[2].data_acceleration_config["acceleration_status"]
