from pathlib import Path
from urllib.parse import parse_qs

import pytest
import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = Path(__file__).parent / "assets"

PAGINATION_XML = TEST_ASSET_DIR / "request_option_pagination.xml"
PAGE_NUMBER_XML = TEST_ASSET_DIR / "request_option_page_number.xml"
PAGE_SIZE_XML = TEST_ASSET_DIR / "request_option_page_size.xml"
FILTER_EQUALS = TEST_ASSET_DIR / "request_option_filter_equals.xml"
FILTER_NAME_IN = TEST_ASSET_DIR / "request_option_filter_name_in.xml"
FILTER_TAGS_IN = TEST_ASSET_DIR / "request_option_filter_tags_in.xml"
FILTER_MULTIPLE = TEST_ASSET_DIR / "request_option_filter_tags_in.xml"
SLICING_QUERYSET = TEST_ASSET_DIR / "request_option_slicing_queryset.xml"
SLICING_QUERYSET_PAGE_1 = TEST_ASSET_DIR / "queryset_slicing_page_1.xml"
SLICING_QUERYSET_PAGE_2 = TEST_ASSET_DIR / "queryset_slicing_page_2.xml"


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_pagination(server: TSC.Server) -> None:
    response_xml = PAGINATION_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.views.baseurl + "?pageNumber=1&pageSize=10", text=response_xml)
        req_option = TSC.RequestOptions().page_size(10)
        all_views, pagination_item = server.views.get(req_option)

    assert 1 == pagination_item.page_number
    assert 10 == pagination_item.page_size
    assert 33 == pagination_item.total_available
    assert 10 == len(all_views)


def test_page_number(server: TSC.Server) -> None:
    response_xml = PAGE_NUMBER_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.views.baseurl + "?pageNumber=3", text=response_xml)
        req_option = TSC.RequestOptions().page_number(3)
        all_views, pagination_item = server.views.get(req_option)

    assert 3 == pagination_item.page_number
    assert 100 == pagination_item.page_size
    assert 210 == pagination_item.total_available
    assert 10 == len(all_views)


def test_page_size(server: TSC.Server) -> None:
    response_xml = PAGE_SIZE_XML.read_text()
    with requests_mock.mock() as m:
        m.get(server.views.baseurl + "?pageSize=5", text=response_xml)
        req_option = TSC.RequestOptions().page_size(5)
        all_views, pagination_item = server.views.get(req_option)

    assert 1 == pagination_item.page_number
    assert 5 == pagination_item.page_size
    assert 33 == pagination_item.total_available
    assert 5 == len(all_views)


def test_filter_equals(server: TSC.Server) -> None:
    response_xml = FILTER_EQUALS.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "?filter=name:eq:RESTAPISample", text=response_xml)
        req_option = TSC.RequestOptions()
        req_option.filter.add(
            TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "RESTAPISample")
        )
        matching_workbooks, pagination_item = server.workbooks.get(req_option)

    assert 2 == pagination_item.total_available
    assert "RESTAPISample" == matching_workbooks[0].name
    assert "RESTAPISample" == matching_workbooks[1].name


def test_filter_equals_shorthand(server: TSC.Server) -> None:
    response_xml = FILTER_EQUALS.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "?filter=name:eq:RESTAPISample", text=response_xml)
        matching_workbooks = server.workbooks.filter(name="RESTAPISample").order_by("name")

        assert 2 == matching_workbooks.total_available
        assert "RESTAPISample" == matching_workbooks[0].name
        assert "RESTAPISample" == matching_workbooks[1].name


def test_filter_tags_in(server: TSC.Server) -> None:
    response_xml = FILTER_TAGS_IN.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "?filter=tags:in:[sample,safari,weather]", text=response_xml)
        req_option = TSC.RequestOptions()
        req_option.filter.add(
            TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["sample", "safari", "weather"])
        )
        matching_workbooks, pagination_item = server.workbooks.get(req_option)

    assert 3 == pagination_item.total_available
    assert {"weather"} == matching_workbooks[0].tags
    assert {"safari"} == matching_workbooks[1].tags
    assert {"sample"} == matching_workbooks[2].tags


# check if filtered projects with spaces & special characters
# get correctly returned
def test_filter_name_in(server: TSC.Server) -> None:
    response_xml = FILTER_NAME_IN.read_text("utf8")
    with requests_mock.mock() as m:
        m.get(
            server.projects.baseurl + "?filter=name%3Ain%3A%5Bdefault%2CSalesforce+Sales+Proje%C5%9Bt%5D",
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
        matching_projects, pagination_item = server.projects.get(req_option)

    assert 2 == pagination_item.total_available
    assert "default" == matching_projects[0].name
    assert "Salesforce Sales Projeśt" == matching_projects[1].name


def test_filter_tags_in_shorthand(server: TSC.Server) -> None:
    response_xml = FILTER_TAGS_IN.read_text()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "?filter=tags:in:[sample,safari,weather]", text=response_xml)
        matching_workbooks = server.workbooks.filter(tags__in=["sample", "safari", "weather"])

        assert 3 == matching_workbooks.total_available
        assert {"weather"} == matching_workbooks[0].tags
        assert {"safari"} == matching_workbooks[1].tags
        assert {"sample"} == matching_workbooks[2].tags


