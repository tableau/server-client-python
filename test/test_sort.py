from urllib.parse import parse_qs

import pytest
import requests_mock

import tableauserverclient as TSC


@pytest.fixture(scope="function")
def server():
    """Fixture to create a TSC.Server instance for testing."""
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_empty_filter() -> None:
    with pytest.raises(TypeError):
        TSC.Filter("")  # type: ignore


def test_filter_equals(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
        opts = TSC.RequestOptions(pagesize=13, pagenumber=13)
        opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "Superstore"))

        resp = server.workbooks.get_request(url, request_object=opts)
        query = parse_qs(resp.request.query)
        assert "pagenumber" in query
        assert query["pagenumber"] == ["13"]
        assert "pagesize" in query
        assert query["pagesize"] == ["13"]
        assert "filter" in query
        assert query["filter"] == ["name:eq:superstore"]


def test_filter_equals_list() -> None:
    with pytest.raises(ValueError, match="Filter values can only be a list if the operator is 'in'.") as cm:
        TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.Equals, ["foo", "bar"])


def test_filter_in(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
        opts = TSC.RequestOptions(pagesize=13, pagenumber=13)

        opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["stocks", "market"]))

        resp = server.workbooks.get_request(url, request_object=opts)
        query = parse_qs(resp.request.query)
        assert "pagenumber" in query
        assert query["pagenumber"] == ["13"]
        assert "pagesize" in query
        assert query["pagesize"] == ["13"]
        assert "filter" in query
        assert query["filter"] == ["tags:in:[stocks,market]"]


def test_sort_asc(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
        opts = TSC.RequestOptions(pagesize=13, pagenumber=13)
        opts.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))

        resp = server.workbooks.get_request(url, request_object=opts)
        query = parse_qs(resp.request.query)
        assert "pagenumber" in query
        assert query["pagenumber"] == ["13"]
        assert "pagesize" in query
        assert query["pagesize"] == ["13"]
        assert "sort" in query
        assert query["sort"] == ["name:asc"]


def test_filter_combo(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(requests_mock.ANY)
        url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/users"
        opts = TSC.RequestOptions(pagesize=13, pagenumber=13)

        opts.filter.add(
            TSC.Filter(
                TSC.RequestOptions.Field.LastLogin,
                TSC.RequestOptions.Operator.GreaterThanOrEqual,
                "2017-01-15T00:00:00:00Z",
            )
        )

        opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.SiteRole, TSC.RequestOptions.Operator.Equals, "Publisher"))

        resp = server.workbooks.get_request(url, request_object=opts)

        query = parse_qs(resp.request.query)
        assert "pagenumber" in query
        assert query["pagenumber"] == ["13"]
        assert "pagesize" in query
        assert query["pagesize"] == ["13"]
        assert "filter" in query
        assert query["filter"] == ["lastlogin:gte:2017-01-15t00:00:00:00z,siterole:eq:publisher"]
