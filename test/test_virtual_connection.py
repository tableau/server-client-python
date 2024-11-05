import json
from pathlib import Path
import unittest

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import parse_datetime
from tableauserverclient.models.virtual_connection_item import VirtualConnectionItem

ASSET_DIR = Path(__file__).parent / "assets"

VIRTUAL_CONNECTION_GET_XML = ASSET_DIR / "virtual_connections_get.xml"
VIRTUAL_CONNECTION_POPULATE_CONNECTIONS = ASSET_DIR / "virtual_connection_populate_connections.xml"
VC_DB_CONN_UPDATE = ASSET_DIR / "virtual_connection_database_connection_update.xml"
VIRTUAL_CONNECTION_DOWNLOAD = ASSET_DIR / "virtual_connections_download.xml"
VIRTUAL_CONNECTION_UPDATE = ASSET_DIR / "virtual_connections_update.xml"
VIRTUAL_CONNECTION_REVISIONS = ASSET_DIR / "virtual_connections_revisions.xml"
VIRTUAL_CONNECTION_PUBLISH = ASSET_DIR / "virtual_connections_publish.xml"
ADD_PERMISSIONS = ASSET_DIR / "virtual_connection_add_permissions.xml"


class TestVirtualConnections(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test")

        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.server.version = "3.23"

        self.baseurl = f"{self.server.baseurl}/sites/{self.server.site_id}/virtualConnections"
        return super().setUp()

    def test_from_xml(self):
        items = VirtualConnectionItem.from_response(VIRTUAL_CONNECTION_GET_XML.read_bytes(), self.server.namespace)

        assert len(items) == 1
        virtual_connection = items[0]
        assert virtual_connection.created_at == parse_datetime("2024-05-30T09:00:00Z")
        assert not virtual_connection.has_extracts
        assert virtual_connection.id == "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        assert virtual_connection.is_certified
        assert virtual_connection.name == "vconn"
        assert virtual_connection.updated_at == parse_datetime("2024-06-18T09:00:00Z")
        assert virtual_connection.webpage_url == "https://test/#/site/site-name/virtualconnections/3"

    def test_virtual_connection_get(self):
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=VIRTUAL_CONNECTION_GET_XML.read_text())
            items, pagination_item = self.server.virtual_connections.get()

        assert len(items) == 1
        assert pagination_item.total_available == 1
        assert items[0].name == "vconn"

    def test_virtual_connection_populate_connections(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{vconn.id}/connections", text=VIRTUAL_CONNECTION_POPULATE_CONNECTIONS.read_text())
            vc_out = self.server.virtual_connections.populate_connections(vconn)
            connection_list = list(vconn.connections)

        assert vc_out is vconn
        assert vc_out._connections is not None

        assert len(connection_list) == 1
        connection = connection_list[0]
        assert connection.id == "37ca6ced-58d7-4dcf-99dc-f0a85223cbef"
        assert connection.connection_type == "postgres"
        assert connection.server_address == "localhost"
        assert connection.server_port == "5432"
        assert connection.username == "pgadmin"

    def test_virtual_connection_update_connection_db_connection(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        connection = TSC.ConnectionItem()
        connection._id = "37ca6ced-58d7-4dcf-99dc-f0a85223cbef"
        connection.server_address = "localhost"
        connection.server_port = "5432"
        connection.username = "pgadmin"
        connection.password = "password"
        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{vconn.id}/connections/{connection.id}/modify", text=VC_DB_CONN_UPDATE.read_text())
            updated_connection = self.server.virtual_connections.update_connection_db_connection(vconn, connection)

        assert updated_connection.id == "37ca6ced-58d7-4dcf-99dc-f0a85223cbef"
        assert updated_connection.server_address == "localhost"
        assert updated_connection.server_port == "5432"
        assert updated_connection.username == "pgadmin"
        assert updated_connection.password is None

    def test_virtual_connection_get_by_id(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{vconn.id}", text=VIRTUAL_CONNECTION_DOWNLOAD.read_text())
            vconn = self.server.virtual_connections.get_by_id(vconn)

        assert vconn.content
        assert vconn.created_at is None
        assert vconn.id is None
        assert "policyCollection" in vconn.content
        assert "revision" in vconn.content

    def test_virtual_connection_update(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        vconn.is_certified = True
        vconn.certification_note = "demo certification note"
        vconn.project_id = "5286d663-8668-4ac2-8c8d-91af7d585f6b"
        vconn.owner_id = "9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0"
        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{vconn.id}", text=VIRTUAL_CONNECTION_UPDATE.read_text())
            vconn = self.server.virtual_connections.update(vconn)

        assert not vconn.has_extracts
        assert vconn.id is None
        assert vconn.is_certified
        assert vconn.name == "testv1"
        assert vconn.certification_note == "demo certification note"
        assert vconn.project_id == "5286d663-8668-4ac2-8c8d-91af7d585f6b"
        assert vconn.owner_id == "9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0"

    def test_virtual_connection_get_revisions(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{vconn.id}/revisions", text=VIRTUAL_CONNECTION_REVISIONS.read_text())
            revisions, pagination_item = self.server.virtual_connections.get_revisions(vconn)

        assert len(revisions) == 3
        assert pagination_item.total_available == 3
        assert revisions[0].resource_id == vconn.id
        assert revisions[0].resource_name == vconn.name
        assert revisions[0].created_at == parse_datetime("2016-07-26T20:34:56Z")
        assert revisions[0].revision_number == "1"
        assert not revisions[0].current
        assert not revisions[0].deleted
        assert revisions[0].user_name == "Cassie"
        assert revisions[0].user_id == "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"
        assert revisions[1].resource_id == vconn.id
        assert revisions[1].resource_name == vconn.name
        assert revisions[1].created_at == parse_datetime("2016-07-27T20:34:56Z")
        assert revisions[1].revision_number == "2"
        assert not revisions[1].current
        assert not revisions[1].deleted
        assert revisions[2].resource_id == vconn.id
        assert revisions[2].resource_name == vconn.name
        assert revisions[2].created_at == parse_datetime("2016-07-28T20:34:56Z")
        assert revisions[2].revision_number == "3"
        assert revisions[2].current
        assert not revisions[2].deleted
        assert revisions[2].user_name == "Cassie"
        assert revisions[2].user_id == "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7"

    def test_virtual_connection_download_revision(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{vconn.id}/revisions/1", text=VIRTUAL_CONNECTION_DOWNLOAD.read_text())
            content = self.server.virtual_connections.download_revision(vconn, 1)

        assert content
        assert "policyCollection" in content
        data = json.loads(content)
        assert "policyCollection" in data
        assert "revision" in data

    def test_virtual_connection_delete(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        with requests_mock.mock() as m:
            m.delete(f"{self.baseurl}/{vconn.id}")
            self.server.virtual_connections.delete(vconn)
            self.server.virtual_connections.delete(vconn.id)

        assert m.call_count == 2

    def test_virtual_connection_publish(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        vconn.project_id = "9836791c-9468-40f0-b7f3-d10b9562a046"
        vconn.owner_id = "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}?overwrite=false&publishAsDraft=false", text=VIRTUAL_CONNECTION_PUBLISH.read_text())
            vconn = self.server.virtual_connections.publish(
                vconn, '{"test": 0}', mode="CreateNew", publish_as_draft=False
            )

        assert vconn.name == "vconn_test"
        assert vconn.owner_id == "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
        assert vconn.project_id == "9836791c-9468-40f0-b7f3-d10b9562a046"
        assert vconn.content
        assert "policyCollection" in vconn.content
        assert "revision" in vconn.content

    def test_virtual_connection_publish_draft_overwrite(self):
        vconn = VirtualConnectionItem("vconn")
        vconn._id = "8fd7cc02-bb55-4d15-b8b1-9650239efe79"
        vconn.project_id = "9836791c-9468-40f0-b7f3-d10b9562a046"
        vconn.owner_id = "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}?overwrite=true&publishAsDraft=true", text=VIRTUAL_CONNECTION_PUBLISH.read_text())
            vconn = self.server.virtual_connections.publish(
                vconn, '{"test": 0}', mode="Overwrite", publish_as_draft=True
            )

        assert vconn.name == "vconn_test"
        assert vconn.owner_id == "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
        assert vconn.project_id == "9836791c-9468-40f0-b7f3-d10b9562a046"
        assert vconn.content
        assert "policyCollection" in vconn.content
        assert "revision" in vconn.content

    def test_add_permissions(self) -> None:
        with open(ADD_PERMISSIONS, "rb") as f:
            response_xml = f.read().decode("utf-8")

        single_virtual_connection = TSC.VirtualConnectionItem("test")
        single_virtual_connection._id = "21778de4-b7b9-44bc-a599-1506a2639ace"

        bob = TSC.UserItem.as_reference("7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
        group_of_people = TSC.GroupItem.as_reference("5e5e1978-71fa-11e4-87dd-7382f5c437af")

        new_permissions = [
            TSC.PermissionsRule(bob, {"Write": "Allow"}),
            TSC.PermissionsRule(group_of_people, {"Read": "Deny"}),
        ]

        with requests_mock.mock() as m:
            m.put(self.baseurl + "/21778de4-b7b9-44bc-a599-1506a2639ace/permissions", text=response_xml)
            permissions = self.server.virtual_connections.add_permissions(single_virtual_connection, new_permissions)

        self.assertEqual(permissions[0].grantee.tag_name, "group")
        self.assertEqual(permissions[0].grantee.id, "5e5e1978-71fa-11e4-87dd-7382f5c437af")
        self.assertDictEqual(permissions[0].capabilities, {TSC.Permission.Capability.Read: TSC.Permission.Mode.Deny})

        self.assertEqual(permissions[1].grantee.tag_name, "user")
        self.assertEqual(permissions[1].grantee.id, "7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
        self.assertDictEqual(permissions[1].capabilities, {TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow})
