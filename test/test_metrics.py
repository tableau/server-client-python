import requests_mock
from pathlib import Path

import pytest

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

assets = Path(__file__).parent / "assets"
METRICS_GET = assets / "metrics_get.xml"
METRICS_GET_BY_ID = assets / "metrics_get_by_id.xml"
METRICS_UPDATE = assets / "metrics_update.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.9"

    return server


def test_metrics_get(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.metrics.baseurl, text=METRICS_GET.read_text())
        all_metrics, pagination_item = server.metrics.get()

    assert len(all_metrics) == 2
    assert pagination_item.total_available == 27
    assert all_metrics[0].id == "6561daa3-20e8-407f-ba09-709b178c0b4a"
    assert all_metrics[0].name == "Example metric"
    assert all_metrics[0].description == "Description of my metric."
    assert all_metrics[0].webpage_url == "https://test/#/site/site-name/metrics/3"
    assert format_datetime(all_metrics[0].created_at) == "2020-01-02T01:02:03Z"
    assert format_datetime(all_metrics[0].updated_at) == "2020-01-02T01:02:03Z"
    assert all_metrics[0].suspended
    assert all_metrics[0].project_id == "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33"
    assert all_metrics[0].project_name == "Default"
    assert all_metrics[0].owner_id == "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33"
    assert all_metrics[0].view_id == "29dae0cd-1862-4a20-a638-e2c2dfa682d4"
    assert len(all_metrics[0].tags) == 0

    assert all_metrics[1].id == "721760d9-0aa4-4029-87ae-371c956cea07"
    assert all_metrics[1].name == "Another Example metric"
    assert all_metrics[1].description == "Description of another metric."
    assert all_metrics[1].webpage_url == "https://test/#/site/site-name/metrics/4"
    assert format_datetime(all_metrics[1].created_at) == "2020-01-03T01:02:03Z"
    assert format_datetime(all_metrics[1].updated_at) == "2020-01-04T01:02:03Z"
    assert all_metrics[1].suspended is False
    assert all_metrics[1].project_id == "486e0de0-2258-45bd-99cf-b62013e19f4e"
    assert all_metrics[1].project_name == "Assets"
    assert all_metrics[1].owner_id == "1bbbc2b9-847d-443c-9a1f-dbcf112b8814"
    assert all_metrics[1].view_id == "7dbfdb63-a6ca-4723-93ee-4fefc71992d3"
    assert len(all_metrics[1].tags) == 2
    assert "Test" in all_metrics[1].tags
    assert "Asset" in all_metrics[1].tags


def test_metrics_get_by_id(server: TSC.Server) -> None:
    luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
    with requests_mock.mock() as m:
        m.get(f"{server.metrics.baseurl}/{luid}", text=METRICS_GET_BY_ID.read_text())
        metric = server.metrics.get_by_id(luid)

    assert metric.id == "6561daa3-20e8-407f-ba09-709b178c0b4a"
    assert metric.name == "Example metric"
    assert metric.description == "Description of my metric."
    assert metric.webpage_url == "https://test/#/site/site-name/metrics/3"
    assert format_datetime(metric.created_at) == "2020-01-02T01:02:03Z"
    assert format_datetime(metric.updated_at) == "2020-01-02T01:02:03Z"
    assert metric.suspended
    assert metric.project_id == "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33"
    assert metric.project_name == "Default"
    assert metric.owner_id == "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33"
    assert metric.view_id == "29dae0cd-1862-4a20-a638-e2c2dfa682d4"
    assert len(metric.tags) == 0


def test_metrics_delete(server: TSC.Server) -> None:
    luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
    with requests_mock.mock() as m:
        m.delete(f"{server.metrics.baseurl}/{luid}")
        server.metrics.delete(luid)


def test_metrics_update(server: TSC.Server) -> None:
    luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
    metric = TSC.MetricItem()
    metric._id = luid

    with requests_mock.mock() as m:
        m.put(f"{server.metrics.baseurl}/{luid}", text=METRICS_UPDATE.read_text())
        metric = server.metrics.update(metric)

    assert metric.id == "6561daa3-20e8-407f-ba09-709b178c0b4a"
    assert metric.name == "Example metric"
    assert metric.description == "Description of my metric."
    assert metric.webpage_url == "https://test/#/site/site-name/metrics/3"
    assert format_datetime(metric.created_at) == "2020-01-02T01:02:03Z"
    assert format_datetime(metric.updated_at) == "2020-01-02T01:02:03Z"
    assert metric.suspended
    assert metric.project_id == "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33"
    assert metric.project_name == "Default"
    assert metric.owner_id == "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33"
    assert metric.view_id == "29dae0cd-1862-4a20-a638-e2c2dfa682d4"
    assert len(metric.tags) == 0
