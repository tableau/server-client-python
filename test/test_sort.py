import re
import unittest

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
        self.assertRaises(TypeError, TSC.Filter, "")

    def test_filter_equals(self):
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            opts = TSC.RequestOptions(pagesize=13, pagenumber=13)
            opts.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "Superstore"))

            resp = self.server.workbooks.get_request(url, request_object=opts)

            self.assertTrue(re.search("pagenumber=13", resp.request.query))
            self.assertTrue(re.search("pagesize=13", resp.request.query))
            self.assertTrue(re.search("filter=name%3aeq%3asuperstore", resp.request.query))

    def test_filter_equals_list(self):
        with self.assertRaises(ValueError) as cm:
            TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.Equals, ["foo", "bar"])

        self.assertEqual("Filter values can only be a list if the operator is 'in'.", str(cm.exception)),

    def test_filter_in(self):
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            opts = TSC.RequestOptions(pagesize=13, pagenumber=13)

            opts.filter.add(
                TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["stocks", "market"])
            )

            resp = self.server.workbooks.get_request(url, request_object=opts)
            self.assertTrue(re.search("pagenumber=13", resp.request.query))
            self.assertTrue(re.search("pagesize=13", resp.request.query))
            self.assertTrue(re.search("filter=tags%3ain%3a%5bstocks%2cmarket%5d", resp.request.query))

    def test_sort_asc(self):
        with requests_mock.mock() as m:
            m.get(requests_mock.ANY)
            url = "http://test/api/2.3/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks"
            opts = TSC.RequestOptions(pagesize=13, pagenumber=13)
            opts.sort.add(TSC.Sort(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Direction.Asc))

            resp = self.server.workbooks.get_request(url, request_object=opts)

            self.assertTrue(re.search("pagenumber=13", resp.request.query))
            self.assertTrue(re.search("pagesize=13", resp.request.query))
            self.assertTrue(re.search("sort=name%3aasc", resp.request.query))

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

            expected = (
                "pagenumber=13&pagesize=13&filter=lastlogin%3agte%3a"
                "2017-01-15t00%3a00%3a00%3a00z%2csiterole%3aeq%3apublisher"
            )

            self.assertTrue(re.search("pagenumber=13", resp.request.query))
            self.assertTrue(re.search("pagesize=13", resp.request.query))
            self.assertTrue(
                re.search(
                    "filter=lastlogin%3agte%3a2017-01-15t00%3a00%3a00%3a00z%2csiterole%3aeq%3apublisher",
                    resp.request.query,
                )
            )


if __name__ == "__main__":
    unittest.main()
