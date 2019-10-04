import unittest
import os.path
import json
import requests_mock
import tableauserverclient as TSC

from tableauserverclient.server.endpoint.exceptions import GraphQLError

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), 'assets')

METADATA_QUERY_SUCCESS = os.path.join(TEST_ASSET_DIR, 'metadata_query_success.json')
METADATA_QUERY_ERROR = os.path.join(TEST_ASSET_DIR, 'metadata_query_error.json')

EXPECTED_DICT = {'publishedDatasources':
                 [{'id': '01cf92b2-2d17-b656-fc48-5c25ef6d5352', 'name': 'Batters (TestV1)'},
                  {'id': '020ae1cd-c356-f1ad-a846-b0094850d22a', 'name': 'SharePoint_List_sharepoint2010.test.tsi.lan'},
                  {'id': '061493a0-c3b2-6f39-d08c-bc3f842b44af', 'name': 'Batters_mongodb'},
                  {'id': '089fe515-ad2f-89bc-94bd-69f55f69a9c2', 'name': 'Sample - Superstore'}]}

EXPECTED_DICT_ERROR = [
    {
        "message": "Reached time limit of PT5S for query execution.",
        "path": None,
        "extensions": None
    }
]


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server('http://test')
        self.baseurl = self.server.metadata.baseurl
        self.server.version = "3.2"

        self.server._site_id = 'dad65087-b08b-4603-af4e-2887b8aafc67'
        self.server._auth_token = 'j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM'

    def test_metadata_query(self):
        with open(METADATA_QUERY_SUCCESS, 'rb') as f:
            response_json = json.loads(f.read().decode())
        with requests_mock.mock() as m:
            m.post(self.baseurl, json=response_json)
            actual = self.server.metadata.query('fake query')

            datasources = actual['data']

        self.assertDictEqual(EXPECTED_DICT, datasources)

    def test_metadata_query_ignore_error(self):
        with open(METADATA_QUERY_ERROR, 'rb') as f:
            response_json = json.loads(f.read().decode())
        with requests_mock.mock() as m:
            m.post(self.baseurl, json=response_json)
            actual = self.server.metadata.query('fake query')
            datasources = actual['data']

        self.assertNotEqual(actual.get('errors', None), None)
        self.assertListEqual(EXPECTED_DICT_ERROR, actual['errors'])
        self.assertDictEqual(EXPECTED_DICT, datasources)

    def test_metadata_query_abort_on_error(self):
        with open(METADATA_QUERY_ERROR, 'rb') as f:
            response_json = json.loads(f.read().decode())
        with requests_mock.mock() as m:
            m.post(self.baseurl, json=response_json)

            with self.assertRaises(GraphQLError) as e:
                self.server.metadata.query('fake query', abort_on_error=True)
                self.assertListEqual(e.error, EXPECTED_DICT_ERROR)
