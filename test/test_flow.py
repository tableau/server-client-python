from io import BytesIO
import os
from pathlib import Path
import requests_mock
import tempfile

import pytest

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "flow_get.xml"
POPULATE_CONNECTIONS_XML = TEST_ASSET_DIR / "flow_populate_connections.xml"
POPULATE_PERMISSIONS_XML = TEST_ASSET_DIR / "flow_populate_permissions.xml"
PUBLISH_XML = TEST_ASSET_DIR / "flow_publish.xml"
UPDATE_XML = TEST_ASSET_DIR / "flow_update.xml"
REFRESH_XML = TEST_ASSET_DIR / "flow_refresh.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.3"

    return server


def test_download(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(
            server.flows.baseurl + "/587daa37-b84d-4400-a9a2-aa90e0be7837/content",
            headers={"Content-Disposition": 'name="tableau_flow"; filename="FlowOne.tfl"'},
        )
        file_path = server.flows.download("587daa37-b84d-4400-a9a2-aa90e0be7837")
        assert os.path.exists(file_path) is True
    os.remove(file_path)


def test_download_object(server: TSC.Server) -> None:
    with BytesIO() as file_object:
        with requests_mock.mock() as m:
            m.get(
                server.flows.baseurl + "/587daa37-b84d-4400-a9a2-aa90e0be7837/content",
                headers={"Content-Disposition": 'name="tableau_flow"; filename="FlowOne.tfl"'},
            )
            file_path = server.flows.download("587daa37-b84d-4400-a9a2-aa90e0be7837", filepath=file_object)
            assert isinstance(file_path, BytesIO)


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.flows.baseurl, text=response_xml)
        all_flows, pagination_item = server.flows.get()

    assert 5 == pagination_item.total_available
    assert "587daa37-b84d-4400-a9a2-aa90e0be7837" == all_flows[0].id
    assert "http://tableauserver/#/flows/1" == all_flows[0].webpage_url
    assert "2019-06-16T21:43:28Z" == format_datetime(all_flows[0].created_at)
    assert "2019-06-16T21:43:28Z" == format_datetime(all_flows[0].updated_at)
    assert "Default" == all_flows[0].project_name
    assert "FlowOne" == all_flows[0].name
    assert "aa23f4ac-906f-11e9-86fb-3f0f71412e77" == all_flows[0].project_id
    assert "7ebb3f20-0fd2-4f27-a2f6-c539470999e2" == all_flows[0].owner_id
    assert {"i_love_tags"} == all_flows[0].tags
    assert "Descriptive" == all_flows[0].description

    assert "5c36be69-eb30-461b-b66e-3e2a8e27cc35" == all_flows[1].id
    assert "http://tableauserver/#/flows/4" == all_flows[1].webpage_url
    assert "2019-06-18T03:08:19Z" == format_datetime(all_flows[1].created_at)
    assert "2019-06-18T03:08:19Z" == format_datetime(all_flows[1].updated_at)
    assert "Default" == all_flows[1].project_name
    assert "FlowTwo" == all_flows[1].name
    assert "aa23f4ac-906f-11e9-86fb-3f0f71412e77" == all_flows[1].project_id
    assert "9127d03f-d996-405f-b392-631b25183a0f" == all_flows[1].owner_id


def test_update(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.flows.baseurl + "/587daa37-b84d-4400-a9a2-aa90e0be7837", text=response_xml)
        single_datasource = TSC.FlowItem("test", "aa23f4ac-906f-11e9-86fb-3f0f71412e77")
        single_datasource.owner_id = "7ebb3f20-0fd2-4f27-a2f6-c539470999e2"
        single_datasource._id = "587daa37-b84d-4400-a9a2-aa90e0be7837"
        single_datasource.description = "So fun to see"
        single_datasource = server.flows.update(single_datasource)

    assert "587daa37-b84d-4400-a9a2-aa90e0be7837" == single_datasource.id
    assert "aa23f4ac-906f-11e9-86fb-3f0f71412e77" == single_datasource.project_id
    assert "7ebb3f20-0fd2-4f27-a2f6-c539470999e2" == single_datasource.owner_id
    assert "So fun to see" == single_datasource.description


def test_populate_connections(server: TSC.Server) -> None:
    response_xml = POPULATE_CONNECTIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.flows.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections", text=response_xml)
        single_datasource = TSC.FlowItem("test", "aa23f4ac-906f-11e9-86fb-3f0f71412e77")
        single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        server.flows.populate_connections(single_datasource)
        assert "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb" == single_datasource.id
        connections = single_datasource.connections

    assert connections is not None
    assert len(connections) > 0
    conn1, conn2, conn3 = connections
    assert "405c1e4b-60c9-499f-9c47-a4ef1af69359" == conn1.id
    assert "excel-direct" == conn1.connection_type
    assert "" == conn1.server_address
    assert "" == conn1.username
    assert conn1.embed_password is False
    assert "b47f41b1-2c47-41a3-8b17-a38ebe8b340c" == conn2.id
    assert "sqlserver" == conn2.connection_type
    assert "test.database.com" == conn2.server_address
    assert "bob" == conn2.username
    assert conn2.embed_password is False
    assert "4f4a3b78-0554-43a7-b327-9605e9df9dd2" == conn3.id
    assert "tableau-server-site" == conn3.connection_type
    assert "http://tableauserver" == conn3.server_address
    assert "sally" == conn3.username
    assert conn3.embed_password is True


