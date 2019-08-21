import unittest
import os
import requests_mock
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime
from tableauserverclient.server.endpoint.exceptions import InternalServerError
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import read_xml_asset, read_xml_assets, asset

GET_XML = 'table_get.xml'
UPDATE_XML = 'table_update.xml'


class TableTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')

        # Fake signin
        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'
        self.server.version = "3.5"

        self.baseurl = self.server.tables.baseurl

    def test_get(self):
        response_xml = read_xml_asset(GET_XML)
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=response_xml)
            all_tables, pagination_item = self.server.tables.get()

        self.assertEqual(4, pagination_item.total_available)
        self.assertEqual('10224773-ecee-42ac-b822-d786b0b8e4d9', all_tables[0].id)
        self.assertEqual('dim_Product', all_tables[0].name)

        self.assertEqual('53c77bc1-fb41-4342-a75a-f68ac0656d0d', all_tables[1].id)
        self.assertEqual('customer', all_tables[1].name)
        self.assertEqual('dbo', all_tables[1].schema)
        self.assertEqual('9324cf6b-ba72-4b8e-b895-ac3f28d2f0e0', all_tables[1].contact_id)
        self.assertEqual(False, all_tables[1].certified)

    def test_update(self):
        response_xml = read_xml_asset(UPDATE_XML)
        with requests_mock.mock() as m:
            m.put(self.baseurl + '/10224773-ecee-42ac-b822-d786b0b8e4d9', text=response_xml)
            single_table = TSC.TableItem('test')
            single_table._id = '10224773-ecee-42ac-b822-d786b0b8e4d9'

            single_table.contact_id = '8e1a8235-c9ee-4d61-ae82-2ffacceed8e0'
            single_table.certified = True
            single_table.certification_note = "Test"
            single_table = self.server.tables.update(single_table)

        self.assertEqual('10224773-ecee-42ac-b822-d786b0b8e4d9', single_table.id)
        self.assertEqual('8e1a8235-c9ee-4d61-ae82-2ffacceed8e0', single_table.contact_id)
        self.assertEqual(True, single_table.certified)
        self.assertEqual("Test", single_table.certification_note)

    def test_delete(self):
        with requests_mock.mock() as m:
            m.delete(self.baseurl + '/0448d2ed-590d-4fa0-b272-a2a8a24555b5', status_code=204)
            self.server.tables.delete('0448d2ed-590d-4fa0-b272-a2a8a24555b5')
