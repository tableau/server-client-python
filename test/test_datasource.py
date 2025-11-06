from io import BytesIO
import os
from pathlib import Path
import tempfile
from typing import Optional
import unittest
from zipfile import ZipFile

from defusedxml.ElementTree import fromstring
import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient import ConnectionItem
from tableauserverclient.datetime_helpers import format_datetime, parse_datetime
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.endpoint.fileuploads_endpoint import Fileuploads
from tableauserverclient.server.request_factory import RequestFactory

TEST_ASSET_DIR = Path(__file__).parent / "assets"

ADD_TAGS_XML = TEST_ASSET_DIR / "datasource_add_tags.xml"
GET_XML = TEST_ASSET_DIR / "datasource_get.xml"
GET_EMPTY_XML = TEST_ASSET_DIR / "datasource_get_empty.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "datasource_get_by_id.xml"
GET_XML_ALL_FIELDS = TEST_ASSET_DIR / "datasource_get_all_fields.xml"
POPULATE_CONNECTIONS_XML = TEST_ASSET_DIR / "datasource_populate_connections.xml"
POPULATE_PERMISSIONS_XML = TEST_ASSET_DIR / "datasource_populate_permissions.xml"
PUBLISH_XML = TEST_ASSET_DIR / "datasource_publish.xml"
PUBLISH_XML_ASYNC = TEST_ASSET_DIR / "datasource_publish_async.xml"
REFRESH_XML = TEST_ASSET_DIR / "datasource_refresh.xml"
REVISION_XML = TEST_ASSET_DIR / "datasource_revision.xml"
UPDATE_XML = TEST_ASSET_DIR / "datasource_update.xml"
UPDATE_HYPER_DATA_XML = TEST_ASSET_DIR / "datasource_data_update.xml"
UPDATE_CONNECTION_XML = TEST_ASSET_DIR / "datasource_connection_update.xml"
UPDATE_CONNECTIONS_XML = TEST_ASSET_DIR / "datasource_connections_update.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_get(server) -> None:
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.datasources.baseurl, text=response_xml)
        all_datasources, pagination_item = server.datasources.get()

    assert 2 == pagination_item.total_available
    assert "e76a1461-3b1d-4588-bf1b-17551a879ad9" == all_datasources[0].id
    assert "dataengine" == all_datasources[0].datasource_type
    assert "SampleDsDescription" == all_datasources[0].description
    assert "SampleDS" == all_datasources[0].content_url
    assert 4096 == all_datasources[0].size
    assert "2016-08-11T21:22:40Z" == format_datetime(all_datasources[0].created_at)
    assert "2016-08-11T21:34:17Z" == format_datetime(all_datasources[0].updated_at)
    assert "default" == all_datasources[0].project_name
    assert "SampleDS" == all_datasources[0].name
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == all_datasources[0].project_id
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_datasources[0].owner_id
    assert "https://web.com" == all_datasources[0].webpage_url
    assert not all_datasources[0].encrypt_extracts
    assert all_datasources[0].has_extracts
    assert not all_datasources[0].use_remote_query_agent

    assert "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb" == all_datasources[1].id
    assert "dataengine" == all_datasources[1].datasource_type
    assert "description Sample" == all_datasources[1].description
    assert "Sampledatasource" == all_datasources[1].content_url
    assert 10240 == all_datasources[1].size
    assert "2016-08-04T21:31:55Z" == format_datetime(all_datasources[1].created_at)
    assert "2016-08-04T21:31:55Z" == format_datetime(all_datasources[1].updated_at)
    assert "default" == all_datasources[1].project_name
    assert "Sample datasource" == all_datasources[1].name
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == all_datasources[1].project_id
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_datasources[1].owner_id
    assert {"world", "indicators", "sample"} == all_datasources[1].tags
    assert "https://page.com" == all_datasources[1].webpage_url
    assert all_datasources[1].encrypt_extracts
    assert not all_datasources[1].has_extracts
    assert all_datasources[1].use_remote_query_agent


