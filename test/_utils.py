import os.path
import unittest
from xml.etree import ElementTree as ET
from contextlib import contextmanager

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")


def asset(filename):
    return os.path.join(TEST_ASSET_DIR, filename)


def read_xml_asset(filename):
    with open(asset(filename), "rb") as f:
        return f.read().decode("utf-8")


def read_xml_assets(*args):
    return map(read_xml_asset, args)


def server_response_error_factory(code: str, summary: str, detail: str) -> str:
    root = ET.Element("tsResponse")
    error = ET.SubElement(root, "error")
    error.attrib["code"] = code

    summary_element = ET.SubElement(error, "summary")
    summary_element.text = summary

    detail_element = ET.SubElement(error, "detail")
    detail_element.text = detail
    return ET.tostring(root, encoding="utf-8").decode("utf-8")


@contextmanager
def mocked_time():
    mock_time = 0

    def sleep_mock(interval):
        nonlocal mock_time
        mock_time += interval

    def get_time():
        return mock_time

    try:
        patch = unittest.mock.patch
    except AttributeError:
        from unittest.mock import patch
    with patch("time.sleep", sleep_mock), patch("time.time", get_time):
        yield get_time
