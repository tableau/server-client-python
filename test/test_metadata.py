import json
from pathlib import Path
import unittest

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.endpoint.exceptions import GraphQLError

TEST_ASSET_DIR = Path(__file__).parent / "assets"

METADATA_QUERY_SUCCESS = TEST_ASSET_DIR / "metadata_query_success.json"
METADATA_QUERY_ERROR = TEST_ASSET_DIR / "metadata_query_error.json"
EXPECTED_PAGED_DICT = TEST_ASSET_DIR / "metadata_query_expected_dict.dict"

METADATA_PAGE_1 = TEST_ASSET_DIR / "metadata_paged_1.json"
METADATA_PAGE_2 = TEST_ASSET_DIR / "metadata_paged_2.json"
METADATA_PAGE_3 = TEST_ASSET_DIR / "metadata_paged_3.json"

EXPECTED_DICT = {
    "publishedDatasources": [
        {"id": "01cf92b2-2d17-b656-fc48-5c25ef6d5352", "name": "Batters (TestV1)"},
        {"id": "020ae1cd-c356-f1ad-a846-b0094850d22a", "name": "SharePoint_List_sharepoint2010.test.tsi.lan"},
        {"id": "061493a0-c3b2-6f39-d08c-bc3f842b44af", "name": "Batters_mongodb"},
        {"id": "089fe515-ad2f-89bc-94bd-69f55f69a9c2", "name": "Sample - Superstore"},
    ]
}

EXPECTED_DICT_ERROR = [{"message": "Reached time limit of PT5S for query execution.", "path": None, "extensions": None}]


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.5"

    return server


def test_metadata_query(server: TSC.Server) -> None:
    with open(METADATA_QUERY_SUCCESS, "rb") as f:
        response_json = json.loads(f.read().decode())
    with requests_mock.mock() as m:
        m.post(server.metadata.baseurl, json=response_json)
        actual = server.metadata.query("fake query")

        datasources = actual["data"]

    assert EXPECTED_DICT == datasources


def test_paged_metadata_query(server: TSC.Server) -> None:
    with open(EXPECTED_PAGED_DICT, "rb") as f:
        expected = eval(f.read())

    # prepare the 3 pages of results
    with open(METADATA_PAGE_1, "rb") as f:
        result_1 = f.read().decode()
    with open(METADATA_PAGE_2, "rb") as f:
        result_2 = f.read().decode()
    with open(METADATA_PAGE_3, "rb") as f:
        result_3 = f.read().decode()

    with requests_mock.mock() as m:
        m.post(
            server.metadata.baseurl,
            [
                {"text": result_1, "status_code": 200},
                {"text": result_2, "status_code": 200},
                {"text": result_3, "status_code": 200},
            ],
        )

        # validation checks for endCursor and hasNextPage,
        # but the query text doesn't matter for the test
        actual = server.metadata.paginated_query(
            "fake query endCursor hasNextPage", variables={"first": 1, "afterToken": None}
        )

    assert expected == actual


def test_metadata_query_ignore_error(server: TSC.Server) -> None:
    with open(METADATA_QUERY_ERROR, "rb") as f:
        response_json = json.loads(f.read().decode())
    with requests_mock.mock() as m:
        m.post(server.metadata.baseurl, json=response_json)
        actual = server.metadata.query("fake query")
        datasources = actual["data"]

    assert actual.get("errors", None) is not None
    assert EXPECTED_DICT_ERROR == actual["errors"]
    assert EXPECTED_DICT == datasources


def test_metadata_query_abort_on_error(server: TSC.Server) -> None:
    with open(METADATA_QUERY_ERROR, "rb") as f:
        response_json = json.loads(f.read().decode())
    with requests_mock.mock() as m:
        m.post(server.metadata.baseurl, json=response_json)

        with pytest.raises(GraphQLError) as e:
            server.metadata.query("fake query", abort_on_error=True)
            assert e.error == EXPECTED_DICT_ERROR  # type: ignore[attr-defined]