def test_get_before_signin(server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.datasources.get()


def test_get_empty(server) -> None:
    response_xml = GET_EMPTY_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.datasources.baseurl, text=response_xml)
        all_datasources, pagination_item = server.datasources.get()

    assert 0 == pagination_item.total_available
    assert [] == all_datasources


def test_get_by_id(server) -> None:
    response_xml = GET_BY_ID_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=response_xml)
        single_datasource = server.datasources.get_by_id("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")

    assert "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb" == single_datasource.id
    assert "dataengine" == single_datasource.datasource_type
    assert "abc description xyz" == single_datasource.description
    assert "Sampledatasource" == single_datasource.content_url
    assert "2016-08-04T21:31:55Z" == format_datetime(single_datasource.created_at)
    assert "2016-08-04T21:31:55Z" == format_datetime(single_datasource.updated_at)
    assert "default" == single_datasource.project_name
    assert "Sample datasource" == single_datasource.name
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == single_datasource.project_id
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == single_datasource.owner_id
    assert {"world", "indicators", "sample"} == single_datasource.tags
    assert TSC.DatasourceItem.AskDataEnablement.SiteDefault == single_datasource.ask_data_enablement


def test_update(server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=response_xml)
        single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "Sample datasource")
        single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_datasource._content_url = "Sampledatasource"
        single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        single_datasource.certified = True
        single_datasource.certification_note = "Warning, here be dragons."
        updated_datasource = server.datasources.update(single_datasource)

    assert updated_datasource.id == single_datasource.id
    assert updated_datasource.name == single_datasource.name
    assert updated_datasource.content_url == single_datasource.content_url
    assert updated_datasource.project_id == single_datasource.project_id
    assert updated_datasource.owner_id == single_datasource.owner_id
    assert updated_datasource.certified == single_datasource.certified
    assert updated_datasource.certification_note == single_datasource.certification_note


def test_update_copy_fields(server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=response_xml)
        single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "test")
        single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        single_datasource._project_name = "Tester"
        updated_datasource = server.datasources.update(single_datasource)

    assert single_datasource.tags == updated_datasource.tags
    assert single_datasource._project_name == updated_datasource._project_name


