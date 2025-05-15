import os
from pathlib import Path
import re
import unittest
from urllib.parse import parse_qs

import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

PAGINATION_XML = os.path.join(TEST_ASSET_DIR, "request_option_pagination.xml")
PAGE_NUMBER_XML = os.path.join(TEST_ASSET_DIR, "request_option_page_number.xml")
PAGE_SIZE_XML = os.path.join(TEST_ASSET_DIR, "request_option_page_size.xml")
FILTER_EQUALS = os.path.join(TEST_ASSET_DIR, "request_option_filter_equals.xml")
FILTER_NAME_IN = os.path.join(TEST_ASSET_DIR, "request_option_filter_name_in.xml")
FILTER_TAGS_IN = os.path.join(TEST_ASSET_DIR, "request_option_filter_tags_in.xml")
FILTER_MULTIPLE = os.path.join(TEST_ASSET_DIR, "request_option_filter_tags_in.xml")
SLICING_QUERYSET = os.path.join(TEST_ASSET_DIR, "request_option_slicing_queryset.xml")
SLICING_QUERYSET_PAGE_1 = TEST_ASSET_DIR / "queryset_slicing_page_1.xml"
SLICING_QUERYSET_PAGE_2 = TEST_ASSET_DIR / "queryset_slicing_page_2.xml"


class RequestOptionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.server = TSC.Server("http://test", False, http_options={"timeout": 5})

        # Fake signin
        self.server.version = "3.10"
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = f"{self.server.sites.baseurl}/{self.server._site_id}"

    def test_pagination(self) -> None:
        with open(PAGINATION_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/views?pageNumber=1&pageSize=10", text=response_xml)
            req_option = TSC.RequestOptions().page_size(10)
            all_views, pagination_item = self.server.views.get(req_option)

        self.assertEqual(1, pagination_item.page_number)
        self.assertEqual(10, pagination_item.page_size)
        self.assertEqual(33, pagination_item.total_available)
        self.assertEqual(10, len(all_views))

    def test_page_number(self) -> None:
        with open(PAGE_NUMBER_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/views?pageNumber=3", text=response_xml)
            req_option = TSC.RequestOptions().page_number(3)
            all_views, pagination_item = self.server.views.get(req_option)

        self.assertEqual(3, pagination_item.page_number)
        self.assertEqual(100, pagination_item.page_size)
        self.assertEqual(210, pagination_item.total_available)
        self.assertEqual(10, len(all_views))

    def test_page_size(self) -> None:
        with open(PAGE_SIZE_XML, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/views?pageSize=5", text=response_xml)
            req_option = TSC.RequestOptions().page_size(5)
            all_views, pagination_item = self.server.views.get(req_option)

        self.assertEqual(1, pagination_item.page_number)
        self.assertEqual(5, pagination_item.page_size)
        self.assertEqual(33, pagination_item.total_available)
        self.assertEqual(5, len(all_views))

    def test_filter_equals(self) -> None:
        with open(FILTER_EQUALS, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/workbooks?filter=name:eq:RESTAPISample", text=response_xml)
            req_option = TSC.RequestOptions()
            req_option.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "RESTAPISample")
            )
            matching_workbooks, pagination_item = self.server.workbooks.get(req_option)

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("RESTAPISample", matching_workbooks[0].name)
        self.assertEqual("RESTAPISample", matching_workbooks[1].name)

    def test_filter_equals_shorthand(self) -> None:
        with open(FILTER_EQUALS, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/workbooks?filter=name:eq:RESTAPISample", text=response_xml)
            matching_workbooks = self.server.workbooks.filter(name="RESTAPISample").order_by("name")

            self.assertEqual(2, matching_workbooks.total_available)
            self.assertEqual("RESTAPISample", matching_workbooks[0].name)
            self.assertEqual("RESTAPISample", matching_workbooks[1].name)

    def test_filter_tags_in(self) -> None:
        with open(FILTER_TAGS_IN, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/workbooks?filter=tags:in:[sample,safari,weather]", text=response_xml)
            req_option = TSC.RequestOptions()
            req_option.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["sample", "safari", "weather"]
                )
            )
            matching_workbooks, pagination_item = self.server.workbooks.get(req_option)

        self.assertEqual(3, pagination_item.total_available)
        self.assertEqual({"weather"}, matching_workbooks[0].tags)
        self.assertEqual({"safari"}, matching_workbooks[1].tags)
        self.assertEqual({"sample"}, matching_workbooks[2].tags)

    # check if filtered projects with spaces & special characters
    # get correctly returned
    def test_filter_name_in(self) -> None:
        with open(FILTER_NAME_IN, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(
                self.baseurl + "/projects?filter=name%3Ain%3A%5Bdefault%2CSalesforce+Sales+Proje%C5%9Bt%5D",
                text=response_xml,
            )
            req_option = TSC.RequestOptions()
            req_option.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.In,
                    ["default", "Salesforce Sales Projeśt"],
                )
            )
            matching_projects, pagination_item = self.server.projects.get(req_option)

        self.assertEqual(2, pagination_item.total_available)
        self.assertEqual("default", matching_projects[0].name)
        self.assertEqual("Salesforce Sales Projeśt", matching_projects[1].name)

    def test_filter_tags_in_shorthand(self) -> None:
        with open(FILTER_TAGS_IN, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/workbooks?filter=tags:in:[sample,safari,weather]", text=response_xml)
            matching_workbooks = self.server.workbooks.filter(tags__in=["sample", "safari", "weather"])

            self.assertEqual(3, matching_workbooks.total_available)
            self.assertEqual({"weather"}, matching_workbooks[0].tags)
            self.assertEqual({"safari"}, matching_workbooks[1].tags)
            self.assertEqual({"sample"}, matching_workbooks[2].tags)

    def test_invalid_shorthand_option(self) -> None:
        with self.assertRaises(ValueError):
            self.server.workbooks.filter(nonexistant__in=["sample", "safari"])

    def test_multiple_filter_options(self) -> None:
        with open(FILTER_MULTIPLE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        # To ensure that this is deterministic, run this a few times
        with requests_mock.mock() as m:
            # Sometimes pep8 requires you to do things you might not otherwise do
            url = "".join(
                (
                    self.baseurl,
                    "/workbooks?pageNumber=1&pageSize=100&",
                    "filter=name:eq:foo,tags:in:[sample,safari,weather]",
                )
            )
            m.get(url, text=response_xml)
            req_option = TSC.RequestOptions()
            req_option.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["sample", "safari", "weather"]
                )
            )
            req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "foo"))
            for _ in range(5):
                matching_workbooks, pagination_item = self.server.workbooks.get(req_option)
                self.assertEqual(3, pagination_item.total_available)

    # Test req_options if url already has query params
    def test_double_query_params(self) -> None:
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = self.baseurl + "/views?queryParamExists=true"
            opts = TSC.RequestOptions()

            opts.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["stocks", "market"])
            )
            opts.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))

            resp = self.server.workbooks.get_request(url, request_object=opts)
            self.assertTrue(re.search("queryparamexists=true", resp.request.query))
            self.assertTrue(re.search("filter=tags%3ain%3a%5bstocks%2cmarket%5d", resp.request.query))
            self.assertTrue(re.search("sort=name%3aasc", resp.request.query))

    # Test req_options for versions below 3.7
    def test_filter_sort_legacy(self) -> None:
        self.server.version = "3.6"
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = self.baseurl + "/views?queryParamExists=true"
            opts = TSC.RequestOptions()

            opts.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["stocks", "market"])
            )
            opts.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))

            resp = self.server.workbooks.get_request(url, request_object=opts)
            self.assertTrue(re.search("queryparamexists=true", resp.request.query))
            self.assertTrue(re.search("filter=tags:in:%5bstocks,market%5d", resp.request.query))
            self.assertTrue(re.search("sort=name:asc", resp.request.query))

    def test_vf(self) -> None:
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = self.baseurl + "/views/456/data"
            opts = TSC.PDFRequestOptions()
            opts.vf("name1#", "value1")
            opts.vf("name2$", "value2")
            opts.page_type = TSC.PDFRequestOptions.PageType.Tabloid

            resp = self.server.workbooks.get_request(url, request_object=opts)
            self.assertTrue(re.search("vf_name1%23=value1", resp.request.query))
            self.assertTrue(re.search("vf_name2%24=value2", resp.request.query))
            self.assertTrue(re.search("type=tabloid", resp.request.query))

    # Test req_options for versions beloe 3.7
    def test_vf_legacy(self) -> None:
        self.server.version = "3.6"
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = self.baseurl + "/views/456/data"
            opts = TSC.PDFRequestOptions()
            opts.vf("name1@", "value1")
            opts.vf("name2$", "value2")
            opts.page_type = TSC.PDFRequestOptions.PageType.Tabloid

            resp = self.server.workbooks.get_request(url, request_object=opts)
            self.assertTrue(re.search("vf_name1@=value1", resp.request.query))
            self.assertTrue(re.search("vf_name2\\$=value2", resp.request.query))
            self.assertTrue(re.search("type=tabloid", resp.request.query))

    def test_all_fields(self) -> None:
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = self.baseurl + "/views/456/data"
            opts = TSC.RequestOptions()
            opts._all_fields = True

            resp = self.server.users.get_request(url, request_object=opts)
            self.assertTrue(re.search("fields=_all_", resp.request.query))

    def test_multiple_filter_options_shorthand(self) -> None:
        with open(FILTER_MULTIPLE, "rb") as f:
            response_xml = f.read().decode("utf-8")
        # To ensure that this is deterministic, run this a few times
        with requests_mock.mock() as m:
            # Sometimes pep8 requires you to do things you might not otherwise do
            url = "".join(
                (
                    self.baseurl,
                    "/workbooks?pageNumber=1&pageSize=100&",
                    "filter=name:eq:foo,tags:in:[sample,safari,weather]",
                )
            )
            m.get(url, text=response_xml)

            for _ in range(5):
                matching_workbooks = self.server.workbooks.filter(tags__in=["sample", "safari", "weather"], name="foo")
                self.assertEqual(3, matching_workbooks.total_available)

    def test_slicing_queryset(self) -> None:
        with open(SLICING_QUERYSET, "rb") as f:
            response_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/views?pageNumber=1", text=response_xml)
            all_views = self.server.views.all()

            self.assertEqual(10, len(all_views[::]))
            self.assertEqual(5, len(all_views[::2]))
            self.assertEqual(8, len(all_views[2:]))
            self.assertEqual(2, len(all_views[:2]))
            self.assertEqual(3, len(all_views[2:5]))
            self.assertEqual(3, len(all_views[-3:]))
            self.assertEqual(3, len(all_views[-6:-3]))
            self.assertEqual(3, len(all_views[3:6:-1]))
            self.assertEqual(3, len(all_views[6:3:-1]))
            self.assertEqual(10, len(all_views[::-1]))
            self.assertEqual(all_views[3:6], list(reversed(all_views[3:6:-1])))

            self.assertEqual(all_views[-3].id, "2df55de2-3a2d-4e34-b515-6d4e70b830e9")

        with self.assertRaises(IndexError):
            all_views[100]

    def test_slicing_queryset_multi_page(self) -> None:
        with requests_mock.mock() as m:
            m.get(self.baseurl + "/views?pageNumber=1", text=SLICING_QUERYSET_PAGE_1.read_text())
            m.get(self.baseurl + "/views?pageNumber=2", text=SLICING_QUERYSET_PAGE_2.read_text())
            sliced_views = self.server.views.all()[9:12]

        self.assertEqual(sliced_views[0].id, "2e6d6c81-da71-4b41-892c-ba80d4e7a6d0")
        self.assertEqual(sliced_views[1].id, "47ffcb8e-3f7a-4ecf-8ab3-605da9febe20")
        self.assertEqual(sliced_views[2].id, "6757fea8-0aa9-4160-a87c-9be27b1d1c8c")

    def test_queryset_filter_args_error(self) -> None:
        with self.assertRaises(RuntimeError):
            workbooks = self.server.workbooks.filter("argument")

    def test_filtering_parameters(self) -> None:
        self.server.version = "3.6"
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = self.baseurl + "/views/456/data"
            opts = TSC.PDFRequestOptions()
            opts.parameter("name1@", "value1")
            opts.parameter("name2$", "value2")
            opts.page_type = TSC.PDFRequestOptions.PageType.Tabloid

            resp = self.server.workbooks.get_request(url, request_object=opts)
            query_params = parse_qs(resp.request.query)
            self.assertIn("name1@", query_params)
            self.assertIn("value1", query_params["name1@"])
            self.assertIn("name2$", query_params)
            self.assertIn("value2", query_params["name2$"])
            self.assertIn("type", query_params)
            self.assertIn("tabloid", query_params["type"])

    def test_queryset_endpoint_pagesize_all(self) -> None:
        for page_size in (1, 10, 100, 1000):
            with self.subTest(page_size):
                with requests_mock.mock() as m:
                    m.get(f"{self.baseurl}/views?pageSize={page_size}", text=SLICING_QUERYSET_PAGE_1.read_text())
                    queryset = self.server.views.all(page_size=page_size)
                    assert queryset.request_options.pagesize == page_size
                    _ = list(queryset)

    def test_queryset_endpoint_pagesize_filter(self) -> None:
        for page_size in (1, 10, 100, 1000):
            with self.subTest(page_size):
                with requests_mock.mock() as m:
                    m.get(f"{self.baseurl}/views?pageSize={page_size}", text=SLICING_QUERYSET_PAGE_1.read_text())
                    queryset = self.server.views.filter(page_size=page_size)
                    assert queryset.request_options.pagesize == page_size
                    _ = list(queryset)

    def test_queryset_pagesize_filter(self) -> None:
        for page_size in (1, 10, 100, 1000):
            with self.subTest(page_size):
                with requests_mock.mock() as m:
                    m.get(f"{self.baseurl}/views?pageSize={page_size}", text=SLICING_QUERYSET_PAGE_1.read_text())
                    queryset = self.server.views.all().filter(page_size=page_size)
                    assert queryset.request_options.pagesize == page_size
                    _ = list(queryset)

    def test_language_export(self) -> None:
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = self.baseurl + "/views/456/data"
            opts = TSC.PDFRequestOptions()
            opts.language = "en-US"

            resp = self.server.users.get_request(url, request_object=opts)
            self.assertTrue(re.search("language=en-us", resp.request.query))
