import unittest
import xml.etree.ElementTree as ET
from unittest.mock import Mock
from tableauserverclient.server.request_factory import TaskRequest


class TestTaskRequest(unittest.TestCase):
    def setUp(self):
        self.task_request = TaskRequest()
        self.xml_request = ET.Element("tsRequest")

    def test_refresh_req_default(self):
        result = self.task_request.refresh_req()
        self.assertEqual(result, ET.tostring(self.xml_request))

    def test_refresh_req_incremental(self):
        with self.assertRaises(ValueError):
            self.task_request.refresh_req(incremental=True)

    def test_refresh_req_with_parent_srv_version_3_25(self):
        parent_srv = Mock()
        parent_srv.check_at_least_version.return_value = True
        result = self.task_request.refresh_req(incremental=True, parent_srv=parent_srv)
        expected_xml = ET.Element("tsRequest")
        task_element = ET.SubElement(expected_xml, "extractRefresh")
        task_element.attrib["incremental"] = "true"
        self.assertEqual(result, ET.tostring(expected_xml))

    def test_refresh_req_with_parent_srv_version_3_25_non_incremental(self):
        parent_srv = Mock()
        parent_srv.check_at_least_version.return_value = True
        result = self.task_request.refresh_req(incremental=False, parent_srv=parent_srv)
        expected_xml = ET.Element("tsRequest")
        ET.SubElement(expected_xml, "extractRefresh")
        self.assertEqual(result, ET.tostring(expected_xml))

    def test_refresh_req_with_parent_srv_version_below_3_25(self):
        parent_srv = Mock()
        parent_srv.check_at_least_version.return_value = False
        with self.assertRaises(ValueError):
            self.task_request.refresh_req(incremental=True, parent_srv=parent_srv)

    def test_refresh_req_with_parent_srv_version_below_3_25_non_incremental(self):
        parent_srv = Mock()
        parent_srv.check_at_least_version.return_value = False
        result = self.task_request.refresh_req(incremental=False, parent_srv=parent_srv)
        self.assertEqual(result, ET.tostring(self.xml_request))
