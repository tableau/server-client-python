import unittest
import os
import requests_mock
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import read_xml_asset, read_xml_assets, asset

GET_XML = 'database_get.xml'
POPULATE_PERMISSIONS_XML = 'database_populate_permissions.xml'
UPDATE_XML = 'database_update.xml'


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'
        self.server.version = "3.5"

        self.baseurl = self.server.databases.baseurl

    def test_get(self):
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_databases, pagination_item = self.server.databases.get()

        self.assertEqual(5, pagination_item.total_available)
        self.assertEqual('5ea59b45-e497-4827-8809-bfe213236f75', all_databases[0].id)
        self.assertEqual('hyper', all_databases[0].connection_type)
        self.assertEqual('hyper_0.hyper', all_databases[0].name)

        self.assertEqual('23591f2c-4802-4d6a-9e28-574a8ea9bc4c', all_databases[1].id)
        self.assertEqual('sqlserver', all_databases[1].connection_type)
        self.assertEqual('testv1', all_databases[1].name)
        self.assertEqual('9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0', all_databases[1].contact_id)
        self.assertEqual(True, all_databases[1].certified)

    def test_update(self):
        response_xml = read_xml_asset(UPDATE_XML)
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/23591f2c-4802-4d6a-9e28-574a8ea9bc4c', text=response_xml)
            single_database = TSC.DatabaseItem('test')
            single_database.contact_id = '9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0'
            single_database._id = '23591f2c-4802-4d6a-9e28-574a8ea9bc4c'
            single_database.certified = True
            single_database.certification_note = "Test"
            single_database = self.server.databases.update(single_database)

        self.assertEqual('23591f2c-4802-4d6a-9e28-574a8ea9bc4c', single_database.id)
        self.assertEqual('9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0', single_database.contact_id)
        self.assertEqual(True, single_database.certified)
        self.assertEqual("Test", single_database.certification_note)

    def test_populate_permissions(self):
        with open(asset(POPULATE_PERMISSIONS_XML), 'rb') as f:
            response_xml = f.read().decode('utf-8')
        with requests_mock.mock() as m:
            m.get(self.baseurl + '/0448d2ed-590d-4fa0-b272-a2a8a24555b5/permissions', text=response_xml)
            single_database = TSC.DatabaseItem('test')
            single_database._id = '0448d2ed-590d-4fa0-b272-a2a8a24555b5'

            self.server.databases.populate_permissions(single_database)
            permissions = single_database.permissions

            self.assertEqual(permissions[0].grantee.tag_name, 'group')
            self.assertEqual(permissions[0].grantee.id, '5e5e1978-71fa-11e4-87dd-7382f5c437af')
            self.assertDictEqual(permissions[0].capabilities, {
                TSC.Permission.Capability.ChangePermissions: TSC.Permission.Mode.Deny,
                TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
            })

            self.assertEqual(permissions[1].grantee.tag_name, 'user')
            self.assertEqual(permissions[1].grantee.id, '7c37ee24-c4b1-42b6-a154-eaeab7ee330a')
            self.assertDictEqual(permissions[1].capabilities, {
                TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow,
            })

    def test_delete(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + '/0448d2ed-590d-4fa0-b272-a2a8a24555b5', status_code=204)
            self.server.databases.delete('0448d2ed-590d-4fa0-b272-a2a8a24555b5')
