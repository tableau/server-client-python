import os.path
import unittest
from contextlib import contextmanager

TEST_ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")


def asset(filename):
    return os.path.join(TEST_ASSET_DIR, filename)


def read_xml_asset(filename):
    with open(asset(filename), "rb") as f:
        return f.read().decode("utf-8")


def read_xml_assets(*args):
    return map(read_xml_asset, args)


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
