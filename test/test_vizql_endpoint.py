import unittest
import json
import requests_mock

import tableauserverclient as TSC
from ._utils import asset


class VizQLEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.5"  # VizQL API requires 3.5+

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.vizql.baseurl
        
        # Sample datasource id to use in tests
        self.datasource_id = "01234567-89ab-cdef-0123-456789abcdef"
        
        # Sample response for metadata call
        self.metadata_response = {
            "fields": [
                {
                    "fieldName": "Field1",
                    "fieldCaption": "Field 1",
                    "dataType": "STRING"
                },
                {
                    "fieldName": "Field2",
                    "fieldCaption": "Field 2",
                    "dataType": "INTEGER"
                }
            ],
            "logicalTables": [
                {
                    "id": "LogicalTable1",
                    "caption": "Table 1"
                }
            ]
        }
        
        # Sample response for query data call
        self.data_response = {
            "data": {
                "rows": [
                    ["value1", 1],
                    ["value2", 2]
                ],
                "columns": ["Field1", "Field2"]
            }
        }
        
        # Sample query object
        self.sample_query = {
            "fields": [
                {
                    "fieldCaption": "Field1"
                },
                {
                    "fieldCaption": "Field2"
                }
            ]
        }

    def test_query_vds_metadata(self) -> None:
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}/read-metadata", 
                  json=self.metadata_response, 
                  status_code=200)
            
            # Call the method
            result = self.server.vizql.query_vds_metadata(self.datasource_id)
            
            # Verify the result
            self.assertEqual(result, self.metadata_response)
            
            # Verify the request was properly formed
            self.assertEqual(m.last_request.json(), 
                             {"datasource": {"datasourceLuid": self.datasource_id}})
    
    def test_query_vds_metadata_with_parameters(self) -> None:
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}/read-metadata", 
                  json=self.metadata_response, 
                  status_code=200)
            
            # Call the method with parameters
            result = self.server.vizql.query_vds_metadata(
                self.datasource_id, 
                parameters={"params": {"param1": "value1"}}
            )
            
            # Verify the result
            self.assertEqual(result, self.metadata_response)
            
            # Verify the request parameters
            self.assertEqual(m.last_request.qs, {"param1": ["value1"]})
    
    def test_query_vds_metadata_abort_on_error(self) -> None:
        error_response = {
            "errors": [{"message": "Test error"}]
        }
        
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}/read-metadata", 
                  json=error_response, 
                  status_code=200)
            
            # Should raise exception when abort_on_error is True
            with self.assertRaises(TSC.server.endpoint.exceptions.GraphQLError):
                self.server.vizql.query_vds_metadata(
                    self.datasource_id, 
                    abort_on_error=True
                )
            
            # Should not raise exception when abort_on_error is False
            result = self.server.vizql.query_vds_metadata(
                self.datasource_id, 
                abort_on_error=False
            )
            self.assertEqual(result, error_response)
    
    def test_query_vds_data(self) -> None:
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}/query-datasource", 
                  json=self.data_response, 
                  status_code=200)
            
            # Call the method
            result = self.server.vizql.query_vds_data(
                self.sample_query,
                self.datasource_id
            )
            
            # Verify the result
            self.assertEqual(result, self.data_response)
            
            # Verify the request was properly formed
            self.assertEqual(m.last_request.json(), {
                "query": self.sample_query,
                "datasource": {"datasourceLuid": self.datasource_id}
            })
    
    def test_query_vds_data_with_parameters(self) -> None:
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}/query-datasource", 
                  json=self.data_response, 
                  status_code=200)
            
            # Call the method with parameters
            result = self.server.vizql.query_vds_data(
                self.sample_query,
                self.datasource_id,
                parameters={"params": {"param1": "value1"}}
            )
            
            # Verify the result
            self.assertEqual(result, self.data_response)
            
            # Verify the request parameters
            self.assertEqual(m.last_request.qs, {"param1": ["value1"]})
    
    def test_query_vds_data_abort_on_error(self) -> None:
        error_response = {
            "errors": [{"message": "Test error"}]
        }
        
        with requests_mock.mock() as m:
            m.post(f"{self.baseurl}/query-datasource", 
                  json=error_response, 
                  status_code=200)
            
            # Should raise exception when abort_on_error is True
            with self.assertRaises(TSC.server.endpoint.exceptions.GraphQLError):
                self.server.vizql.query_vds_data(
                    self.sample_query,
                    self.datasource_id,
                    abort_on_error=True
                )
            
            # Should not raise exception when abort_on_error is False
            result = self.server.vizql.query_vds_data(
                self.sample_query,
                self.datasource_id,
                abort_on_error=False
            )
            self.assertEqual(result, error_response)
    
    def test_get_before_signin(self) -> None:
        self.server._auth_token = None
        with self.assertRaises(TSC.NotSignedInError):
            self.server.vizql.query_vds_metadata(self.datasource_id) 