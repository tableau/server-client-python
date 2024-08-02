import re
from typing import Iterable
from xml.etree import ElementTree as ET

import pytest
import requests_mock
import tableauserverclient as TSC


@pytest.fixture
def get_server() -> TSC.Server:
    server = TSC.Server("http://test", False)

    # Fake sign in
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.28"
    return server


def xml_response_factory(tags: Iterable[str]) -> str:
    root = ET.Element("tsResponse")
    tags_element = ET.SubElement(root, "tags")
    for tag in tags:
        tag_element = ET.SubElement(tags_element, "tag")
        tag_element.attrib["label"] = tag
    root.attrib["xmlns"] = "http://tableau.com/api"
    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def make_workbook() -> TSC.WorkbookItem:
    workbook = TSC.WorkbookItem("project", "test")
    workbook._id = "06b944d2-959d-4604-9305-12323c95e70e"
    return workbook


def make_view() -> TSC.ViewItem:
    view = TSC.ViewItem()
    view._id = "06b944d2-959d-4604-9305-12323c95e70e"
    return view


def make_datasource() -> TSC.DatasourceItem:
    datasource = TSC.DatasourceItem("project", "test")
    datasource._id = "06b944d2-959d-4604-9305-12323c95e70e"
    return datasource


@pytest.mark.parametrize(
    "endpoint_type, item",
    [
        ("workbooks", make_workbook()),
        ("views", make_view()),
        ("datasources", make_datasource()),
    ],
)
@pytest.mark.parametrize(
    "tags",
    [
        "a",
        ["a", "b"],
    ],
)
def test_add_tags(get_server, endpoint_type, item, tags) -> None:
    add_tags_xml = xml_response_factory(tags)
    endpoint = getattr(get_server, endpoint_type)
    id_ = getattr(item, "id", item)

    with requests_mock.mock() as m:
        m.put(
            f"{endpoint.baseurl}/{id_}/tags",
            status_code=200,
            text=add_tags_xml,
        )
        tag_result = endpoint.add_tags(item, tags)

    if isinstance(tags, str):
        tags = [tags]
    assert set(tag_result) == set(tags)


@pytest.mark.parametrize(
    "endpoint_type, item",
    [
        ("workbooks", make_workbook()),
        ("views", make_view()),
        ("datasources", make_datasource()),
    ],
)
@pytest.mark.parametrize(
    "tags",
    [
        "a",
        ["a", "b"],
    ],
)
def test_delete_tags(get_server, endpoint_type, item, tags) -> None:
    add_tags_xml = xml_response_factory(tags)
    endpoint = getattr(get_server, endpoint_type)
    id_ = getattr(item, "id", item)

    if isinstance(tags, str):
        tags = [tags]
    tag_paths = "|".join(tags)
    tag_paths = f"({tag_paths})"
    matcher = re.compile(rf"{endpoint.baseurl}\/{id_}\/tags\/{tag_paths}")
    with requests_mock.mock() as m:
        m.delete(
            matcher,
            status_code=200,
            text=add_tags_xml,
        )
        endpoint.delete_tags(item, tags)
        history = m.request_history

    assert len(history) == len(tags)
    urls = sorted([r.url.split("/")[-1] for r in history])
    assert set(urls) == set(tags)
