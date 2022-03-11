import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from ._utils import read_xml_asset, asset

GET_XML = "flow_get.xml"
POPULATE_CONNECTIONS_XML = "flow_populate_connections.xml"
POPULATE_PERMISSIONS_XML = "flow_populate_permissions.xml"
UPDATE_XML = "flow_update.xml"
REFRESH_XML = "flow_refresh.xml"


class FlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.server.version = "3.5"

        self.baseurl = self.server.flows.baseurl

    def test_get(self) -> None:
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_flows, pagination_item = self.server.flows.get()

        self.assertEqual(5, pagination_item.total_available)
        self.assertEqual("587daa37-b84d-4400-a9a2-aa90e0be7837", all_flows[0].id)
        self.assertEqual("http://tableauserver/#/flows/1", all_flows[0].webpage_url)
        self.assertEqual("2019-06-16T21:43:28Z", format_datetime(all_flows[0].created_at))
        self.assertEqual("2019-06-16T21:43:28Z", format_datetime(all_flows[0].updated_at))
        self.assertEqual("Default", all_flows[0].project_name)
        self.assertEqual("FlowOne", all_flows[0].name)
        self.assertEqual("aa23f4ac-906f-11e9-86fb-3f0f71412e77", all_flows[0].project_id)
        self.assertEqual("7ebb3f20-0fd2-4f27-a2f6-c539470999e2", all_flows[0].owner_id)
        self.assertEqual({"i_love_tags"}, all_flows[0].tags)
        self.assertEqual("Descriptive", all_flows[0].description)

        self.assertEqual("5c36be69-eb30-461b-b66e-3e2a8e27cc35", all_flows[1].id)
        self.assertEqual("http://tableauserver/#/flows/4", all_flows[1].webpage_url)
        self.assertEqual("2019-06-18T03:08:19Z", format_datetime(all_flows[1].created_at))
        self.assertEqual("2019-06-18T03:08:19Z", format_datetime(all_flows[1].updated_at))
        self.assertEqual("Default", all_flows[1].project_name)
        self.assertEqual("FlowTwo", all_flows[1].name)
        self.assertEqual("aa23f4ac-906f-11e9-86fb-3f0f71412e77", all_flows[1].project_id)
        self.assertEqual("9127d03f-d996-405f-b392-631b25183a0f", all_flows[1].owner_id)

    def test_update(self) -> None:
        response_xml = read_xml_asset(UPDATE_XML)
        with requests_mock.mock() as m:
            m.put(self.baseurl + "/587daa37-b84d-4400-a9a2-aa90e0be7837", text=response_xml)
            single_datasource = TSC.FlowItem("test", "aa23f4ac-906f-11e9-86fb-3f0f71412e77")
            single_datasource.owner_id = "7ebb3f20-0fd2-4f27-a2f6-c539470999e2"
            single_datasource._id = "587daa37-b84d-4400-a9a2-aa90e0be7837"
            single_datasource.description = "So fun to see"
            single_datasource = self.server.flows.update(single_datasource)

        self.assertEqual("587daa37-b84d-4400-a9a2-aa90e0be7837", single_datasource.id)
        self.assertEqual("aa23f4ac-906f-11e9-86fb-3f0f71412e77", single_datasource.project_id)
        self.assertEqual("7ebb3f20-0fd2-4f27-a2f6-c539470999e2", single_datasource.owner_id)
        self.assertEqual("So fun to see", single_datasource.description)

    def test_populate_connections(self) -> None:
        response_xml = read_xml_asset(POPULATE_CONNECTIONS_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/connections", text=response_xml)
            single_datasource = TSC.FlowItem("test", "aa23f4ac-906f-11e9-86fb-3f0f71412e77")
            single_datasource.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
            single_datasource._id = "9dbd2263-16b5-46e1-9c43-a76bb8ab65fb"
            self.server.flows.populate_connections(single_datasource)
            self.assertEqual("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", single_datasource.id)
            connections = single_datasource.connections

        self.assertTrue(connections)
        conn1, conn2, conn3 = connections
        self.assertEqual("405c1e4b-60c9-499f-9c47-a4ef1af69359", conn1.id)
        self.assertEqual("excel-direct", conn1.connection_type)
        self.assertEqual("", conn1.server_address)
        self.assertEqual("", conn1.username)
        self.assertEqual(False, conn1.embed_password)
        self.assertEqual("b47f41b1-2c47-41a3-8b17-a38ebe8b340c", conn2.id)
        self.assertEqual("sqlserver", conn2.connection_type)
        self.assertEqual("test.database.com", conn2.server_address)
        self.assertEqual("bob", conn2.username)
        self.assertEqual(False, conn2.embed_password)
        self.assertEqual("4f4a3b78-0554-43a7-b327-9605e9df9dd2", conn3.id)
        self.assertEqual("tableau-server-site", conn3.connection_type)
        self.assertEqual("http://tableauserver", conn3.server_address)
        self.assertEqual("sally", conn3.username)
        self.assertEqual(True, conn3.embed_password)

    def test_populate_permissions(self) -> None:
        with open(asset(POPULATE_PERMISSIONS_XML), "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions", text=response_xml)
            single_datasource = TSC.FlowItem("test")
            single_datasource._id = "0448d2ed-590d-4fa0-b272-a2a8a24555b5"

            self.server.flows.populate_permissions(single_datasource)
            permissions = single_datasource.permissions

            self.assertEqual(permissions[0].grantee.tag_name, "group")
            self.assertEqual(permissions[0].grantee.id, "aa42f384-906f-11e9-86fc-bb24278874b9")
            self.assertDictEqual(
                permissions[0].capabilities,
                {
                    TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
                    TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
                },
            )

    def test_refresh(self):
        with open(asset(REFRESH_XML), "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.post(self.baseurl + "/92967d2d-c7e2-46d0-8847-4802df58f484/run", text=response_xml)
            flow_item = TSC.FlowItem("test")
            flow_item._id = "92967d2d-c7e2-46d0-8847-4802df58f484"
            refresh_job = self.server.flows.refresh(flow_item)

            self.assertEqual(refresh_job.id, "d1b2ccd0-6dfa-444a-aee4-723dbd6b7c9d")
            self.assertEqual(refresh_job.mode, "Asynchronous")
            self.assertEqual(refresh_job.type, "RunFlow")
            self.assertEqual(format_datetime(refresh_job.created_at), "2018-05-22T13:00:29Z")
            self.assertIsInstance(refresh_job.flow_run, TSC.FlowRunItem)
            self.assertEqual(refresh_job.flow_run.id, "e0c3067f-2333-4eee-8028-e0a56ca496f6")
            self.assertEqual(refresh_job.flow_run.flow_id, "92967d2d-c7e2-46d0-8847-4802df58f484")
            self.assertEqual(format_datetime(refresh_job.flow_run.started_at), "2018-05-22T13:00:29Z")
