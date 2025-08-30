from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC

TEST_ASSETS_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSETS_DIR / "data_acceleration_report.xml"


@pytest.fixture(scope="function")
def server():
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.8"

    return server


def test_get_data_acceleration_report(server):
    response_xml = GET_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.data_acceleration_report.baseurl, text=response_xml)
        data_acceleration_report = server.data_acceleration_report.get()

    assert 2 == len(data_acceleration_report.comparison_records)

    assert "site-1" == data_acceleration_report.comparison_records[0].site
    assert "sheet-1" == data_acceleration_report.comparison_records[0].sheet_uri
    assert "0" == data_acceleration_report.comparison_records[0].unaccelerated_session_count
    assert "0.0" == data_acceleration_report.comparison_records[0].avg_non_accelerated_plt
    assert "1" == data_acceleration_report.comparison_records[0].accelerated_session_count
    assert "0.166" == data_acceleration_report.comparison_records[0].avg_accelerated_plt

    assert "site-2" == data_acceleration_report.comparison_records[1].site
    assert "sheet-2" == data_acceleration_report.comparison_records[1].sheet_uri
    assert "2" == data_acceleration_report.comparison_records[1].unaccelerated_session_count
    assert "1.29" == data_acceleration_report.comparison_records[1].avg_non_accelerated_plt
    assert "3" == data_acceleration_report.comparison_records[1].accelerated_session_count
    assert "0.372" == data_acceleration_report.comparison_records[1].avg_accelerated_plt
