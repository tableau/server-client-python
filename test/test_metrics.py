import unittest
import requests_mock
from pathlib import Path

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime

assets = Path(__file__).parent / "assets"
METRICS_GET = assets / "metrics_get.xml"
METRICS_GET_BY_ID = assets / "metrics_get_by_id.xml"
METRICS_UPDATE = assets / "metrics_update.xml"


class TestMetrics(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False)

        # Fake signin
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.server.version = "3.9"

        self.baseurl = self.server.metrics.baseurl

    def test_metrics_get(self) -> None:
        with requests_mock.mock() as m:
            m.get(self.baseurl, text=METRICS_GET.read_text())
            all_metrics, pagination_item = self.server.metrics.get()

        self.assertEqual(len(all_metrics), 2)
        self.assertEqual(pagination_item.total_available, 27)
        self.assertEqual(all_metrics[0].id, "6561daa3-20e8-407f-ba09-709b178c0b4a")
        self.assertEqual(all_metrics[0].name, "Example metric")
        self.assertEqual(all_metrics[0].description, "Description of my metric.")
        self.assertEqual(all_metrics[0].webpage_url, "https://test/#/site/site-name/metrics/3")
        self.assertEqual(format_datetime(all_metrics[0].created_at), "2020-01-02T01:02:03Z")
        self.assertEqual(format_datetime(all_metrics[0].updated_at), "2020-01-02T01:02:03Z")
        self.assertEqual(all_metrics[0].suspended, True)
        self.assertEqual(all_metrics[0].project_id, "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33")
        self.assertEqual(all_metrics[0].project_name, "Default")
        self.assertEqual(all_metrics[0].owner_id, "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33")
        self.assertEqual(all_metrics[0].view_id, "29dae0cd-1862-4a20-a638-e2c2dfa682d4")
        self.assertEqual(len(all_metrics[0].tags), 0)

        self.assertEqual(all_metrics[1].id, "721760d9-0aa4-4029-87ae-371c956cea07")
        self.assertEqual(all_metrics[1].name, "Another Example metric")
        self.assertEqual(all_metrics[1].description, "Description of another metric.")
        self.assertEqual(all_metrics[1].webpage_url, "https://test/#/site/site-name/metrics/4")
        self.assertEqual(format_datetime(all_metrics[1].created_at), "2020-01-03T01:02:03Z")
        self.assertEqual(format_datetime(all_metrics[1].updated_at), "2020-01-04T01:02:03Z")
        self.assertEqual(all_metrics[1].suspended, False)
        self.assertEqual(all_metrics[1].project_id, "486e0de0-2258-45bd-99cf-b62013e19f4e")
        self.assertEqual(all_metrics[1].project_name, "Assets")
        self.assertEqual(all_metrics[1].owner_id, "1bbbc2b9-847d-443c-9a1f-dbcf112b8814")
        self.assertEqual(all_metrics[1].view_id, "7dbfdb63-a6ca-4723-93ee-4fefc71992d3")
        self.assertEqual(len(all_metrics[1].tags), 2)
        self.assertIn("Test", all_metrics[1].tags)
        self.assertIn("Asset", all_metrics[1].tags)

    def test_metrics_get_by_id(self) -> None:
        luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
        with requests_mock.mock() as m:
            m.get(f"{self.baseurl}/{luid}", text=METRICS_GET_BY_ID.read_text())
            metric = self.server.metrics.get_by_id(luid)

        self.assertEqual(metric.id, "6561daa3-20e8-407f-ba09-709b178c0b4a")
        self.assertEqual(metric.name, "Example metric")
        self.assertEqual(metric.description, "Description of my metric.")
        self.assertEqual(metric.webpage_url, "https://test/#/site/site-name/metrics/3")
        self.assertEqual(format_datetime(metric.created_at), "2020-01-02T01:02:03Z")
        self.assertEqual(format_datetime(metric.updated_at), "2020-01-02T01:02:03Z")
        self.assertEqual(metric.suspended, True)
        self.assertEqual(metric.project_id, "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33")
        self.assertEqual(metric.project_name, "Default")
        self.assertEqual(metric.owner_id, "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33")
        self.assertEqual(metric.view_id, "29dae0cd-1862-4a20-a638-e2c2dfa682d4")
        self.assertEqual(len(metric.tags), 0)

    def test_metrics_delete(self) -> None:
        luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
        with requests_mock.mock() as m:
            m.delete(f"{self.baseurl}/{luid}")
            self.server.metrics.delete(luid)

    def test_metrics_update(self) -> None:
        luid = "6561daa3-20e8-407f-ba09-709b178c0b4a"
        metric = TSC.MetricItem()
        metric._id = luid

        with requests_mock.mock() as m:
            m.put(f"{self.baseurl}/{luid}", text=METRICS_UPDATE.read_text())
            metric = self.server.metrics.update(metric)

        self.assertEqual(metric.id, "6561daa3-20e8-407f-ba09-709b178c0b4a")
        self.assertEqual(metric.name, "Example metric")
        self.assertEqual(metric.description, "Description of my metric.")
        self.assertEqual(metric.webpage_url, "https://test/#/site/site-name/metrics/3")
        self.assertEqual(format_datetime(metric.created_at), "2020-01-02T01:02:03Z")
        self.assertEqual(format_datetime(metric.updated_at), "2020-01-02T01:02:03Z")
        self.assertEqual(metric.suspended, True)
        self.assertEqual(metric.project_id, "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33")
        self.assertEqual(metric.project_name, "Default")
        self.assertEqual(metric.owner_id, "32e79edb-6cfd-47dc-ad79-e8ec2fbb1d33")
        self.assertEqual(metric.view_id, "29dae0cd-1862-4a20-a638-e2c2dfa682d4")
        self.assertEqual(len(metric.tags), 0)