def test_invalid_shorthand_option(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.workbooks.filter(nonexistant__in=["sample", "safari"])


def test_multiple_filter_options(server: TSC.Server) -> None:
    response_xml = FILTER_MULTIPLE.read_text()
    # To ensure that this is deterministic, run this a few times
    with requests_mock.mock() as m:
        # Sometimes pep8 requires you to do things you might not otherwise do
        url = "".join(
            (
                server.workbooks.baseurl,
                "?pageNumber=1&pageSize=100&",
                "filter=name:eq:foo,tags:in:[sample,safari,weather]",
            )
        )
        m.get(url, text=response_xml)
        req_option = TSC.RequestOptions()
        req_option.filter.add(
            TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["sample", "safari", "weather"])
        )
        req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "foo"))
        for _ in range(5):
            matching_workbooks, pagination_item = server.workbooks.get(req_option)
            assert 3 == pagination_item.total_available


# Test req_options if url already has query params
def test_double_query_params(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = server.workbooks.baseurl + "?queryParamExists=true"
        opts = TSC.RequestOptions()

        opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["stocks", "market"]))
        opts.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))

        resp = server.workbooks.get_request(url, request_object=opts)
        query_string = parse_qs(resp.request.query)
        assert "queryparamexists" in query_string
        assert "true" in query_string["queryparamexists"]
        assert "filter" in query_string
        assert "tags:in:[stocks,market]" in query_string["filter"]
        assert "sort" in query_string
        assert "name:asc" in query_string["sort"]


# Test req_options for versions below 3.7
def test_filter_sort_legacy(server: TSC.Server) -> None:
    server.version = "3.6"
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = server.workbooks.baseurl + "?queryParamExists=true"
        opts = TSC.RequestOptions()

        opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["stocks", "market"]))
        opts.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))

        resp = server.workbooks.get_request(url, request_object=opts)
        query_string = parse_qs(resp.request.query)
        assert "queryparamexists" in query_string
        assert "true" in query_string["queryparamexists"]
        assert "filter" in query_string
        assert "tags:in:[stocks,market]" in query_string["filter"]
        assert "sort" in query_string
        assert "name:asc" in query_string["sort"]


def test_vf(server: TSC.Server) -> None:
    server.version = "3.10"
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = server.workbooks.baseurl + "/456/data"
        opts = TSC.PDFRequestOptions()
        opts.vf("name1#", "value1")
        opts.vf("name2$", "value2")
        opts.page_type = TSC.PDFRequestOptions.PageType.Tabloid

        resp = server.workbooks.get_request(url, request_object=opts)
        query_string = parse_qs(resp.request.query)
    assert "vf_name1#" in query_string
    assert "value1" in query_string["vf_name1#"]
    assert "vf_name2$" in query_string
    assert "value2" in query_string["vf_name2$"]
    assert "type" in query_string
    assert "tabloid" in query_string["type"]


# Test req_options for versions below 3.7
def test_vf_legacy(server: TSC.Server) -> None:
    server.version = "3.6"
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = server.workbooks.baseurl
        opts = TSC.PDFRequestOptions()
        opts.vf("name1@", "value1")
        opts.vf("name2$", "value2")
        opts.page_type = TSC.PDFRequestOptions.PageType.Tabloid

        resp = server.workbooks.get_request(url, request_object=opts)
        query_string = parse_qs(resp.request.query)
        assert "vf_name1@" in query_string
        assert "value1" in query_string["vf_name1@"]
        assert "vf_name2$" in query_string
        assert "value2" in query_string["vf_name2$"]
        assert "type" in query_string
        assert "tabloid" in query_string["type"]


