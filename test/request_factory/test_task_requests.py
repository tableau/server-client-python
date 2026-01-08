import xml.etree.ElementTree as ET
from unittest.mock import Mock

import pytest

from tableauserverclient.server.request_factory import TaskRequest


@pytest.fixture
def task_request() -> TaskRequest:
    return TaskRequest()


@pytest.fixture
def xml_request() -> ET.Element:
    return ET.Element("tsRequest")


def test_refresh_req_default(task_request: TaskRequest, xml_request: ET.Element) -> None:
    result = task_request.refresh_req()
    assert result == ET.tostring(xml_request)


def test_refresh_req_incremental(task_request: TaskRequest) -> None:
    with pytest.raises(ValueError):
        task_request.refresh_req(incremental=True)


def test_refresh_req_with_parent_srv_version_3_25(task_request: TaskRequest) -> None:
    parent_srv = Mock()
    parent_srv.check_at_least_version.return_value = True
    result = task_request.refresh_req(incremental=True, parent_srv=parent_srv)
    expected_xml = ET.Element("tsRequest")
    task_element = ET.SubElement(expected_xml, "extractRefresh")
    task_element.attrib["incremental"] = "true"
    assert result == ET.tostring(expected_xml)


def test_refresh_req_with_parent_srv_version_3_25_non_incremental(task_request: TaskRequest) -> None:
    parent_srv = Mock()
    parent_srv.check_at_least_version.return_value = True
    result = task_request.refresh_req(incremental=False, parent_srv=parent_srv)
    expected_xml = ET.Element("tsRequest")
    ET.SubElement(expected_xml, "extractRefresh")
    assert result == ET.tostring(expected_xml)


def test_refresh_req_with_parent_srv_version_below_3_25(task_request: TaskRequest) -> None:
    parent_srv = Mock()
    parent_srv.check_at_least_version.return_value = False
    with pytest.raises(ValueError):
        task_request.refresh_req(incremental=True, parent_srv=parent_srv)


def test_refresh_req_with_parent_srv_version_below_3_25_non_incremental(
    task_request: TaskRequest, xml_request: ET.Element
) -> None:
    parent_srv = Mock()
    parent_srv.check_at_least_version.return_value = False
    result = task_request.refresh_req(incremental=False, parent_srv=parent_srv)
    assert result == ET.tostring(xml_request)
