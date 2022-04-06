import os
import unittest

import requests_mock

import tableauserverclient as TSC

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_XML_PAGE1 = os.path.join(TEST_ASSET_DIR, "workbook_get_page_1.xml")
GET_XML_PAGE2 = os.path.join(TEST_ASSET_DIR, "workbook_get_page_2.xml")
GET_XML_PAGE3 = os.path.join(TEST_ASSET_DIR, "workbook_get_page_3.xml")


class PagerTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test", False)

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.workbooks.baseurl

    def test_pager_with_no_options(self):
        with open(GET_XML_PAGE1, "rb") as f:
            page_1 = f.read().decode("utf-8")
        with open(GET_XML_PAGE2, "rb") as f:
            page_2 = f.read().decode("utf-8")
        with open(GET_XML_PAGE3, "rb") as f:
            page_3 = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            # Register Pager with default request options
            m.get(self.baseurl, text=page_1)

            # Register Pager with some pages
            m.get(self.baseurl + "?pageNumber=1&pageSize=1", text=page_1)
            m.get(self.baseurl + "?pageNumber=2&pageSize=1", text=page_2)
            m.get(self.baseurl + "?pageNumber=3&pageSize=1", text=page_3)

            # No options should get all 3
            workbooks = list(TSC.Pager(self.server.workbooks))
            self.assertTrue(len(workbooks) == 3)

            # Let's check that workbook items aren't duplicates
            wb1, wb2, wb3 = workbooks
            self.assertEqual(wb1.name, "Page1Workbook")
            self.assertEqual(wb2.name, "Page2Workbook")
            self.assertEqual(wb3.name, "Page3Workbook")

    def test_pager_with_options(self):
        with open(GET_XML_PAGE1, "rb") as f:
            page_1 = f.read().decode("utf-8")
        with open(GET_XML_PAGE2, "rb") as f:
            page_2 = f.read().decode("utf-8")
        with open(GET_XML_PAGE3, "rb") as f:
            page_3 = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            # Register Pager with some pages
            m.get(self.baseurl + "?pageNumber=1&pageSize=1", complete_qs=True, text=page_1)
            m.get(self.baseurl + "?pageNumber=2&pageSize=1", complete_qs=True, text=page_2)
            m.get(self.baseurl + "?pageNumber=3&pageSize=1", complete_qs=True, text=page_3)
            m.get(self.baseurl + "?pageNumber=1&pageSize=3", complete_qs=True, text=page_1)

            # Starting on page 2 should get 2 out of 3
            opts = TSC.RequestOptions(2, 1)
            workbooks = list(TSC.Pager(self.server.workbooks, opts))
            self.assertTrue(len(workbooks) == 2)

            # Check that the workbooks are the 2 we think they should be
            wb2, wb3 = workbooks
            self.assertEqual(wb2.name, "Page2Workbook")
            self.assertEqual(wb3.name, "Page3Workbook")

            # Starting on 1 with pagesize of 3 should get all 3
            opts = TSC.RequestOptions(1, 3)
            workbooks = list(TSC.Pager(self.server.workbooks, opts))
            self.assertTrue(len(workbooks) == 3)
            wb1, wb2, wb3 = workbooks
            self.assertEqual(wb1.name, "Page1Workbook")
            self.assertEqual(wb2.name, "Page2Workbook")
            self.assertEqual(wb3.name, "Page3Workbook")

            # Starting on 3 with pagesize of 1 should get the last item
            opts = TSC.RequestOptions(3, 1)
            workbooks = list(TSC.Pager(self.server.workbooks, opts))
            self.assertTrue(len(workbooks) == 1)
            # Should have the last workbook
            wb3 = workbooks.pop()
            self.assertEqual(wb3.name, "Page3Workbook")