def test_all_fields(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = server.views.baseurl + "/456/data"
        opts = TSC.RequestOptions()
        opts.all_fields = True

        resp = server.users.get_request(url, request_object=opts)
        query_string = parse_qs(resp.request.query)
        assert "fields" in query_string
        assert ["_all_"] == query_string["fields"]


def test_multiple_filter_options_shorthand(server: TSC.Server) -> None:
    response_xml = FILTER_MULTIPLE.read_text()
    # To ensure that this is deterministic, run this a few times
    with requests_mock.mock() as m:
        # Sometimes pep8 requires you to do things you might not otherwise do
        url = "".join(
            (
                server.workbooks.baseurl,
                "?pageNumber=1&pageSize=100&",
                "filter=name:eq:foo,tags:in:[sample,safari,weather]",
            )
        )
        m.get(url, text=response_xml)

        for _ in range(5):
            matching_workbooks = server.workbooks.filter(tags__in=["sample", "safari", "weather"], name="foo")
            assert 3 == matching_workbooks.total_available


def test_slicing_queryset(server: TSC.Server) -> None:
    response_xml = SLICING_QUERYSET.read_text()
    with requests_mock.mock() as m:
        m.get(server.views.baseurl + "?pageNumber=1", text=response_xml)
        all_views = server.views.all()

        assert 10 == len(all_views[::])
        assert 5 == len(all_views[::2])
        assert 8 == len(all_views[2:])
        assert 2 == len(all_views[:2])
        assert 3 == len(all_views[2:5])
        assert 3 == len(all_views[-3:])
        assert 3 == len(all_views[-6:-3])
        assert 3 == len(all_views[3:6:-1])
        assert 3 == len(all_views[6:3:-1])
        assert 10 == len(all_views[::-1])
        assert all_views[3:6] == list(reversed(all_views[3:6:-1]))

        assert all_views[-3].id == "2df55de2-3a2d-4e34-b515-6d4e70b830e9"

    with pytest.raises(IndexError):
        all_views[100]


def test_slicing_queryset_multi_page(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.views.baseurl + "?pageNumber=1", text=SLICING_QUERYSET_PAGE_1.read_text())
        m.get(server.views.baseurl + "?pageNumber=2", text=SLICING_QUERYSET_PAGE_2.read_text())
        sliced_views = server.views.all()[9:12]

    assert sliced_views[0].id == "2e6d6c81-da71-4b41-892c-ba80d4e7a6d0"
    assert sliced_views[1].id == "47ffcb8e-3f7a-4ecf-8ab3-605da9febe20"
    assert sliced_views[2].id == "6757fea8-0aa9-4160-a87c-9be27b1d1c8c"


def test_queryset_filter_args_error(server: TSC.Server) -> None:
    with pytest.raises(RuntimeError):
        workbooks = server.workbooks.filter("argument")


def test_filtering_parameters(server: TSC.Server) -> None:
    server.version = "3.6"
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = server.workbooks.baseurl + "/456/data"
        opts = TSC.PDFRequestOptions()
        opts.parameter("name1@", "value1")
        opts.parameter("name2$", "value2")
        opts.page_type = TSC.PDFRequestOptions.PageType.Tabloid

        resp = server.workbooks.get_request(url, request_object=opts)
        query_params = parse_qs(resp.request.query)
        assert "name1@" in query_params
        assert "value1" in query_params["name1@"]
        assert "name2$" in query_params
        assert "value2" in query_params["name2$"]
        assert "type" in query_params
        assert "tabloid" in query_params["type"]


@pytest.mark.parametrize("page_size", [1, 10, 100, 1_000])
def test_queryset_endpoint_pagesize_all(server: TSC.Server, page_size: int) -> None:
    with requests_mock.mock() as m:
        m.get(f"{server.views.baseurl}?pageSize={page_size}", text=SLICING_QUERYSET_PAGE_1.read_text())
        queryset = server.views.all(page_size=page_size)
        assert queryset.request_options.pagesize == page_size
        _ = list(queryset)


@pytest.mark.parametrize("page_size", [1, 10, 100, 1_000])
def test_queryset_endpoint_pagesize_filter(server: TSC.Server, page_size: int) -> None:
    with requests_mock.mock() as m:
        m.get(f"{server.views.baseurl}?pageSize={page_size}", text=SLICING_QUERYSET_PAGE_1.read_text())
        queryset = server.views.filter(page_size=page_size)
        assert queryset.request_options.pagesize == page_size
        _ = list(queryset)


@pytest.mark.parametrize("page_size", [1, 10, 100, 1_000])
def test_queryset_pagesize_filter(server: TSC.Server, page_size: int) -> None:
    with requests_mock.mock() as m:
        m.get(f"{server.views.baseurl}?pageSize={page_size}", text=SLICING_QUERYSET_PAGE_1.read_text())
        queryset = server.views.all().filter(page_size=page_size)
        assert queryset.request_options.pagesize == page_size
        _ = list(queryset)


def test_language_export(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = server.views.baseurl + "/456/data"
        opts = TSC.PDFRequestOptions()
        opts.language = "en-US"

        resp = server.users.get_request(url, request_object=opts)
        query_string = parse_qs(resp.request.query)
        assert "language" in query_string
        assert "en-us" in query_string["language"]


def test_queryset_fields(server: TSC.Server) -> None:
    loop = server.users.fields("id")
    assert "id" in loop.request_options.fields
    assert "_default_" in loop.request_options.fields


def test_queryset_only_fields(server: TSC.Server) -> None:
    loop = server.users.only_fields("id")
    assert "id" in loop.request_options.fields
    assert "_default_" not in loop.request_options.fields


def test_queryset_field_order(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.views.baseurl, text=SLICING_QUERYSET_PAGE_1.read_text())
        loop = server.views.fields("id", "name")
        list(loop)
        history = m.request_history[0]

    fields = history.qs.get("fields", [""])[0].split(",")

    assert fields[0] == "_default_"
    assert "id" in fields
    assert "name" in fields


def test_queryset_field_all(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(server.views.baseurl, text=SLICING_QUERYSET_PAGE_1.read_text())
        loop = server.views.fields("id", "name", "_all_")
        list(loop)
        history = m.request_history[0]

    fields = history.qs.get("fields", [""])[0]

    assert fields == "_all_"
