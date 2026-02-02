from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import parse_datetime

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_FAVORITES_XML = TEST_ASSET_DIR / "favorites_get.xml"
ADD_FAVORITE_WORKBOOK_XML = TEST_ASSET_DIR / "favorites_add_workbook.xml"
ADD_FAVORITE_VIEW_XML = TEST_ASSET_DIR / "favorites_add_view.xml"
ADD_FAVORITE_DATASOURCE_XML = TEST_ASSET_DIR / "favorites_add_datasource.xml"
ADD_FAVORITE_PROJECT_XML = TEST_ASSET_DIR / "favorites_add_project.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    server = TSC.Server("http://test", False)
    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.5"

    return server


@pytest.fixture(scope="function")
def user() -> TSC.UserItem:
    user = TSC.UserItem("alice", TSC.UserItem.Roles.Viewer)
    user._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
    return user


def test_get(server: TSC.Server, user: TSC.UserItem) -> None:
    response_xml = GET_FAVORITES_XML.read_text()
    with requests_mock.mock() as m:
        m.get(f"{server.favorites.baseurl}/{user.id}", text=response_xml)
        server.favorites.get(user)
    assert user._favorites is not None
    assert len(user.favorites["workbooks"]) == 1
    assert len(user.favorites["views"]) == 1
    assert len(user.favorites["projects"]) == 1
    assert len(user.favorites["datasources"]) == 1

    workbook = user.favorites["workbooks"][0]
    print("favorited: ")
    print(workbook)
    view = user.favorites["views"][0]
    datasource = user.favorites["datasources"][0]
    project = user.favorites["projects"][0]

    assert workbook.id == "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00"
    assert view.id == "d79634e1-6063-4ec9-95ff-50acbf609ff5"
    assert datasource.id == "e76a1461-3b1d-4588-bf1b-17551a879ad9"
    assert project.id == "1d0304cd-3796-429f-b815-7258370b9b74"

    collection = user.favorites["collections"][0]

    assert collection.id == "8c57cb8a-d65f-4a32-813e-5a3f86e8f94e"
    assert collection.name == "sample collection"
    assert collection.description == "description for sample collection"
    assert collection.total_item_count == 3
    assert collection.permissioned_item_count == 2
    assert collection.visibility == "Private"
    assert collection.created_at == parse_datetime("2016-08-11T21:22:40Z")
    assert collection.updated_at == parse_datetime("2016-08-11T21:34:17Z")


def test_add_favorite_workbook(server: TSC.Server, user: TSC.UserItem) -> None:
    response_xml = ADD_FAVORITE_WORKBOOK_XML.read_text()
    workbook = TSC.WorkbookItem("")
    workbook._id = "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00"
    workbook.name = "Superstore"
    with requests_mock.mock() as m:
        m.put(f"{server.favorites.baseurl}/{user.id}", text=response_xml)
        server.favorites.add_favorite_workbook(user, workbook)


def test_add_favorite_view(server: TSC.Server, user: TSC.UserItem) -> None:
    response_xml = ADD_FAVORITE_VIEW_XML.read_text()
    view = TSC.ViewItem()
    view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
    view._name = "ENDANGERED SAFARI"
    with requests_mock.mock() as m:
        m.put(f"{server.favorites.baseurl}/{user.id}", text=response_xml)
        server.favorites.add_favorite_view(user, view)


def test_add_favorite_datasource(server: TSC.Server, user: TSC.UserItem) -> None:
    response_xml = ADD_FAVORITE_DATASOURCE_XML.read_text()
    datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    datasource._id = "e76a1461-3b1d-4588-bf1b-17551a879ad9"
    datasource.name = "SampleDS"
    with requests_mock.mock() as m:
        m.put(f"{server.favorites.baseurl}/{user.id}", text=response_xml)
        server.favorites.add_favorite_datasource(user, datasource)


def test_add_favorite_project(server: TSC.Server, user: TSC.UserItem) -> None:
    server.version = "3.1"
    baseurl = server.favorites.baseurl
    response_xml = ADD_FAVORITE_PROJECT_XML.read_text()
    project = TSC.ProjectItem("Tableau")
    project._id = "1d0304cd-3796-429f-b815-7258370b9b74"
    with requests_mock.mock() as m:
        m.put(f"{baseurl}/{user.id}", text=response_xml)
        server.favorites.add_favorite_project(user, project)


def test_delete_favorite_workbook(server: TSC.Server, user: TSC.UserItem) -> None:
    workbook = TSC.WorkbookItem("")
    workbook._id = "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00"
    workbook.name = "Superstore"
    with requests_mock.mock() as m:
        m.delete(f"{server.favorites.baseurl}/{user.id}/workbooks/{workbook.id}")
        server.favorites.delete_favorite_workbook(user, workbook)


def test_delete_favorite_view(server: TSC.Server, user: TSC.UserItem) -> None:
    view = TSC.ViewItem()
    view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
    view._name = "ENDANGERED SAFARI"
    with requests_mock.mock() as m:
        m.delete(f"{server.favorites.baseurl}/{user.id}/views/{view.id}")
        server.favorites.delete_favorite_view(user, view)


def test_delete_favorite_datasource(server: TSC.Server, user: TSC.UserItem) -> None:
    datasource = TSC.DatasourceItem("ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    datasource._id = "e76a1461-3b1d-4588-bf1b-17551a879ad9"
    datasource.name = "SampleDS"
    with requests_mock.mock() as m:
        m.delete(f"{server.favorites.baseurl}/{user.id}/datasources/{datasource.id}")
        server.favorites.delete_favorite_datasource(user, datasource)


def test_delete_favorite_project(server: TSC.Server, user: TSC.UserItem) -> None:
    server.version = "3.1"
    baseurl = server.favorites.baseurl
    project = TSC.ProjectItem("Tableau")
    project._id = "1d0304cd-3796-429f-b815-7258370b9b74"
    with requests_mock.mock() as m:
        m.delete(f"{baseurl}/{user.id}/projects/{project.id}")
        server.favorites.delete_favorite_project(user, project)