def test_update_tags(server) -> None:
    add_tags_xml = ADD_TAGS_XML.read_text()
    update_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.delete(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags/b", status_code=204)
        m.delete(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags/d", status_code=204)
        m.put(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags", text=add_tags_xml)
        m.put(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=update_xml)
        single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74")
        single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        single_datasource._initial_tags.update(["a", "b", "c", "d"])
        single_datasource.tags.update(["a", "c", "e"])
        updated_datasource = server.datasources.update(single_datasource)

    assert single_datasource.tags == updated_datasource.tags
    assert single_datasource._initial_tags == updated_datasource._initial_tags


def test_populate_connections(server) -> None:
    response_xml = POPULATE_CONNECTIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections", text=response_xml)
        single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "test")
        single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        server.datasources.populate_connections(single_datasource)
        assert "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb" == single_datasource.id
        connections: Optional[list[ConnectionItem]] = single_datasource.connections

    assert connections is not None
    ds1, ds2 = connections
    assert "be786ae0-d2bf-4a4b-9b34-e2de8d2d4488" == ds1.id
    assert "textscan" == ds1.connection_type
    assert "forty-two.net" == ds1.server_address
    assert "duo" == ds1.username
    assert True == ds1.embed_password
    assert ds1.datasource_id == single_datasource.id
    assert single_datasource.name == ds1.datasource_name
    assert "970e24bc-e200-4841-a3e9-66e7d122d77e" == ds2.id
    assert "sqlserver" == ds2.connection_type
    assert "database.com" == ds2.server_address
    assert "heero" == ds2.username
    assert False == ds2.embed_password
    assert ds2.datasource_id == single_datasource.id
    assert single_datasource.name == ds2.datasource_name


def test_update_connection(server) -> None:
    populate_xml = POPULATE_CONNECTIONS_XML.read_text()
    response_xml = UPDATE_CONNECTION_XML.read_text()

    with requests_mock.mock() as m:
        m.get(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections", text=populate_xml)
        m.put(
            server.datasources.baseurl
            + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections/be786ae0-d2bf-4a4b-9b34-e2de8d2d4488",
            text=response_xml,
        )
        single_datasource = TSC.DatasourceItem("be786ae0-d2bf-4a4b-9b34-e2de8d2d4488")
        single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        server.datasources.populate_connections(single_datasource)

        connection = single_datasource.connections[0]  # type: ignore[index]
        connection.server_address = "bar"
        connection.server_port = "9876"
        connection.username = "foo"
        new_connection = server.datasources.update_connection(single_datasource, connection)
        assert connection.id == new_connection.id
        assert connection.connection_type == new_connection.connection_type
        assert "bar" == new_connection.server_address
        assert "9876" == new_connection.server_port
        assert "foo" == new_connection.username


def test_update_connections(server) -> None:
    populate_xml = POPULATE_CONNECTIONS_XML.read_text()
    response_xml = UPDATE_CONNECTIONS_XML.read_text()

    with requests_mock.Mocker() as m:

        datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        connection_luids = ["be786ae0-d2bf-4a4b-9b34-e2de8d2d4488", "a1b2c3d4-e5f6-7a8b-9c0d-123456789abc"]

        datasource = TSC.DatasourceItem(datasource_id)
        datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        server.version = "3.26"

        url = f"{server.baseurl}/{datasource.id}/connections"
        m.get(
            "http://test/api/3.26/sites/dad65087-b08b-4603-af4e-2887b8aafc67/datasources/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections",
            text=populate_xml,
        )
        m.put(
            "http://test/api/3.26/sites/dad65087-b08b-4603-af4e-2887b8aafc67/datasources/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections",
            text=response_xml,
        )

        print("BASEURL:", server.baseurl)
        print("Calling PUT on:", f"{server.baseurl}/{datasource.id}/connections")

        connection_items = server.datasources.update_connections(
            datasource_item=datasource,
            connection_luids=connection_luids,
            authentication_type="auth-keypair",
            username="testuser",
            password="testpass",
            embed_password=True,
        )
        updated_ids = [conn.id for conn in connection_items]

        assert updated_ids == connection_luids
        assert "auth-keypair" == connection_items[0].auth_type


def test_populate_permissions(server) -> None:
    response_xml = POPULATE_PERMISSIONS_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.datasources.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)
        single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "test")
        single_datasource._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

        server.datasources.populate_permissions(single_datasource)
        permissions = single_datasource.permissions

        assert permissions is not None
        assert permissions[0].grantee.tag_name == "group"
        assert permissions[0].grantee.id == "5e5e1978-71fa-11e4-87dd-7382f5c437af"
        assert permissions[0].capabilities == {  # type: ignore[index]
            TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.ChangePermissions: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.Connect: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
        }

        assert permissions[1].grantee.tag_name == "user"
        assert permissions[1].grantee.id == "7c37ee24-c4b1-42b6-a154-eaeab7ee330a"
        assert permissions[1].capabilities == {  # type: ignore[index]
            TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
        }


def test_publish(server) -> None:
    response_xml = PUBLISH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.datasources.baseurl, text=response_xml)
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
        publish_mode = server.PublishMode.CreateNew

        new_datasource = server.datasources.publish(new_datasource, TEST_ASSET_DIR / "SampleDS.tds", mode=publish_mode)

    assert "e76a1461-3b1d-4588-bf1b-17551a879ad9" == new_datasource.id
    assert "SampleDS" == new_datasource.name
    assert "SampleDS" == new_datasource.content_url
    assert "dataengine" == new_datasource.datasource_type
    assert "2016-08-11T21:22:40Z" == format_datetime(new_datasource.created_at)
    assert "2016-08-17T23:37:08Z" == format_datetime(new_datasource.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_datasource.project_id
    assert "default" == new_datasource.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_datasource.owner_id


def test_publish_a_non_packaged_file_object(server) -> None:
    response_xml = PUBLISH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.datasources.baseurl, text=response_xml)
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
        publish_mode = server.PublishMode.CreateNew

        with open(TEST_ASSET_DIR / "SampleDS.tds", "rb") as file_object:
            new_datasource = server.datasources.publish(new_datasource, file_object, mode=publish_mode)

    assert "e76a1461-3b1d-4588-bf1b-17551a879ad9" == new_datasource.id
    assert "SampleDS" == new_datasource.name
    assert "SampleDS" == new_datasource.content_url
    assert "dataengine" == new_datasource.datasource_type
    assert "2016-08-11T21:22:40Z" == format_datetime(new_datasource.created_at)
    assert "2016-08-17T23:37:08Z" == format_datetime(new_datasource.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_datasource.project_id
    assert "default" == new_datasource.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_datasource.owner_id


def test_publish_a_packaged_file_object(server) -> None:
    response_xml = PUBLISH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(server.datasources.baseurl, text=response_xml)
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
        publish_mode = server.PublishMode.CreateNew

        # Create a dummy tdsx file in memory
        with BytesIO() as zip_archive:
            with ZipFile(zip_archive, "w") as zf:
                zf.write(str(TEST_ASSET_DIR / "SampleDS.tds"), arcname="SampleDS.tds")

            zip_archive.seek(0)

            new_datasource = server.datasources.publish(new_datasource, zip_archive, mode=publish_mode)

    assert "e76a1461-3b1d-4588-bf1b-17551a879ad9" == new_datasource.id
    assert "SampleDS" == new_datasource.name
    assert "SampleDS" == new_datasource.content_url
    assert "dataengine" == new_datasource.datasource_type
    assert "2016-08-11T21:22:40Z" == format_datetime(new_datasource.created_at)
    assert "2016-08-17T23:37:08Z" == format_datetime(new_datasource.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_datasource.project_id
    assert "default" == new_datasource.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_datasource.owner_id


def test_publish_async(server) -> None:
    server.version = "3.0"
    baseurl = server.datasources.baseurl
    response_xml = PUBLISH_XML_ASYNC.read_text()
    with requests_mock.mock() as m:
        m.post(baseurl, text=response_xml)
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
        publish_mode = server.PublishMode.CreateNew

        new_job = server.datasources.publish(
            new_datasource, TEST_ASSET_DIR / "SampleDS.tds", mode=publish_mode, as_job=True
        )

    assert "9a373058-af5f-4f83-8662-98b3e0228a73" == new_job.id
    assert "PublishDatasource" == new_job.type
    assert "0" == new_job.progress
    assert "2018-06-30T00:54:54Z" == format_datetime(new_job.created_at)
    assert 1 == new_job.finish_code


def test_publish_unnamed_file_object(server) -> None:
    new_datasource = TSC.DatasourceItem("test")
    publish_mode = server.PublishMode.CreateNew

    with open(TEST_ASSET_DIR / "SampleDS.tds", "rb") as file_object:
        with pytest.raises(ValueError):
            server.datasources.publish(new_datasource, file_object, publish_mode)


def test_refresh_id(server) -> None:
    server.version = "2.8"
    response_xml = REFRESH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/refresh",
            status_code=202,
            text=response_xml,
        )
        new_job = server.datasources.refresh("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")

    assert "7c3d599e-949f-44c3-94a1-f30ba85757e4" == new_job.id
    assert "RefreshExtract" == new_job.type
    assert None == new_job.progress
    assert "2020-03-05T22:05:32Z" == format_datetime(new_job.created_at)
    assert -1 == new_job.finish_code


def test_refresh_object(server) -> None:
    server.version = "2.8"
    datasource = TSC.DatasourceItem("")
    datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
    response_xml = REFRESH_XML.read_text()
    with requests_mock.mock() as m:
        m.post(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/refresh",
            status_code=202,
            text=response_xml,
        )
        new_job = server.datasources.refresh(datasource)

    # We only check the `id`; remaining fields are already tested in `test_refresh_id`
    assert "7c3d599e-949f-44c3-94a1-f30ba85757e4" == new_job.id


def test_datasource_refresh_request_empty(server) -> None:
    server.version = "2.8"
    item = TSC.DatasourceItem("")
    item._id = "1234"
    text = REFRESH_XML.read_text()

    def match_request_body(request):
        try:
            root = fromstring(request.body)
            assert root.tag == "tsRequest"
            assert len(root) == 0
            return True
        except Exception:
            return False

    with requests_mock.mock() as m:
        m.post(f"{server.datasources.baseurl}/1234/refresh", text=text, additional_matcher=match_request_body)


def test_update_hyper_data_datasource_object(server) -> None:
    """Calling `update_hyper_data` with a `DatasourceItem` should update that datasource"""
    server.version = "3.13"

    datasource = TSC.DatasourceItem("")
    datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
    response_xml = UPDATE_HYPER_DATA_XML.read_text()
    with requests_mock.mock() as m:
        m.patch(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/data",
            status_code=202,
            headers={"requestid": "test_id"},
            text=response_xml,
        )
        new_job = server.datasources.update_hyper_data(datasource, request_id="test_id", actions=[])

    assert "5c0ba560-c959-424e-b08a-f32ef0bfb737" == new_job.id
    assert "UpdateUploadedFile" == new_job.type
    assert None == new_job.progress
    assert "2021-09-18T09:40:12Z" == format_datetime(new_job.created_at)
    assert -1 == new_job.finish_code


def test_update_hyper_data_connection_object(server) -> None:
    """Calling `update_hyper_data` with a `ConnectionItem` should update that connection"""
    server.version = "3.13"

    connection = TSC.ConnectionItem()
    connection._datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
    connection._id = "7ecaccd8-39b0-4875-a77d-094f6e930019"
    response_xml = UPDATE_HYPER_DATA_XML.read_text()
    with requests_mock.mock() as m:
        m.patch(
            server.datasources.baseurl
            + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections/7ecaccd8-39b0-4875-a77d-094f6e930019/data",
            status_code=202,
            headers={"requestid": "test_id"},
            text=response_xml,
        )
        new_job = server.datasources.update_hyper_data(connection, request_id="test_id", actions=[])

    # We only check the `id`; remaining fields are already tested in `test_update_hyper_data_datasource_object`
    assert "5c0ba560-c959-424e-b08a-f32ef0bfb737" == new_job.id


def test_update_hyper_data_datasource_string(server) -> None:
    """For convenience, calling `update_hyper_data` with a `str` should update the datasource with the corresponding UUID"""
    server.version = "3.13"

    datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
    response_xml = UPDATE_HYPER_DATA_XML.read_text()
    with requests_mock.mock() as m:
        m.patch(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/data",
            status_code=202,
            headers={"requestid": "test_id"},
            text=response_xml,
        )
        new_job = server.datasources.update_hyper_data(datasource_id, request_id="test_id", actions=[])

    # We only check the `id`; remaining fields are already tested in `test_update_hyper_data_datasource_object`
    assert "5c0ba560-c959-424e-b08a-f32ef0bfb737" == new_job.id


def test_update_hyper_data_datasource_payload_file(server) -> None:
    """If `payload` is present, we upload it and associate the job with it"""
    server.version = "3.13"

    datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
    mock_upload_id = "10051:c3e56879876842d4b3600f20c1f79876-0:0"
    response_xml = UPDATE_HYPER_DATA_XML.read_text()
    with requests_mock.mock() as rm, unittest.mock.patch.object(Fileuploads, "upload", return_value=mock_upload_id):
        rm.patch(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/data?uploadSessionId=" + mock_upload_id,
            status_code=202,
            headers={"requestid": "test_id"},
            text=response_xml,
        )
        new_job = server.datasources.update_hyper_data(
            datasource_id, request_id="test_id", actions=[], payload=(TEST_ASSET_DIR / "World Indicators.hyper")
        )

    # We only check the `id`; remaining fields are already tested in `test_update_hyper_data_datasource_object`
    assert "5c0ba560-c959-424e-b08a-f32ef0bfb737" == new_job.id


def test_update_hyper_data_datasource_invalid_payload_file(server) -> None:
    """If `payload` points to a non-existing file, we report an error"""
    server.version = "3.13"
    datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
    with pytest.raises(IOError, match="File path does not lead to an existing file."):
        server.datasources.update_hyper_data(
            datasource_id, request_id="test_id", actions=[], payload="no/such/file.missing"
        )


def test_delete(server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", status_code=204)
        server.datasources.delete("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")


def test_download(server) -> None:
    with requests_mock.mock() as m:
        m.get(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content",
            headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
        )
        file_path = server.datasources.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")
        assert os.path.exists(file_path)
    os.remove(file_path)


def test_download_object(server) -> None:
    with BytesIO() as file_object:
        with requests_mock.mock() as m:
            m.get(
                server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content",
                headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
            )
            file_path = server.datasources.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", filepath=file_object)
            assert isinstance(file_path, BytesIO)


def test_download_sanitizes_name(server) -> None:
    filename = "Name,With,Commas.tds"
    disposition = f'name="tableau_workbook"; filename="{filename}"'
    with requests_mock.mock() as m:
        m.get(
            server.datasources.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
            headers={"Content-Disposition": disposition},
        )
        file_path = server.datasources.download("1f951daf-4061-451a-9df1-69a8062664f2")
        assert os.path.basename(file_path) == "NameWithCommas.tds"
        assert os.path.exists(file_path)
    os.remove(file_path)


def test_download_extract_only(server) -> None:
    # Pretend we're 2.5 for 'extract_only'
    server.version = "2.5"

    with requests_mock.mock() as m:
        m.get(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content?includeExtract=False",
            headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
            complete_qs=True,
        )
        file_path = server.datasources.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", include_extract=False)
        assert os.path.exists(file_path)
    os.remove(file_path)


def test_update_missing_id(server) -> None:
    single_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.datasources.update(single_datasource)


def test_publish_missing_path(server) -> None:
    new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
    with pytest.raises(IOError):
        server.datasources.publish(new_datasource, "", server.PublishMode.CreateNew)


def test_publish_missing_mode(server) -> None:
    new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
    with pytest.raises(ValueError):
        server.datasources.publish(new_datasource, TEST_ASSET_DIR / "SampleDS.tds", None)


def test_publish_invalid_file_type(server) -> None:
    new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
    with pytest.raises(ValueError):
        server.datasources.publish(
            new_datasource,
            TEST_ASSET_DIR / "SampleWB.twbx",
            server.PublishMode.Append,
        )


def test_publish_hyper_file_object_raises_exception(server) -> None:
    new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
    with open(TEST_ASSET_DIR / "World Indicators.hyper", "rb") as file_object:
        with pytest.raises(ValueError):
            server.datasources.publish(new_datasource, file_object, server.PublishMode.Append)


def test_publish_tde_file_object_raises_exception(server) -> None:
    new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
    tds_asset = TEST_ASSET_DIR / "Data" / "Tableau Samples" / "World Indicators.tde"
    with open(tds_asset, "rb") as file_object:
        with pytest.raises(ValueError):
            server.datasources.publish(new_datasource, file_object, server.PublishMode.Append)


def test_publish_file_object_of_unknown_type_raises_exception(server) -> None:
    new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")

    with BytesIO() as file_object:
        file_object.write(bytes.fromhex("89504E470D0A1A0A"))
        file_object.seek(0)
        with pytest.raises(ValueError):
            server.datasources.publish(new_datasource, file_object, server.PublishMode.Append)


def test_publish_multi_connection(server) -> None:
    new_datasource = TSC.DatasourceItem(name="Sample", project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    connection1 = TSC.ConnectionItem()
    connection1.server_address = "mysql.test.com"
    connection1.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)
    connection2 = TSC.ConnectionItem()
    connection2.server_address = "pgsql.test.com"
    connection2.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)

    response = RequestFactory.Datasource._generate_xml(new_datasource, connections=[connection1, connection2])
    # Can't use ConnectionItem parser due to xml namespace problems
    connection_results = fromstring(response).findall(".//connection")

    assert connection_results[0].get("serverAddress", None) == "mysql.test.com"
    assert connection_results[0].find("connectionCredentials").get("name", None) == "test"
    assert connection_results[1].get("serverAddress", None) == "pgsql.test.com"
    assert connection_results[1].find("connectionCredentials").get("password", None) == "secret"


def test_publish_single_connection(server) -> None:
    new_datasource = TSC.DatasourceItem(name="Sample", project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    connection_creds = TSC.ConnectionCredentials("test", "secret", True)

    response = RequestFactory.Datasource._generate_xml(new_datasource, connection_credentials=connection_creds)
    #  Can't use ConnectionItem parser due to xml namespace problems
    credentials = fromstring(response).findall(".//connectionCredentials")

    assert len(credentials) == 1
    assert credentials[0].get("name", None) == "test"
    assert credentials[0].get("password", None) == "secret"
    assert credentials[0].get("embed", None) == "true"


def test_credentials_and_multi_connect_raises_exception(server) -> None:
    new_datasource = TSC.DatasourceItem(name="Sample", project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

    connection_creds = TSC.ConnectionCredentials("test", "secret", True)

    connection1 = TSC.ConnectionItem()
    connection1.server_address = "mysql.test.com"
    connection1.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)

    with pytest.raises(RuntimeError):
        response = RequestFactory.Datasource._generate_xml(
            new_datasource, connection_credentials=connection_creds, connections=[connection1]
        )


def test_synchronous_publish_timeout_error(server) -> None:
    with requests_mock.mock() as m:
        m.register_uri("POST", server.datasources.baseurl, status_code=504)

        new_datasource = TSC.DatasourceItem(project_id="")
        publish_mode = server.PublishMode.CreateNew
        # http://test/api/2.4/sites/dad65087-b08b-4603-af4e-2887b8aafc67/datasources?datasourceType=tds

        with pytest.raises(InternalServerError, match="Please use asynchronous publishing to avoid timeouts."):
            server.datasources.publish(
                new_datasource,
                TEST_ASSET_DIR / "SampleDS.tds",
                publish_mode,
            )


def test_delete_extracts(server) -> None:
    server.version = "3.10"
    with requests_mock.mock() as m:
        m.post(server.datasources.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/deleteExtract", status_code=200)
        server.datasources.delete_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")


def test_create_extracts(server) -> None:
    server.version = "3.10"

    response_xml = PUBLISH_XML_ASYNC.read_text()
    with requests_mock.mock() as m:
        m.post(
            server.datasources.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract",
            status_code=200,
            text=response_xml,
        )
        server.datasources.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")


def test_create_extracts_encrypted(server) -> None:
    server.version = "3.10"

    response_xml = PUBLISH_XML_ASYNC.read_text()
    with requests_mock.mock() as m:
        m.post(
            server.datasources.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract",
            status_code=200,
            text=response_xml,
        )
        server.datasources.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42", True)


def test_revisions(server) -> None:
    datasource = TSC.DatasourceItem("project", "test")
    datasource._id = "06b944d2-959d-4604-9305-12323c95e70e"

    response_xml = REVISION_XML.read_text()
    with requests_mock.mock() as m:
        m.get(f"{server.datasources.baseurl}/{datasource.id}/revisions", text=response_xml)
        server.datasources.populate_revisions(datasource)
        revisions = datasource.revisions

    assert len(revisions) == 3
    assert "2016-07-26T20:34:56Z" == format_datetime(revisions[0].created_at)
    assert "2016-07-27T20:34:56Z" == format_datetime(revisions[1].created_at)
    assert "2016-07-28T20:34:56Z" == format_datetime(revisions[2].created_at)

    assert False == revisions[0].deleted
    assert False == revisions[0].current
    assert False == revisions[1].deleted
    assert False == revisions[1].current
    assert False == revisions[2].deleted
    assert True == revisions[2].current

    assert "Cassie" == revisions[0].user_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == revisions[0].user_id
    assert revisions[1].user_name is None
    assert revisions[1].user_id is None
    assert "Cassie" == revisions[2].user_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == revisions[2].user_id


def test_delete_revision(server) -> None:
    datasource = TSC.DatasourceItem("project", "test")
    datasource._id = "06b944d2-959d-4604-9305-12323c95e70e"

    with requests_mock.mock() as m:
        m.delete(f"{server.datasources.baseurl}/{datasource.id}/revisions/3")
        server.datasources.delete_revision(datasource.id, "3")


def test_download_revision(server) -> None:
    with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
        m.get(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/revisions/3/content",
            headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
        )
        file_path = server.datasources.download_revision("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", "3", td)
        assert os.path.exists(file_path)


def test_bad_download_response(server) -> None:
    with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
        m.get(
            server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content",
            headers={"Content-Disposition": '''name="tableau_datasource"; filename*=UTF-8''"Sample datasource.tds"'''},
        )
        file_path = server.datasources.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", td)
        assert os.path.exists(file_path)


def test_get_datasource_all_fields(server) -> None:
    ro = TSC.RequestOptions()
    ro.all_fields = True
    with requests_mock.mock() as m:
        m.get(f"{server.datasources.baseurl}?fields=_all_", text=GET_XML_ALL_FIELDS.read_text())
        datasources, _ = server.datasources.get(req_options=ro)

    assert datasources[0].connected_workbooks_count == 0
    assert datasources[0].content_url == "SuperstoreDatasource"
    assert datasources[0].created_at == parse_datetime("2024-02-14T04:42:13Z")
    assert not datasources[0].encrypt_extracts
    assert datasources[0].favorites_total == 0
    assert not datasources[0].has_alert
    assert not datasources[0].has_extracts
    assert datasources[0].id == "a71cdd15-3a23-4ec1-b3ce-9956f5e00bb7"
    assert not datasources[0].certified
    assert datasources[0].is_published
    assert datasources[0].name == "Superstore Datasource"
    assert datasources[0].size == 1
    assert datasources[0].datasource_type == "excel-direct"
    assert datasources[0].updated_at == parse_datetime("2024-02-14T04:42:14Z")
    assert not datasources[0].use_remote_query_agent
    assert datasources[0].server_name == "localhost"
    assert datasources[0].webpage_url == "https://10ax.online.tableau.com/#/site/example/datasources/3566752"
    assert isinstance(datasources[0].project, TSC.ProjectItem)
    assert datasources[0].project.id == "669ca36b-492e-4ccf-bca1-3614fe6a9d7a"
    assert datasources[0].project.name == "Samples"
    assert datasources[0].project.description == "This project includes automatically uploaded samples."
    assert datasources[0].owner.email == "bob@example.com"
    assert isinstance(datasources[0].owner, TSC.UserItem)
    assert datasources[0].owner.fullname == "Bob Smith"
    assert datasources[0].owner.id == "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
    assert datasources[0].owner.last_login == parse_datetime("2025-02-04T06:39:20Z")
    assert datasources[0].owner.name == "bob@example.com"
    assert datasources[0].owner.site_role == "SiteAdministratorCreator"


def test_update_description(server: TSC.Server) -> None:
    response_xml = UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.datasources.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=response_xml)
        single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "Sample datasource")
        single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_datasource._content_url = "Sampledatasource"
        single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        single_datasource.certified = True
        single_datasource.certification_note = "Warning, here be dragons."
        single_datasource.description = "Sample description"
        _ = server.datasources.update(single_datasource)

        history = m.request_history[0]
    body = fromstring(history.body)
    ds_elem = body.find(".//datasource")
    assert ds_elem is not None
    assert ds_elem.attrib["description"] == "Sample description"
