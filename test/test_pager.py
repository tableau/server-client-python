import contextlib
import os
import unittest
import xml.etree.ElementTree as ET

import requests_mock

import tableauserverclient as TSC
from tableauserverclient.config import config

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")

GET_VIEW_XML = os.path.join(TEST_ASSET_DIR, "view_get.xml")
GET_XML_PAGE1 = os.path.join(TEST_ASSET_DIR, "workbook_get_page_1.xml")
GET_XML_PAGE2 = os.path.join(TEST_ASSET_DIR, "workbook_get_page_2.xml")
GET_XML_PAGE3 = os.path.join(TEST_ASSET_DIR, "workbook_get_page_3.xml")


@contextlib.contextmanager
def set_env(**environ):
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


class PagerTests(unittest.TestCase):
    def setUp(self):
        self.server = TSC.Server("http://test", False)

        # Fake sign in
        self.server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
        self.server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

        self.baseurl = self.server.workbooks.baseurl

    def test_pager_with_no_options(self) -> None:
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

    def test_pager_with_options(self) -> None:
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

    def test_pager_with_env_var(self) -> None:
        with set_env(TSC_PAGE_SIZE="1000"):
            assert config.PAGE_SIZE == 1000
            loop = TSC.Pager(self.server.workbooks)
            assert loop._options.pagesize == 1000

    def test_queryset_with_env_var(self) -> None:
        with set_env(TSC_PAGE_SIZE="1000"):
            assert config.PAGE_SIZE == 1000
            loop = self.server.workbooks.all()
            assert loop.request_options.pagesize == 1000

    def test_pager_view(self) -> None:
        with open(GET_VIEW_XML, "rb") as f:
            view_xml = f.read().decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.server.views.baseurl, text=view_xml)
            for view in TSC.Pager(self.server.views):
                assert view.name is not None

    def test_queryset_no_matches(self) -> None:
        elem = ET.Element("tsResponse", xmlns="http://tableau.com/api")
        ET.SubElement(elem, "pagination", totalAvailable="0")
        ET.SubElement(elem, "groups")
        xml = ET.tostring(elem).decode("utf-8")
        with requests_mock.mock() as m:
            m.get(self.server.groups.baseurl, text=xml)
            all_groups = self.server.groups.all()
            groups = list(all_groups)
        assert len(groups) == 0
