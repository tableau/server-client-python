import re
import unittest
from urllib.parse import parse_qs

import pytest
import requests_mock

import tableauserverclient as TSC


class SortTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test", False)
        self.server.version = "3.10"
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
        self.baseurl = self.server.workbooks.baseurl

    def test_empty_filter(self):
        with pytest.raises(TypeError):
            TSC.Filter("")

    def test_filter_equals(self):
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            opts = TSC.RequestOptions(pagesize=13, pagenumber=13)
            opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "Superstore"))

            resp = self.server.workbooks.get_request(url, request_object=opts)
            query = parse_qs(resp.request.query)
            assert "pagenumber" in query
            assert query["pagenumber"] == ["13"]
            assert "pagesize" in query
            assert query["pagesize"] == ["13"]
            assert "filter" in query
            assert query["filter"] == ["name:eq:superstore"]

    def test_filter_equals_list(self):
        with pytest.raises(ValueError, match="Filter values can only be a list if the operator is 'in'.") as cm:
            TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.Equals, ["foo", "bar"])

    def test_filter_in(self):
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            opts = TSC.RequestOptions(pagesize=13, pagenumber=13)

            opts.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["stocks", "market"])
            )

            resp = self.server.workbooks.get_request(url, request_object=opts)
            query = parse_qs(resp.request.query)
            assert "pagenumber" in query
            assert query["pagenumber"] == ["13"]
            assert "pagesize" in query
            assert query["pagesize"] == ["13"]
            assert "filter" in query
            assert query["filter"] == ["tags:in:[stocks,market]"]

    def test_sort_asc(self):
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            opts = TSC.RequestOptions(pagesize=13, pagenumber=13)
            opts.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))

            resp = self.server.workbooks.get_request(url, request_object=opts)
            query = parse_qs(resp.request.query)
            assert "pagenumber" in query
            assert query["pagenumber"] == ["13"]
            assert "pagesize" in query
            assert query["pagesize"] == ["13"]
            assert "sort" in query
            assert query["sort"] == ["name:asc"]

    def test_filter_combo(self):
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

            opts.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.SiteRole, TSC.RequestOptions.Operator.Equals, "Publisher")
            )

            resp = self.server.workbooks.get_request(url, request_object=opts)

            query = parse_qs(resp.request.query)
            assert "pagenumber" in query
            assert query["pagenumber"] == ["13"]
            assert "pagesize" in query
            assert query["pagesize"] == ["13"]
            assert "filter" in query
            assert query["filter"] == ["lastlogin:gte:2017-01-15t00:00:00:00z,siterole:eq:publisher"]
