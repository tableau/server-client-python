from contextlib import ExitStack
import re
from collections.abc import Iterable
import uuid
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


def add_tag_xml_response_factory(tags: Iterable[str]) -> str:
    root = ET.Element("tsResponse")
    tags_element = ET.SubElement(root, "tags")
    for tag in tags:
        tag_element = ET.SubElement(tags_element, "tag")
        tag_element.attrib["label"] = tag
    root.attrib["xmlns"] = "http://tableau.com/api"
    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def batch_add_tags_xml_response_factory(tags, content):
    root = ET.Element("tsResponse")
    tag_batch = ET.SubElement(root, "tagBatch")
    tags_element = ET.SubElement(tag_batch, "tags")
    for tag in tags:
        tag_element = ET.SubElement(tags_element, "tag")
        tag_element.attrib["label"] = tag
    contents_element = ET.SubElement(tag_batch, "contents")
    for item in content:
        content_elem = ET.SubElement(contents_element, "content")
        content_elem.attrib["id"] = item.id or "some_id"
        t = item.__class__.__name__.replace("Item", "") or ""
        content_elem.attrib["contentType"] = t
    root.attrib["xmlns"] = "http://tableau.com/api"
    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def make_workbook() -> TSC.WorkbookItem:
    workbook = TSC.WorkbookItem("project", "test")
    workbook._id = str(uuid.uuid4())
    return workbook


def make_view() -> TSC.ViewItem:
    view = TSC.ViewItem()
    view._id = str(uuid.uuid4())
    return view


def make_datasource() -> TSC.DatasourceItem:
    datasource = TSC.DatasourceItem("project", "test")
    datasource._id = str(uuid.uuid4())
    return datasource


def make_table() -> TSC.TableItem:
    table = TSC.TableItem("project", "test")
    table._id = str(uuid.uuid4())
    return table


def make_database() -> TSC.DatabaseItem:
    database = TSC.DatabaseItem("project", "test")
    database._id = str(uuid.uuid4())
    return database


def make_flow() -> TSC.FlowItem:
    flow = TSC.FlowItem("project", "test")
    flow._id = str(uuid.uuid4())
    return flow


def make_vconn() -> TSC.VirtualConnectionItem:
    vconn = TSC.VirtualConnectionItem("test")
    vconn._id = str(uuid.uuid4())
    return vconn


sample_taggable_items = (
    [
        ("workbooks", make_workbook()),
        ("workbooks", "some_id"),
        ("views", make_view()),
        ("views", "some_id"),
        ("datasources", make_datasource()),
        ("datasources", "some_id"),
        ("tables", make_table()),
        ("tables", "some_id"),
        ("databases", make_database()),
        ("databases", "some_id"),
        ("flows", make_flow()),
        ("flows", "some_id"),
        ("virtual_connections", make_vconn()),
        ("virtual_connections", "some_id"),
    ],
)

sample_tags = [
    "a",
    ["a", "b"],
    ["a", "b", "c", "c"],
]


@pytest.mark.parametrize("endpoint_type, item", *sample_taggable_items)
@pytest.mark.parametrize("tags", sample_tags)
def test_add_tags(get_server, endpoint_type, item, tags) -> None:
    add_tags_xml = add_tag_xml_response_factory(tags)
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


@pytest.mark.parametrize("endpoint_type, item", *sample_taggable_items)
@pytest.mark.parametrize("tags", sample_tags)
def test_delete_tags(get_server, endpoint_type, item, tags) -> None:
    add_tags_xml = add_tag_xml_response_factory(tags)
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

    tag_set = set(tags)
    assert len(history) == len(tag_set)
    urls = {r.url.split("/")[-1] for r in history}
    assert urls == tag_set


@pytest.mark.parametrize("endpoint_type, item", *sample_taggable_items)
@pytest.mark.parametrize("tags", sample_tags)
def test_update_tags(get_server, endpoint_type, item, tags) -> None:
    endpoint = getattr(get_server, endpoint_type)
    id_ = getattr(item, "id", item)
    tags = set([tags] if isinstance(tags, str) else tags)
    with ExitStack() as stack:
        if isinstance(item, str):
            stack.enter_context(pytest.raises((ValueError, NotImplementedError)))
        elif hasattr(item, "_initial_tags"):
            initial_tags = {"x", "y", "z"}
            item._initial_tags = initial_tags
            add_tags_xml = add_tag_xml_response_factory(tags - initial_tags)
            delete_tags_xml = add_tag_xml_response_factory(initial_tags - tags)
            m = stack.enter_context(requests_mock.mock())
            m.put(
                f"{endpoint.baseurl}/{id_}/tags",
                status_code=200,
                text=add_tags_xml,
            )

            tag_paths = "|".join(initial_tags - tags)
            tag_paths = f"({tag_paths})"
            matcher = re.compile(rf"{endpoint.baseurl}\/{id_}\/tags\/{tag_paths}")
            m.delete(
                matcher,
                status_code=200,
                text=delete_tags_xml,
            )

        else:
            stack.enter_context(pytest.raises(NotImplementedError))

        endpoint.update_tags(item)


def test_tags_batch_add(get_server) -> None:
    server = get_server
    content = [make_workbook(), make_view(), make_datasource(), make_table(), make_database()]
    tags = ["a", "b"]
    add_tags_xml = batch_add_tags_xml_response_factory(tags, content)
    with requests_mock.mock() as m:
        m.put(
            f"{server.tags.baseurl}:batchCreate",
            status_code=200,
            text=add_tags_xml,
        )
        tag_result = server.tags.batch_add(tags, content)

    assert set(tag_result) == set(tags)


def test_tags_batch_delete(get_server) -> None:
    server = get_server
    content = [make_workbook(), make_view(), make_datasource(), make_table(), make_database()]
    tags = ["a", "b"]
    add_tags_xml = batch_add_tags_xml_response_factory(tags, content)
    with requests_mock.mock() as m:
        m.put(
            f"{server.tags.baseurl}:batchDelete",
            status_code=200,
            text=add_tags_xml,
        )
        tag_result = server.tags.batch_delete(tags, content)

    assert set(tag_result) == set(tags)
