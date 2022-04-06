import os
import tempfile
import unittest
from io import BytesIO
from zipfile import ZipFile

import requests_mock
from defusedxml.ElementTree import fromstring

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.endpoint.fileuploads_endpoint import Fileuploads
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import read_xml_asset, read_xml_assets, asset

ADD_TAGS_XML = "datasource_add_tags.xml"
GET_XML = "datasource_get.xml"
GET_EMPTY_XML = "datasource_get_empty.xml"
GET_BY_ID_XML = "datasource_get_by_id.xml"
POPULATE_CONNECTIONS_XML = "datasource_populate_connections.xml"
POPULATE_PERMISSIONS_XML = "datasource_populate_permissions.xml"
PUBLISH_XML = "datasource_publish.xml"
PUBLISH_XML_ASYNC = "datasource_publish_async.xml"
REFRESH_XML = "datasource_refresh.xml"
REVISION_XML = "datasource_revision.xml"
UPDATE_XML = "datasource_update.xml"
UPDATE_HYPER_DATA_XML = "datasource_data_update.xml"
UPDATE_CONNECTION_XML = "datasource_connection_update.xml"


class DatasourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.datasources.baseurl

    def test_get(self) -> None:
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_datasources, pagination_item = self.server.datasources.get()

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("e76a1461-3b1d-4588-bf1b-17551a879ad9", all_datasources[0].id)
        self.assertEqual("dataengine", all_datasources[0].datasource_type)
        self.assertEqual("SampleDsDescription", all_datasources[0].description)
        self.assertEqual("SampleDS", all_datasources[0].content_url)
        self.assertEqual("2016-08-11T21:22:40Z", format_datetime(all_datasources[0].created_at))
        self.assertEqual("2016-08-11T21:34:17Z", format_datetime(all_datasources[0].updated_at))
        self.assertEqual("default", all_datasources[0].project_name)
        self.assertEqual("SampleDS", all_datasources[0].name)
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", all_datasources[0].project_id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_datasources[0].owner_id)
        self.assertEqual("https://web.com", all_datasources[0].webpage_url)
        self.assertFalse(all_datasources[0].encrypt_extracts)
        self.assertTrue(all_datasources[0].has_extracts)
        self.assertFalse(all_datasources[0].use_remote_query_agent)

        self.assertEqual("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", all_datasources[1].id)
        self.assertEqual("dataengine", all_datasources[1].datasource_type)
        self.assertEqual("description Sample", all_datasources[1].description)
        self.assertEqual("Sampledatasource", all_datasources[1].content_url)
        self.assertEqual("2016-08-04T21:31:55Z", format_datetime(all_datasources[1].created_at))
        self.assertEqual("2016-08-04T21:31:55Z", format_datetime(all_datasources[1].updated_at))
        self.assertEqual("default", all_datasources[1].project_name)
        self.assertEqual("Sample datasource", all_datasources[1].name)
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", all_datasources[1].project_id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", all_datasources[1].owner_id)
        self.assertEqual(set(["world", "indicators", "sample"]), all_datasources[1].tags)
        self.assertEqual("https://page.com", all_datasources[1].webpage_url)
        self.assertTrue(all_datasources[1].encrypt_extracts)
        self.assertFalse(all_datasources[1].has_extracts)
        self.assertTrue(all_datasources[1].use_remote_query_agent)

    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        self.assertRaises(TSC.NotSignedInError, self.server.datasources.get)

    def test_get_empty(self) -> None:
        response_xml = read_xml_asset(GET_EMPTY_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_datasources, pagination_item = self.server.datasources.get()

        self.assertEqual(0, pagination_item.total_available)
        self.assertEqual([], all_datasources)

    def test_get_by_id(self) -> None:
        response_xml = read_xml_asset(GET_BY_ID_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=response_xml)
            single_datasource = self.server.datasources.get_by_id("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")

        self.assertEqual("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", single_datasource.id)
        self.assertEqual("dataengine", single_datasource.datasource_type)
        self.assertEqual("abc description xyz", single_datasource.description)
        self.assertEqual("Sampledatasource", single_datasource.content_url)
        self.assertEqual("2016-08-04T21:31:55Z", format_datetime(single_datasource.created_at))
        self.assertEqual("2016-08-04T21:31:55Z", format_datetime(single_datasource.updated_at))
        self.assertEqual("default", single_datasource.project_name)
        self.assertEqual("Sample datasource", single_datasource.name)
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", single_datasource.project_id)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", single_datasource.owner_id)
        self.assertEqual(set(["world", "indicators", "sample"]), single_datasource.tags)
        self.assertEqual(TSC.DatasourceItem.AskDataEnablement.SiteDefault, single_datasource.ask_data_enablement)

    def test_update(self) -> None:
        response_xml = read_xml_asset(UPDATE_XML)
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=response_xml)
            single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "Sample datasource")
            single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_datasource._content_url = "Sampledatasource"
            single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
            single_datasource.certified = True
            single_datasource.certification_note = "Warning, here be dragons."
            updated_datasource = self.server.datasources.update(single_datasource)

        self.assertEqual(updated_datasource.id, single_datasource.id)
        self.assertEqual(updated_datasource.name, single_datasource.name)
        self.assertEqual(updated_datasource.content_url, single_datasource.content_url)
        self.assertEqual(updated_datasource.project_id, single_datasource.project_id)
        self.assertEqual(updated_datasource.owner_id, single_datasource.owner_id)
        self.assertEqual(updated_datasource.certified, single_datasource.certified)
        self.assertEqual(updated_datasource.certification_note, single_datasource.certification_note)

    def test_update_copy_fields(self) -> None:
        with open(asset(UPDATE_XML), "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=response_xml)
            single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "test")
            single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
            single_datasource._project_name = "Tester"
            updated_datasource = self.server.datasources.update(single_datasource)

        self.assertEqual(single_datasource.tags, updated_datasource.tags)
        self.assertEqual(single_datasource._project_name, updated_datasource._project_name)

    def test_update_tags(self) -> None:
        add_tags_xml, update_xml = read_xml_assets(ADD_TAGS_XML, UPDATE_XML)
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags", text=add_tags_xml)
            m.delete(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags/b", status_code=204)
            m.delete(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/tags/d", status_code=204)
            m.put(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", text=update_xml)
            single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74")
            single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
            single_datasource._initial_tags.update(["a", "b", "c", "d"])
            single_datasource.tags.update(["a", "c", "e"])
            updated_datasource = self.server.datasources.update(single_datasource)

        self.assertEqual(single_datasource.tags, updated_datasource.tags)
        self.assertEqual(single_datasource._initial_tags, updated_datasource._initial_tags)

    def test_populate_connections(self) -> None:
        response_xml = read_xml_asset(POPULATE_CONNECTIONS_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections", text=response_xml)
            single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "test")
            single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
            self.server.datasources.populate_connections(single_datasource)
            self.assertEqual("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", single_datasource.id)
            connections = single_datasource.connections

        self.assertTrue(connections)
        ds1, ds2 = connections
        self.assertEqual("be786ae0-d2bf-4a4b-9b34-e2de8d2d4488", ds1.id)
        self.assertEqual("textscan", ds1.connection_type)
        self.assertEqual("forty-two.net", ds1.server_address)
        self.assertEqual("duo", ds1.username)
        self.assertEqual(True, ds1.embed_password)
        self.assertEqual("970e24bc-e200-4841-a3e9-66e7d122d77e", ds2.id)
        self.assertEqual("sqlserver", ds2.connection_type)
        self.assertEqual("database.com", ds2.server_address)
        self.assertEqual("heero", ds2.username)
        self.assertEqual(False, ds2.embed_password)

    def test_update_connection(self) -> None:
        populate_xml, response_xml = read_xml_assets(POPULATE_CONNECTIONS_XML, UPDATE_CONNECTION_XML)

        with requests_mock.mock() as m:
            m.get(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections", text=populate_xml)
            m.put(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections/be786ae0-d2bf-4a4b-9b34-e2de8d2d4488",
                text=response_xml,
            )
            single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74")
            single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
            self.server.datasources.populate_connections(single_datasource)

            connection = single_datasource.connections[0]  # type: ignore[index]
            connection.server_address = "bar"
            connection.server_port = "9876"
            connection.username = "foo"
            new_connection = self.server.datasources.update_connection(single_datasource, connection)
            self.assertEqual(connection.id, new_connection.id)
            self.assertEqual(connection.connection_type, new_connection.connection_type)
            self.assertEqual("bar", new_connection.server_address)
            self.assertEqual("9876", new_connection.server_port)
            self.assertEqual("foo", new_connection.username)

    def test_populate_permissions(self) -> None:
        with open(asset(POPULATE_PERMISSIONS_XML), "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)
            single_datasource = TSC.DatasourceItem("1d0304cd-3796-429f-b815-7258370b9b74", "test")
            single_datasource._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

            self.server.datasources.populate_permissions(single_datasource)
            permissions = single_datasource.permissions

            self.assertEqual(permissions[0].grantee.tag_name, "group")  # type: ignore[index]
            self.assertEqual(permissions[0].grantee.id, "5e5e1978-71fa-11e4-87dd-7382f5c437af")  # type: ignore[index]
            self.assertDictEqual(
                permissions[0].capabilities,  # type: ignore[index]
                {
                    TSC.Permission.Capability.Delete: TSC.Permission.Mode.Deny,
                    TSC.Permission.Capability.ChangePermissions: TSC.Permission.Mode.Deny,
                    TSC.Permission.Capability.Connect: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
                },
            )

            self.assertEqual(permissions[1].grantee.tag_name, "user")  # type: ignore[index]
            self.assertEqual(permissions[1].grantee.id, "7c37ee24-c4b1-42b6-a154-eaeab7ee330a")  # type: ignore[index]
            self.assertDictEqual(
                permissions[1].capabilities,  # type: ignore[index]
                {
                    TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
                },
            )

    def test_publish(self) -> None:
        response_xml = read_xml_asset(PUBLISH_XML)
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
            publish_mode = self.server.PublishMode.CreateNew

            new_datasource = self.server.datasources.publish(new_datasource, asset("SampleDS.tds"), mode=publish_mode)

        self.assertEqual("e76a1461-3b1d-4588-bf1b-17551a879ad9", new_datasource.id)
        self.assertEqual("SampleDS", new_datasource.name)
        self.assertEqual("SampleDS", new_datasource.content_url)
        self.assertEqual("dataengine", new_datasource.datasource_type)
        self.assertEqual("2016-08-11T21:22:40Z", format_datetime(new_datasource.created_at))
        self.assertEqual("2016-08-17T23:37:08Z", format_datetime(new_datasource.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", new_datasource.project_id)
        self.assertEqual("default", new_datasource.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", new_datasource.owner_id)

    def test_publish_a_non_packaged_file_object(self) -> None:
        response_xml = read_xml_asset(PUBLISH_XML)
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
            publish_mode = self.server.PublishMode.CreateNew

            with open(asset("SampleDS.tds"), "rb") as file_object:
                new_datasource = self.server.datasources.publish(new_datasource, file_object, mode=publish_mode)

        self.assertEqual("e76a1461-3b1d-4588-bf1b-17551a879ad9", new_datasource.id)
        self.assertEqual("SampleDS", new_datasource.name)
        self.assertEqual("SampleDS", new_datasource.content_url)
        self.assertEqual("dataengine", new_datasource.datasource_type)
        self.assertEqual("2016-08-11T21:22:40Z", format_datetime(new_datasource.created_at))
        self.assertEqual("2016-08-17T23:37:08Z", format_datetime(new_datasource.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", new_datasource.project_id)
        self.assertEqual("default", new_datasource.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", new_datasource.owner_id)

    def test_publish_a_packaged_file_object(self) -> None:
        response_xml = read_xml_asset(PUBLISH_XML)
        with requests_mock.mock() as m:
            m.post(self.baseurl, text=response_xml)
            new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
            publish_mode = self.server.PublishMode.CreateNew

            # Create a dummy tdsx file in memory
            with BytesIO() as zip_archive:
                with ZipFile(zip_archive, "w") as zf:
                    zf.write(asset("SampleDS.tds"))

                zip_archive.seek(0)

                new_datasource = self.server.datasources.publish(new_datasource, zip_archive, mode=publish_mode)

        self.assertEqual("e76a1461-3b1d-4588-bf1b-17551a879ad9", new_datasource.id)
        self.assertEqual("SampleDS", new_datasource.name)
        self.assertEqual("SampleDS", new_datasource.content_url)
        self.assertEqual("dataengine", new_datasource.datasource_type)
        self.assertEqual("2016-08-11T21:22:40Z", format_datetime(new_datasource.created_at))
        self.assertEqual("2016-08-17T23:37:08Z", format_datetime(new_datasource.updated_at))
        self.assertEqual("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", new_datasource.project_id)
        self.assertEqual("default", new_datasource.project_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", new_datasource.owner_id)

    def test_publish_async(self) -> None:
        self.server.version = "3.0"
        baseurl = self.server.datasources.baseurl
        response_xml = read_xml_asset(PUBLISH_XML_ASYNC)
        with requests_mock.mock() as m:
            m.post(baseurl, text=response_xml)
            new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "SampleDS")
            publish_mode = self.server.PublishMode.CreateNew

            new_job = self.server.datasources.publish(
                new_datasource, asset("SampleDS.tds"), mode=publish_mode, as_job=True
            )

        self.assertEqual("9a373058-af5f-4f83-8662-98b3e0228a73", new_job.id)
        self.assertEqual("PublishDatasource", new_job.type)
        self.assertEqual("0", new_job.progress)
        self.assertEqual("2018-06-30T00:54:54Z", format_datetime(new_job.created_at))
        self.assertEqual(1, new_job.finish_code)

    def test_publish_unnamed_file_object(self) -> None:
        new_datasource = TSC.DatasourceItem("test")
        publish_mode = self.server.PublishMode.CreateNew

        with open(asset("SampleDS.tds"), "rb") as file_object:
            self.assertRaises(ValueError, self.server.datasources.publish, new_datasource, file_object, publish_mode)

    def test_refresh_id(self) -> None:
        self.server.version = "2.8"
        self.baseurl = self.server.datasources.baseurl
        response_xml = read_xml_asset(REFRESH_XML)
        with requests_mock.mock() as m:
            m.post(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/refresh", status_code=202, text=response_xml)
            new_job = self.server.datasources.refresh("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")

        self.assertEqual("7c3d599e-949f-44c3-94a1-f30ba85757e4", new_job.id)
        self.assertEqual("RefreshExtract", new_job.type)
        self.assertEqual(None, new_job.progress)
        self.assertEqual("2020-03-05T22:05:32Z", format_datetime(new_job.created_at))
        self.assertEqual(-1, new_job.finish_code)

    def test_refresh_object(self) -> None:
        self.server.version = "2.8"
        self.baseurl = self.server.datasources.baseurl
        datasource = TSC.DatasourceItem("")
        datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        response_xml = read_xml_asset(REFRESH_XML)
        with requests_mock.mock() as m:
            m.post(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/refresh", status_code=202, text=response_xml)
            new_job = self.server.datasources.refresh(datasource)

        # We only check the `id`; remaining fields are already tested in `test_refresh_id`
        self.assertEqual("7c3d599e-949f-44c3-94a1-f30ba85757e4", new_job.id)

    def test_update_hyper_data_datasource_object(self) -> None:
        """Calling `update_hyper_data` with a `DatasourceItem` should update that datasource"""
        self.server.version = "3.13"
        self.baseurl = self.server.datasources.baseurl

        datasource = TSC.DatasourceItem("")
        datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        response_xml = read_xml_asset(UPDATE_HYPER_DATA_XML)
        with requests_mock.mock() as m:
            m.patch(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/data",
                status_code=202,
                headers={"requestid": "test_id"},
                text=response_xml,
            )
            new_job = self.server.datasources.update_hyper_data(datasource, request_id="test_id", actions=[])

        self.assertEqual("5c0ba560-c959-424e-b08a-f32ef0bfb737", new_job.id)
        self.assertEqual("UpdateUploadedFile", new_job.type)
        self.assertEqual(None, new_job.progress)
        self.assertEqual("2021-09-18T09:40:12Z", format_datetime(new_job.created_at))
        self.assertEqual(-1, new_job.finish_code)

    def test_update_hyper_data_connection_object(self) -> None:
        """Calling `update_hyper_data` with a `ConnectionItem` should update that connection"""
        self.server.version = "3.13"
        self.baseurl = self.server.datasources.baseurl

        connection = TSC.ConnectionItem()
        connection._datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        connection._id = "7ecaccd8-39b0-4875-a77d-094f6e930019"
        response_xml = read_xml_asset(UPDATE_HYPER_DATA_XML)
        with requests_mock.mock() as m:
            m.patch(
                self.baseurl
                + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections/7ecaccd8-39b0-4875-a77d-094f6e930019/data",
                status_code=202,
                headers={"requestid": "test_id"},
                text=response_xml,
            )
            new_job = self.server.datasources.update_hyper_data(connection, request_id="test_id", actions=[])

        # We only check the `id`; remaining fields are already tested in `test_update_hyper_data_datasource_object`
        self.assertEqual("5c0ba560-c959-424e-b08a-f32ef0bfb737", new_job.id)

    def test_update_hyper_data_datasource_string(self) -> None:
        """For convenience, calling `update_hyper_data` with a `str` should update the datasource with the corresponding UUID"""
        self.server.version = "3.13"
        self.baseurl = self.server.datasources.baseurl

        datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        response_xml = read_xml_asset(UPDATE_HYPER_DATA_XML)
        with requests_mock.mock() as m:
            m.patch(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/data",
                status_code=202,
                headers={"requestid": "test_id"},
                text=response_xml,
            )
            new_job = self.server.datasources.update_hyper_data(datasource_id, request_id="test_id", actions=[])

        # We only check the `id`; remaining fields are already tested in `test_update_hyper_data_datasource_object`
        self.assertEqual("5c0ba560-c959-424e-b08a-f32ef0bfb737", new_job.id)

    def test_update_hyper_data_datasource_payload_file(self) -> None:
        """If `payload` is present, we upload it and associate the job with it"""
        self.server.version = "3.13"
        self.baseurl = self.server.datasources.baseurl

        datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        mock_upload_id = "10051:c3e56879876842d4b3600f20c1f79876-0:0"
        response_xml = read_xml_asset(UPDATE_HYPER_DATA_XML)
        with requests_mock.mock() as rm, unittest.mock.patch.object(Fileuploads, "upload", return_value=mock_upload_id):
            rm.patch(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/data?uploadSessionId=" + mock_upload_id,
                status_code=202,
                headers={"requestid": "test_id"},
                text=response_xml,
            )
            new_job = self.server.datasources.update_hyper_data(
                datasource_id, request_id="test_id", actions=[], payload=asset("World Indicators.hyper")
            )

        # We only check the `id`; remaining fields are already tested in `test_update_hyper_data_datasource_object`
        self.assertEqual("5c0ba560-c959-424e-b08a-f32ef0bfb737", new_job.id)

    def test_update_hyper_data_datasource_invalid_payload_file(self) -> None:
        """If `payload` points to a non-existing file, we report an error"""
        self.server.version = "3.13"
        self.baseurl = self.server.datasources.baseurl
        datasource_id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
        with self.assertRaises(IOError) as cm:
            self.server.datasources.update_hyper_data(
                datasource_id, request_id="test_id", actions=[], payload="no/such/file.missing"
            )
        exception = cm.exception
        self.assertEqual(str(exception), "File path does not lead to an existing file.")

    def test_delete(self) -> None:
        with requests_mock.mock() as m:
            m.delete(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", status_code=204)
            self.server.datasources.delete("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")

    def test_download(self) -> None:
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content",
                headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
            )
            file_path = self.server.datasources.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb")
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_download_sanitizes_name(self) -> None:
        filename = "Name,With,Commas.tds"
        disposition = 'name="tableau_workbook"; filename="{}"'.format(filename)
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
                headers={"Content-Disposition": disposition},
            )
            file_path = self.server.datasources.download("1f951daf-4061-451a-9df1-69a8062664f2")
            self.assertEqual(os.path.basename(file_path), "NameWithCommas.tds")
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_download_extract_only(self) -> None:
        # Pretend we're 2.5 for 'extract_only'
        self.server.version = "2.5"
        self.baseurl = self.server.datasources.baseurl

        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content?includeExtract=False",
                headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
                complete_qs=True,
            )
            file_path = self.server.datasources.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", include_extract=False)
            self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    def test_update_missing_id(self) -> None:
        single_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
        self.assertRaises(TSC.MissingRequiredFieldError, self.server.datasources.update, single_datasource)

    def test_publish_missing_path(self) -> None:
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
        self.assertRaises(
            IOError, self.server.datasources.publish, new_datasource, "", self.server.PublishMode.CreateNew
        )

    def test_publish_missing_mode(self) -> None:
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
        self.assertRaises(ValueError, self.server.datasources.publish, new_datasource, asset("SampleDS.tds"), None)

    def test_publish_invalid_file_type(self) -> None:
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
        self.assertRaises(
            ValueError,
            self.server.datasources.publish,
            new_datasource,
            asset("SampleWB.twbx"),
            self.server.PublishMode.Append,
        )

    def test_publish_hyper_file_object_raises_exception(self) -> None:
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
        with open(asset("World Indicators.hyper"), "rb") as file_object:
            self.assertRaises(
                ValueError, self.server.datasources.publish, new_datasource, file_object, self.server.PublishMode.Append
            )

    def test_publish_tde_file_object_raises_exception(self) -> None:

        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")
        tds_asset = asset(os.path.join("Data", "Tableau Samples", "World Indicators.tde"))
        with open(tds_asset, "rb") as file_object:
            self.assertRaises(
                ValueError, self.server.datasources.publish, new_datasource, file_object, self.server.PublishMode.Append
            )

    def test_publish_file_object_of_unknown_type_raises_exception(self) -> None:
        new_datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760", "test")

        with BytesIO() as file_object:
            file_object.write(bytes.fromhex("89504E470D0A1A0A"))
            file_object.seek(0)
            self.assertRaises(
                ValueError, self.server.datasources.publish, new_datasource, file_object, self.server.PublishMode.Append
            )

    def test_publish_multi_connection(self) -> None:
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

        self.assertEqual(connection_results[0].get("serverAddress", None), "mysql.test.com")
        self.assertEqual(connection_results[0].find("connectionCredentials").get("name", None), "test")  # type: ignore[union-attr]
        self.assertEqual(connection_results[1].get("serverAddress", None), "pgsql.test.com")
        self.assertEqual(connection_results[1].find("connectionCredentials").get("password", None), "secret")  # type: ignore[union-attr]

    def test_publish_single_connection(self) -> None:
        new_datasource = TSC.DatasourceItem(name="Sample", project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
        connection_creds = TSC.ConnectionCredentials("test", "secret", True)

        response = RequestFactory.Datasource._generate_xml(new_datasource, connection_credentials=connection_creds)
        #  Can't use ConnectionItem parser due to xml namespace problems
        credentials = fromstring(response).findall(".//connectionCredentials")

        self.assertEqual(len(credentials), 1)
        self.assertEqual(credentials[0].get("name", None), "test")
        self.assertEqual(credentials[0].get("password", None), "secret")
        self.assertEqual(credentials[0].get("embed", None), "true")

    def test_credentials_and_multi_connect_raises_exception(self) -> None:
        new_datasource = TSC.DatasourceItem(name="Sample", project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")

        connection_creds = TSC.ConnectionCredentials("test", "secret", True)

        connection1 = TSC.ConnectionItem()
        connection1.server_address = "mysql.test.com"
        connection1.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)

        with self.assertRaises(RuntimeError):
            response = RequestFactory.Datasource._generate_xml(
                new_datasource, connection_credentials=connection_creds, connections=[connection1]
            )

    def test_synchronous_publish_timeout_error(self) -> None:
        with requests_mock.mock() as m:
            m.register_uri("POST", self.baseurl, status_code=504)

            new_datasource = TSC.DatasourceItem(project_id="")
            publish_mode = self.server.PublishMode.CreateNew

            self.assertRaisesRegex(
                InternalServerError,
                "Please use asynchronous publishing to avoid timeouts.",
                self.server.datasources.publish,
                new_datasource,
                asset("SampleDS.tds"),
                publish_mode,
            )

    def test_delete_extracts(self) -> None:
        self.server.version = "3.10"
        self.baseurl = self.server.datasources.baseurl
        with requests_mock.mock() as m:
            m.post(self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/deleteExtract", status_code=200)
            self.server.datasources.delete_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    def test_create_extracts(self) -> None:
        self.server.version = "3.10"
        self.baseurl = self.server.datasources.baseurl

        response_xml = read_xml_asset(PUBLISH_XML_ASYNC)
        with requests_mock.mock() as m:
            m.post(
                self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract", status_code=200, text=response_xml
            )
            self.server.datasources.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    def test_create_extracts_encrypted(self) -> None:
        self.server.version = "3.10"
        self.baseurl = self.server.datasources.baseurl

        response_xml = read_xml_asset(PUBLISH_XML_ASYNC)
        with requests_mock.mock() as m:
            m.post(
                self.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract", status_code=200, text=response_xml
            )
            self.server.datasources.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42", True)

    def test_revisions(self) -> None:
        datasource = TSC.DatasourceItem("project", "test")
        datasource._id = "06b944d2-959d-4604-9305-12323c95e70e"

        response_xml = read_xml_asset(REVISION_XML)
        with requests_mock.mock() as m:
            m.get("{0}/{1}/revisions".format(self.baseurl, datasource.id), text=response_xml)
            self.server.datasources.populate_revisions(datasource)
            revisions = datasource.revisions

        self.assertEqual(len(revisions), 3)
        self.assertEqual("2016-07-26T20:34:56Z", format_datetime(revisions[0].created_at))
        self.assertEqual("2016-07-27T20:34:56Z", format_datetime(revisions[1].created_at))
        self.assertEqual("2016-07-28T20:34:56Z", format_datetime(revisions[2].created_at))

        self.assertEqual(False, revisions[0].deleted)
        self.assertEqual(False, revisions[0].current)
        self.assertEqual(False, revisions[1].deleted)
        self.assertEqual(False, revisions[1].current)
        self.assertEqual(False, revisions[2].deleted)
        self.assertEqual(True, revisions[2].current)

        self.assertEqual("Cassie", revisions[0].user_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", revisions[0].user_id)
        self.assertIsNone(revisions[1].user_name)
        self.assertIsNone(revisions[1].user_id)
        self.assertEqual("Cassie", revisions[2].user_name)
        self.assertEqual("5de011f8-5aa9-4d5b-b991-f462c8dd6bb7", revisions[2].user_id)

    def test_delete_revision(self) -> None:
        datasource = TSC.DatasourceItem("project", "test")
        datasource._id = "06b944d2-959d-4604-9305-12323c95e70e"

        with requests_mock.mock() as m:
            m.delete("{0}/{1}/revisions/3".format(self.baseurl, datasource.id))
            self.server.datasources.delete_revision(datasource.id, "3")

    def test_download_revision(self) -> None:
        with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
            m.get(
                self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/revisions/3/content",
                headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
            )
            file_path = self.server.datasources.download_revision("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", "3", td)
            self.assertTrue(os.path.exists(file_path))