def test_populate_permissions(server: TSC.Server) -> None:
    response_xml = POPULATE_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.flows.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)
        single_datasource = TSC.FlowItem("test")
        single_datasource._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

        server.flows.populate_permissions(single_datasource)
        permissions = single_datasource.permissions

        assert permissions[0].grantee.tag_name == "group"
        assert permissions[0].grantee.id == "aa42f384-906f-11e9-86fc-bb24278874b9"
        assert permissions[0].capabilities == {
            TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        }

        assert permissions[1].grantee.tag_name == "groupSet"
        assert permissions[1].grantee.id == "7ea95a1b-6872-44d6-a969-68598a7df4a0"
        assert permissions[1].capabilities == {
            TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        }


def test_publish(server: TSC.Server) -> None:
    response_xml = PUBLISH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.flows.baseurl, text=response_xml)

        new_flow = TSC.FlowItem(name="SampleFlow", project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

        sample_flow = TEST_ASSET_DIR / "SampleFlow.tfl"
        publish_mode = server.PublishMode.CreateNew

        new_flow = server.flows.publish(new_flow, sample_flow, publish_mode)

    assert "2457c468-1b24-461a-8f95-a461b3209d32" == new_flow.id
    assert "SampleFlow" == new_flow.name
    assert "2023-01-13T09:50:55Z" == format_datetime(new_flow.created_at)
    assert "2023-01-13T09:50:55Z" == format_datetime(new_flow.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_flow.project_id
    assert "default" == new_flow.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_flow.owner_id


def test_publish_file_object(server: TSC.Server) -> None:
    response_xml = PUBLISH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.flows.baseurl, text=response_xml)

        new_flow = TSC.FlowItem(name="SampleFlow", project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
        sample_flow = os.path.join(TEST_ASSET_DIR, "SampleFlow.tfl")
        publish_mode = server.PublishMode.CreateNew

        
        with open(sample_flow, "rb") as fp:
            publish_mode = server.PublishMode.CreateNew

            new_flow = server.flows.publish(new_flow, fp, publish_mode)

    assert "2457c468-1b24-461a-8f95-a461b3209d32" == new_flow.id
    assert "SampleFlow" == new_flow.name
    assert "2023-01-13T09:50:55Z" == format_datetime(new_flow.created_at)
    assert "2023-01-13T09:50:55Z" == format_datetime(new_flow.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_flow.project_id
    assert "default" == new_flow.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_flow.owner_id


def test_refresh(server: TSC.Server) -> None:
    response_xml = REFRESH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.flows.baseurl + "/92967d2d-c7e2-46d0-8847-4802df58f484/run", text=response_xml)
        flow_item = TSC.FlowItem("test")
        flow_item._id = "92967d2d-c7e2-46d0-8847-4802df58f484"
        refresh_job = server.flows.refresh(flow_item)

        assert refresh_job.id == "d1b2ccd0-6dfa-444a-aee4-723dbd6b7c9d"
        assert refresh_job.mode == "Asynchronous"
        assert refresh_job.type == "RunFlow"
        assert format_datetime(refresh_job.created_at) == "2018-05-22T13:00:29Z"
        assert isinstance(refresh_job.flow_run, TSC.FlowRunItem)
        assert refresh_job.flow_run.id == "e0c3067f-2333-4eee-8028-e0a56ca496f6"
        assert refresh_job.flow_run.flow_id == "92967d2d-c7e2-46d0-8847-4802df58f484"
        assert format_datetime(refresh_job.flow_run.started_at) == "2018-05-22T13:00:29Z"


def test_refresh_id_str(server: TSC.Server) -> None:
        response_xml = REFRESH_XML.read_text()
        with requests_mock.mock() as m:
            m.post(server.flows.baseurl + "/92967d2d-c7e2-46d0-8847-4802df58f484/run", text=response_xml)
            refresh_job = server.flows.refresh("92967d2d-c7e2-46d0-8847-4802df58f484")

            assert refresh_job.id == "d1b2ccd0-6dfa-444a-aee4-723dbd6b7c9d"
            assert refresh_job.mode == "Asynchronous"
            assert refresh_job.type == "RunFlow"
            assert format_datetime(refresh_job.created_at) == "2018-05-22T13:00:29Z"
            assert isinstance(refresh_job.flow_run, TSC.FlowRunItem)
            assert refresh_job.flow_run.id == "e0c3067f-2333-4eee-8028-e0a56ca496f6"
            assert refresh_job.flow_run.flow_id == "92967d2d-c7e2-46d0-8847-4802df58f484"
            assert format_datetime(refresh_job.flow_run.started_at) == "2018-05-22T13:00:29Z"


def test_bad_download_response(server: TSC.Server) -> None:
    with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
        m.get(
            server.flows.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content",
            headers={"Content-Disposition": '''name="tableau_flow"; filename*=UTF-8''"Sample flow.tfl"'''},
        )
        file_path = server.flows.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", td)
        assert os.path.exists(file_path) is True
