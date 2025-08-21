import os
import re
import requests_mock
import tempfile
from defusedxml.ElementTree import fromstring
from io import BytesIO
from pathlib import Path

import pytest

import tableauserverclient as TSC
from tableauserverclient.datetime_helpers import format_datetime, parse_datetime
from tableauserverclient.models import UserItem, GroupItem, PermissionsRule
from tableauserverclient.server.endpoint.exceptions import InternalServerError, UnsupportedAttributeError
from tableauserverclient.server.request_factory import RequestFactory
from ._utils import read_xml_assets, asset

TEST_ASSET_DIR = Path(__file__).parent / "assets"

ADD_TAGS_XML = TEST_ASSET_DIR / "workbook_add_tags.xml"
GET_BY_ID_XML = TEST_ASSET_DIR / "workbook_get_by_id.xml"
GET_BY_ID_XML_PERSONAL = TEST_ASSET_DIR / "workbook_get_by_id_personal.xml"
GET_EMPTY_XML = TEST_ASSET_DIR / "workbook_get_empty.xml"
GET_INVALID_DATE_XML = TEST_ASSET_DIR / "workbook_get_invalid_date.xml"
GET_XML = TEST_ASSET_DIR / "workbook_get.xml"
GET_XML_ALL_FIELDS = TEST_ASSET_DIR / "workbook_get_all_fields.xml"
ODATA_XML = TEST_ASSET_DIR / "odata_connection.xml"
POPULATE_CONNECTIONS_XML = TEST_ASSET_DIR / "workbook_populate_connections.xml"
POPULATE_PDF = TEST_ASSET_DIR / "populate_pdf.pdf"
POPULATE_POWERPOINT = TEST_ASSET_DIR / "populate_powerpoint.pptx"
POPULATE_PERMISSIONS_XML = TEST_ASSET_DIR / "workbook_populate_permissions.xml"
POPULATE_PREVIEW_IMAGE = TEST_ASSET_DIR / "RESTAPISample Image.png"
POPULATE_VIEWS_XML = TEST_ASSET_DIR / "workbook_populate_views.xml"
POPULATE_VIEWS_USAGE_XML = TEST_ASSET_DIR / "workbook_populate_views_usage.xml"
PUBLISH_XML = TEST_ASSET_DIR / "workbook_publish.xml"
PUBLISH_ASYNC_XML = TEST_ASSET_DIR / "workbook_publish_async.xml"
REFRESH_XML = TEST_ASSET_DIR / "workbook_refresh.xml"
REVISION_XML = TEST_ASSET_DIR / "workbook_revision.xml"
UPDATE_XML = TEST_ASSET_DIR / "workbook_update.xml"
UPDATE_PERMISSIONS = TEST_ASSET_DIR / "workbook_update_permissions.xml"
UPDATE_CONNECTIONS_XML = TEST_ASSET_DIR / "workbook_update_connections.xml"


@pytest.fixture(scope="function")
def server():
    server = TSC.Server("http://test", False)

    # Fake sign in
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_get(server) -> None:
    response_xml = GET_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl, text=response_xml)
        all_workbooks, pagination_item = server.workbooks.get()

    assert 2 == pagination_item.total_available
    assert "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00" == all_workbooks[0].id
    assert "Superstore" == all_workbooks[0].name
    assert "Superstore" == all_workbooks[0].content_url
    assert not all_workbooks[0].show_tabs
    assert "http://tableauserver/#/workbooks/1/views" == all_workbooks[0].webpage_url
    assert 1 == all_workbooks[0].size
    assert "2016-08-03T20:34:04Z" == format_datetime(all_workbooks[0].created_at)
    assert "description for Superstore" == all_workbooks[0].description
    assert "2016-08-04T17:56:41Z" == format_datetime(all_workbooks[0].updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == all_workbooks[0].project_id
    assert "default" == all_workbooks[0].project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_workbooks[0].owner_id

    assert "3cc6cd06-89ce-4fdc-b935-5294135d6d42" == all_workbooks[1].id
    assert "SafariSample" == all_workbooks[1].name
    assert "SafariSample" == all_workbooks[1].content_url
    assert "http://tableauserver/#/workbooks/2/views" == all_workbooks[1].webpage_url
    assert not all_workbooks[1].show_tabs
    assert 26 == all_workbooks[1].size
    assert "2016-07-26T20:34:56Z" == format_datetime(all_workbooks[1].created_at)
    assert "description for SafariSample" == all_workbooks[1].description
    assert "2016-07-26T20:35:05Z" == format_datetime(all_workbooks[1].updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == all_workbooks[1].project_id
    assert "default" == all_workbooks[1].project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_workbooks[1].owner_id
    assert {"Safari", "Sample"} == all_workbooks[1].tags


def test_get_ignore_invalid_date(server) -> None:
    response_xml = GET_INVALID_DATE_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl, text=response_xml)
        all_workbooks, pagination_item = server.workbooks.get()
    assert format_datetime(all_workbooks[0].created_at) is None
    assert "2016-08-04T17:56:41Z" == format_datetime(all_workbooks[0].updated_at)


def test_get_before_signin(server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.workbooks.get()


def test_get_empty(server) -> None:
    response_xml = GET_EMPTY_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl, text=response_xml)
        all_workbooks, pagination_item = server.workbooks.get()

    assert 0 == pagination_item.total_available
    assert [] == all_workbooks


def test_get_by_id(server) -> None:
    response_xml = GET_BY_ID_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42", text=response_xml)
        single_workbook = server.workbooks.get_by_id("3cc6cd06-89ce-4fdc-b935-5294135d6d42")

    assert "3cc6cd06-89ce-4fdc-b935-5294135d6d42" == single_workbook.id
    assert "SafariSample" == single_workbook.name
    assert "SafariSample" == single_workbook.content_url
    assert "http://tableauserver/#/workbooks/2/views" == single_workbook.webpage_url
    assert not single_workbook.show_tabs
    assert 26 == single_workbook.size
    assert "2016-07-26T20:34:56Z" == format_datetime(single_workbook.created_at)
    assert "description for SafariSample" == single_workbook.description
    assert "2016-07-26T20:35:05Z" == format_datetime(single_workbook.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == single_workbook.project_id
    assert "default" == single_workbook.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == single_workbook.owner_id
    assert {"Safari", "Sample"} == single_workbook.tags
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff5" == single_workbook.views[0].id
    assert "ENDANGERED SAFARI" == single_workbook.views[0].name
    assert "SafariSample/sheets/ENDANGEREDSAFARI" == single_workbook.views[0].content_url


def test_get_by_id_personal(server) -> None:
    # workbooks in personal space don't have project_id or project_name
    response_xml = GET_BY_ID_XML_PERSONAL.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d43", text=response_xml)
        single_workbook = server.workbooks.get_by_id("3cc6cd06-89ce-4fdc-b935-5294135d6d43")

    assert "3cc6cd06-89ce-4fdc-b935-5294135d6d43" == single_workbook.id
    assert "SafariSample" == single_workbook.name
    assert "SafariSample" == single_workbook.content_url
    assert "http://tableauserver/#/workbooks/2/views" == single_workbook.webpage_url
    assert not single_workbook.show_tabs
    assert 26 == single_workbook.size
    assert "2016-07-26T20:34:56Z" == format_datetime(single_workbook.created_at)
    assert "description for SafariSample" == single_workbook.description
    assert "2016-07-26T20:35:05Z" == format_datetime(single_workbook.updated_at)
    assert single_workbook.project_id
    assert single_workbook.project_name is None
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == single_workbook.owner_id
    assert {"Safari", "Sample"} == single_workbook.tags
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff5" == single_workbook.views[0].id
    assert "ENDANGERED SAFARI" == single_workbook.views[0].name
    assert "SafariSample/sheets/ENDANGEREDSAFARI" == single_workbook.views[0].content_url


def test_get_by_id_missing_id(server) -> None:
    with pytest.raises(ValueError):
        server.workbooks.get_by_id("")


def test_refresh_id(server) -> None:
    server.version = "2.8"
    server.workbooks.baseurl
    response_xml = REFRESH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(
            server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/refresh",
            status_code=202,
            text=response_xml,
        )
        server.workbooks.refresh("3cc6cd06-89ce-4fdc-b935-5294135d6d42")


def test_refresh_object(server) -> None:
    server.version = "2.8"
    server.workbooks.baseurl
    workbook = TSC.WorkbookItem("")
    workbook._id = "3cc6cd06-89ce-4fdc-b935-5294135d6d42"
    response_xml = REFRESH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(
            server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/refresh",
            status_code=202,
            text=response_xml,
        )
        server.workbooks.refresh(workbook)


def test_delete(server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42", status_code=204)
        server.workbooks.delete("3cc6cd06-89ce-4fdc-b935-5294135d6d42")


def test_delete_missing_id(server) -> None:
    with pytest.raises(ValueError):
        server.workbooks.delete("")


def test_update(server) -> None:
    response_xml = UPDATE_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74", show_tabs=True)
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook.owner_id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        single_workbook.name = "renamedWorkbook"
        single_workbook.data_acceleration_config = {
            "acceleration_enabled": True,
            "accelerate_now": False,
            "last_updated_at": None,
            "acceleration_status": None,
        }
        single_workbook = server.workbooks.update(single_workbook)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == single_workbook.id
    assert single_workbook.show_tabs
    assert "1d0304cd-3796-429f-b815-7258370b9b74" == single_workbook.project_id
    assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == single_workbook.owner_id
    assert "renamedWorkbook" == single_workbook.name
    assert single_workbook.data_acceleration_config["acceleration_enabled"]
    assert not single_workbook.data_acceleration_config["accelerate_now"]


def test_update_missing_id(server) -> None:
    single_workbook = TSC.WorkbookItem("test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.workbooks.update(single_workbook)


def test_update_copy_fields(server) -> None:
    connection_xml = POPULATE_CONNECTIONS_XML.read_text(encoding="utf-8")
    update_xml = UPDATE_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/connections", text=connection_xml)
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=update_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        server.workbooks.populate_connections(single_workbook)
        updated_workbook = server.workbooks.update(single_workbook)

    assert single_workbook._connections == updated_workbook._connections
    assert single_workbook._views == updated_workbook._views
    assert single_workbook.tags == updated_workbook.tags
    assert single_workbook._initial_tags == updated_workbook._initial_tags
    assert single_workbook._preview_image == updated_workbook._preview_image


def test_update_tags(server) -> None:
    add_tags_xml = ADD_TAGS_XML.read_text(encoding="utf-8")
    update_xml = UPDATE_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/tags", text=add_tags_xml)
        m.delete(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/tags/b", status_code=204)
        m.delete(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/tags/d", status_code=204)
        m.put(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=update_xml)
        single_workbook = TSC.WorkbookItem("1d0304cd-3796-429f-b815-7258370b9b74")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        single_workbook._initial_tags.update(["a", "b", "c", "d"])
        single_workbook.tags.update(["a", "c", "e"])
        updated_workbook = server.workbooks.update(single_workbook)

    assert single_workbook.tags == updated_workbook.tags
    assert single_workbook._initial_tags == updated_workbook._initial_tags


def test_download(server) -> None:
    with requests_mock.mock() as m:
        m.get(
            server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
            headers={"Content-Disposition": 'name="tableau_workbook"; filename="RESTAPISample.twbx"'},
        )
        file_path = server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2")
        assert os.path.exists(file_path)
    os.remove(file_path)


def test_download_object(server) -> None:
    with BytesIO() as file_object:
        with requests_mock.mock() as m:
            m.get(
                server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
                headers={"Content-Disposition": 'name="tableau_workbook"; filename="RESTAPISample.twbx"'},
            )
            file_path = server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2", filepath=file_object)
            assert isinstance(file_path, BytesIO)


def test_download_sanitizes_name(server) -> None:
    filename = "Name,With,Commas.twbx"
    disposition = f'name="tableau_workbook"; filename="{filename}"'
    with requests_mock.mock() as m:
        m.get(
            server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content",
            headers={"Content-Disposition": disposition},
        )
        file_path = server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2")
        assert os.path.basename(file_path) == "NameWithCommas.twbx"
        assert os.path.exists(file_path)
    os.remove(file_path)


def test_download_extract_only(server) -> None:
    # Pretend we're 2.5 for 'extract_only'
    server.version = "2.5"
    server.workbooks.baseurl

    with requests_mock.mock() as m:
        m.get(
            server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/content?includeExtract=False",
            headers={"Content-Disposition": 'name="tableau_workbook"; filename="RESTAPISample.twbx"'},
            complete_qs=True,
        )
        # Technically this shouldn't download a twbx, but we are interested in the qs, not the file
        file_path = server.workbooks.download("1f951daf-4061-451a-9df1-69a8062664f2", include_extract=False)
        assert os.path.exists(file_path)
    os.remove(file_path)


def test_download_missing_id(server) -> None:
    with pytest.raises(ValueError):
        server.workbooks.download("")


def test_populate_views(server) -> None:
    response_xml = POPULATE_VIEWS_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/views", text=response_xml)
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        server.workbooks.populate_views(single_workbook)

        views_list = single_workbook.views
        assert "097dbe13-de89-445f-b2c3-02f28bd010c1" == views_list[0].id
        assert "GDP per capita" == views_list[0].name
        assert "RESTAPISample/sheets/GDPpercapita" == views_list[0].content_url

        assert "2c1ab9d7-8d64-4cc6-b495-52e40c60c330" == views_list[1].id
        assert "Country ranks" == views_list[1].name
        assert "RESTAPISample/sheets/Countryranks" == views_list[1].content_url

        assert "0599c28c-6d82-457e-a453-e52c1bdb00f5" == views_list[2].id
        assert "Interest rates" == views_list[2].name
        assert "RESTAPISample/sheets/Interestrates" == views_list[2].content_url


def test_populate_views_with_usage(server) -> None:
    response_xml = POPULATE_VIEWS_USAGE_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(
            server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/views?includeUsageStatistics=true",
            text=response_xml,
        )
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        server.workbooks.populate_views(single_workbook, usage=True)

        views_list = single_workbook.views
        assert "097dbe13-de89-445f-b2c3-02f28bd010c1" == views_list[0].id
        assert 2 == views_list[0].total_views
        assert "2c1ab9d7-8d64-4cc6-b495-52e40c60c330" == views_list[1].id
        assert 37 == views_list[1].total_views
        assert "0599c28c-6d82-457e-a453-e52c1bdb00f5" == views_list[2].id
        assert 0 == views_list[2].total_views


def test_populate_views_missing_id(server) -> None:
    single_workbook = TSC.WorkbookItem("test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.workbooks.populate_views(single_workbook)


def test_populate_connections(server) -> None:
    response_xml = POPULATE_CONNECTIONS_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/connections", text=response_xml)
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        server.workbooks.populate_connections(single_workbook)

        assert "37ca6ced-58d7-4dcf-99dc-f0a85223cbef" == single_workbook.connections[0].id
        assert "dataengine" == single_workbook.connections[0].connection_type
        assert "4506225a-0d32-4ab1-82d3-c24e85f7afba" == single_workbook.connections[0].datasource_id
        assert "World Indicators" == single_workbook.connections[0].datasource_name


def test_populate_permissions(server) -> None:
    response_xml = POPULATE_PERMISSIONS_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/21778de4-b7b9-44bc-a599-1506a2639ace/permissions", text=response_xml)
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "21778de4-b7b9-44bc-a599-1506a2639ace"

        server.workbooks.populate_permissions(single_workbook)
        permissions = single_workbook.permissions

        assert permissions[0].grantee.tag_name == "group"
        assert permissions[0].grantee.id == "5e5e1978-71fa-11e4-87dd-7382f5c437af"
        assert permissions[0].capabilities == {
            TSC.Permission.Capability.WebAuthoring: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Read: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.Filter: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.AddComment: TSC.Permission.Mode.Allow,
        }

        assert permissions[1].grantee.tag_name == "user"
        assert permissions[1].grantee.id == "7c37ee24-c4b1-42b6-a154-eaeab7ee330a"
        assert permissions[1].capabilities == {
            TSC.Permission.Capability.ExportImage: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ShareView: TSC.Permission.Mode.Allow,
            TSC.Permission.Capability.ExportData: TSC.Permission.Mode.Deny,
            TSC.Permission.Capability.ViewComments: TSC.Permission.Mode.Deny,
        }


def test_add_permissions(server) -> None:
    response_xml = UPDATE_PERMISSIONS.read_text(encoding="utf-8")

    single_workbook = TSC.WorkbookItem("test")
    single_workbook._id = "21778de4-b7b9-44bc-a599-1506a2639ace"

    bob = UserItem.as_reference("7c37ee24-c4b1-42b6-a154-eaeab7ee330a")
    group_of_people = GroupItem.as_reference("5e5e1978-71fa-11e4-87dd-7382f5c437af")

    new_permissions = [PermissionsRule(bob, {"Write": "Allow"}), PermissionsRule(group_of_people, {"Read": "Deny"})]

    with requests_mock.mock() as m:
        m.put(server.workbooks.baseurl + "/21778de4-b7b9-44bc-a599-1506a2639ace/permissions", text=response_xml)
        permissions = server.workbooks.update_permissions(single_workbook, new_permissions)

    assert permissions[0].grantee.tag_name == "group"
    assert permissions[0].grantee.id == "5e5e1978-71fa-11e4-87dd-7382f5c437af"
    assert permissions[0].capabilities == {TSC.Permission.Capability.Read: TSC.Permission.Mode.Deny}
    assert permissions[1].grantee.tag_name == "user"
    assert permissions[1].grantee.id == "7c37ee24-c4b1-42b6-a154-eaeab7ee330a"
    assert permissions[1].capabilities == {TSC.Permission.Capability.Write: TSC.Permission.Mode.Allow}


def test_populate_connections_missing_id(server) -> None:
    single_workbook = TSC.WorkbookItem("test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.workbooks.populate_connections(single_workbook)


def test_populate_pdf(server) -> None:
    server.version = "3.4"
    server.workbooks.baseurl
    response = POPULATE_PDF.read_bytes()
    with requests_mock.mock() as m:
        m.get(
            server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/pdf?type=a5&orientation=landscape",
            content=response,
        )
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"

        type = TSC.PDFRequestOptions.PageType.A5
        orientation = TSC.PDFRequestOptions.Orientation.Landscape
        req_option = TSC.PDFRequestOptions(type, orientation)

        server.workbooks.populate_pdf(single_workbook, req_option)
        assert response == single_workbook.pdf


def test_populate_pdf_unsupported(server) -> None:
    server.version = "3.4"
    server.workbooks.baseurl
    with requests_mock.mock() as m:
        m.get(
            server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/pdf?type=a5&orientation=landscape",
            content=b"",
        )
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"

        type = TSC.PDFRequestOptions.PageType.A5
        orientation = TSC.PDFRequestOptions.Orientation.Landscape
        req_option = TSC.PDFRequestOptions(type, orientation)
        req_option.vf("Region", "West")

        with pytest.raises(UnsupportedAttributeError):
            server.workbooks.populate_pdf(single_workbook, req_option)


def test_populate_pdf_vf_dims(server) -> None:
    server.version = "3.23"
    server.workbooks.baseurl
    response = POPULATE_PDF.read_bytes()
    with requests_mock.mock() as m:
        m.get(
            server.workbooks.baseurl
            + "/1f951daf-4061-451a-9df1-69a8062664f2/pdf?type=a5&orientation=landscape&vf_Region=West&vizWidth=1920&vizHeight=1080",
            content=response,
        )
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"

        type = TSC.PDFRequestOptions.PageType.A5
        orientation = TSC.PDFRequestOptions.Orientation.Landscape
        req_option = TSC.PDFRequestOptions(type, orientation)
        req_option.vf("Region", "West")
        req_option.viz_width = 1920
        req_option.viz_height = 1080

        server.workbooks.populate_pdf(single_workbook, req_option)
        assert response == single_workbook.pdf


def test_populate_powerpoint(server) -> None:
    server.version = "3.8"
    server.workbooks.baseurl
    response = POPULATE_POWERPOINT.read_bytes()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/powerpoint?maxAge=1", content=response)
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"

        ro = TSC.PPTXRequestOptions(maxage=1)

        server.workbooks.populate_powerpoint(single_workbook, ro)
        assert response == single_workbook.powerpoint


def test_populate_preview_image(server) -> None:
    response = POPULATE_PREVIEW_IMAGE.read_bytes()
    with requests_mock.mock() as m:
        m.get(server.workbooks.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2/previewImage", content=response)
        single_workbook = TSC.WorkbookItem("test")
        single_workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        server.workbooks.populate_preview_image(single_workbook)

        assert response == single_workbook.preview_image


def test_populate_preview_image_missing_id(server) -> None:
    single_workbook = TSC.WorkbookItem("test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.workbooks.populate_preview_image(single_workbook)


def test_publish(server) -> None:
    response_xml = PUBLISH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )

        new_workbook.description = "REST API Testing"

        sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
        publish_mode = server.PublishMode.CreateNew

        new_workbook = server.workbooks.publish(new_workbook, sample_workbook, publish_mode)
    assert "a8076ca1-e9d8-495e-bae6-c684dbb55836" == new_workbook.id
    assert "RESTAPISample" == new_workbook.name
    assert "RESTAPISample_0" == new_workbook.content_url
    assert not new_workbook.show_tabs
    assert 1 == new_workbook.size
    assert "2016-08-18T18:33:24Z" == format_datetime(new_workbook.created_at)
    assert "2016-08-18T20:31:34Z" == format_datetime(new_workbook.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_workbook.project_id
    assert "default" == new_workbook.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_workbook.owner_id
    assert "fe0b4e89-73f4-435e-952d-3a263fbfa56c" == new_workbook.views[0].id
    assert "GDP per capita" == new_workbook.views[0].name
    assert "RESTAPISample_0/sheets/GDPpercapita" == new_workbook.views[0].content_url
    assert "REST API Testing" == new_workbook.description


def test_publish_a_packaged_file_object(server) -> None:
    response_xml = PUBLISH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )

        sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")

        with open(sample_workbook, "rb") as fp:
            publish_mode = server.PublishMode.CreateNew

            new_workbook = server.workbooks.publish(new_workbook, fp, publish_mode)

    assert "a8076ca1-e9d8-495e-bae6-c684dbb55836" == new_workbook.id
    assert "RESTAPISample" == new_workbook.name
    assert "RESTAPISample_0" == new_workbook.content_url
    assert not new_workbook.show_tabs
    assert 1 == new_workbook.size
    assert "2016-08-18T18:33:24Z" == format_datetime(new_workbook.created_at)
    assert "2016-08-18T20:31:34Z" == format_datetime(new_workbook.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_workbook.project_id
    assert "default" == new_workbook.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_workbook.owner_id
    assert "fe0b4e89-73f4-435e-952d-3a263fbfa56c" == new_workbook.views[0].id
    assert "GDP per capita" == new_workbook.views[0].name
    assert "RESTAPISample_0/sheets/GDPpercapita" == new_workbook.views[0].content_url


def test_publish_non_packeged_file_object(server) -> None:
    response_xml = PUBLISH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )

        sample_workbook = os.path.join(TEST_ASSET_DIR, "RESTAPISample.twb")

        with open(sample_workbook, "rb") as fp:
            publish_mode = server.PublishMode.CreateNew

            new_workbook = server.workbooks.publish(new_workbook, fp, publish_mode)

    assert "a8076ca1-e9d8-495e-bae6-c684dbb55836" == new_workbook.id
    assert "RESTAPISample" == new_workbook.name
    assert "RESTAPISample_0" == new_workbook.content_url
    assert not new_workbook.show_tabs
    assert 1 == new_workbook.size
    assert "2016-08-18T18:33:24Z" == format_datetime(new_workbook.created_at)
    assert "2016-08-18T20:31:34Z" == format_datetime(new_workbook.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_workbook.project_id
    assert "default" == new_workbook.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_workbook.owner_id
    assert "fe0b4e89-73f4-435e-952d-3a263fbfa56c" == new_workbook.views[0].id
    assert "GDP per capita" == new_workbook.views[0].name
    assert "RESTAPISample_0/sheets/GDPpercapita" == new_workbook.views[0].content_url


def test_publish_path_object(server) -> None:
    response_xml = PUBLISH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )

        sample_workbook = Path(TEST_ASSET_DIR) / "SampleWB.twbx"
        publish_mode = server.PublishMode.CreateNew

        new_workbook = server.workbooks.publish(new_workbook, sample_workbook, publish_mode)

    assert "a8076ca1-e9d8-495e-bae6-c684dbb55836" == new_workbook.id
    assert "RESTAPISample" == new_workbook.name
    assert "RESTAPISample_0" == new_workbook.content_url
    assert not new_workbook.show_tabs
    assert 1 == new_workbook.size
    assert "2016-08-18T18:33:24Z" == format_datetime(new_workbook.created_at)
    assert "2016-08-18T20:31:34Z" == format_datetime(new_workbook.updated_at)
    assert "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760" == new_workbook.project_id
    assert "default" == new_workbook.project_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == new_workbook.owner_id
    assert "fe0b4e89-73f4-435e-952d-3a263fbfa56c" == new_workbook.views[0].id
    assert "GDP per capita" == new_workbook.views[0].name
    assert "RESTAPISample_0/sheets/GDPpercapita" == new_workbook.views[0].content_url


def test_publish_with_hidden_views_on_workbook(server) -> None:
    response_xml = PUBLISH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )

        sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
        publish_mode = server.PublishMode.CreateNew

        new_workbook.hidden_views = ["GDP per capita"]
        new_workbook = server.workbooks.publish(new_workbook, sample_workbook, publish_mode)
        request_body = m._adapter.request_history[0]._request.body
        # order of attributes in xml is unspecified
        assert re.search(b'<views><view.*?hidden=\\"true\\".*?\\/><\\/views>', request_body)
        assert re.search(b'<views><view.*?name=\\"GDP per capita\\".*?\\/><\\/views>', request_body)


def test_publish_with_thumbnails_user_id(server) -> None:
    response_xml = PUBLISH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample",
            show_tabs=False,
            project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760",
            thumbnails_user_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20761",
        )

        sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
        publish_mode = server.PublishMode.CreateNew
        new_workbook = server.workbooks.publish(new_workbook, sample_workbook, publish_mode)
        request_body = m._adapter.request_history[0]._request.body
        # order of attributes in xml is unspecified
        assert re.search(b'thumbnailsUserId=\\"ee8c6e70-43b6-11e6-af4f-f7b0d8e20761\\"', request_body)


def test_publish_with_thumbnails_group_id(server) -> None:
    response_xml = PUBLISH_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample",
            show_tabs=False,
            project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760",
            thumbnails_group_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20762",
        )

        sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
        publish_mode = server.PublishMode.CreateNew
        new_workbook = server.workbooks.publish(new_workbook, sample_workbook, publish_mode)
        request_body = m._adapter.request_history[0]._request.body
        assert re.search(b'thumbnailsGroupId=\\"ee8c6e70-43b6-11e6-af4f-f7b0d8e20762\\"', request_body)


@pytest.mark.filterwarnings("ignore:'as_job' not available")
def test_publish_with_query_params(server) -> None:
    response_xml = PUBLISH_ASYNC_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(server.workbooks.baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )

        sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
        publish_mode = server.PublishMode.CreateNew

        server.workbooks.publish(new_workbook, sample_workbook, publish_mode, as_job=True, skip_connection_check=True)

        request_query_params = m._adapter.request_history[0].qs
        assert "asjob" in request_query_params
        assert request_query_params["asjob"]
        assert "skipconnectioncheck" in request_query_params
        assert request_query_params["skipconnectioncheck"]


def test_publish_async(server) -> None:
    server.version = "3.0"
    baseurl = server.workbooks.baseurl
    response_xml = PUBLISH_ASYNC_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(baseurl, text=response_xml)

        new_workbook = TSC.WorkbookItem(
            name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760"
        )

        sample_workbook = os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")
        publish_mode = server.PublishMode.CreateNew

        new_job = server.workbooks.publish(new_workbook, sample_workbook, publish_mode, as_job=True)

    assert "7c3d599e-949f-44c3-94a1-f30ba85757e4" == new_job.id
    assert "PublishWorkbook" == new_job.type
    assert "0" == new_job.progress
    assert "2018-06-29T23:22:32Z" == format_datetime(new_job.created_at)
    assert 1 == new_job.finish_code


def test_publish_invalid_file(server) -> None:
    new_workbook = TSC.WorkbookItem("test", "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    with pytest.raises(IOError):
        server.workbooks.publish(new_workbook, ".", server.PublishMode.CreateNew)


def test_publish_invalid_file_type(server) -> None:
    new_workbook = TSC.WorkbookItem("test", "ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    with pytest.raises(ValueError):
        server.workbooks.publish(
            new_workbook, os.path.join(TEST_ASSET_DIR, "SampleDS.tds"), server.PublishMode.CreateNew
        )


def test_publish_unnamed_file_object(server) -> None:
    new_workbook = TSC.WorkbookItem("test")

    with open(os.path.join(TEST_ASSET_DIR, "SampleWB.twbx"), "rb") as f:
        with pytest.raises(ValueError):
            server.workbooks.publish(new_workbook, f, server.PublishMode.CreateNew)


def test_publish_non_bytes_file_object(server) -> None:
    new_workbook = TSC.WorkbookItem("test")

    with open(os.path.join(TEST_ASSET_DIR, "SampleWB.twbx")) as f:
        with pytest.raises(TypeError):
            server.workbooks.publish(new_workbook, f, server.PublishMode.CreateNew)


def test_publish_file_object_of_unknown_type_raises_exception(server) -> None:
    new_workbook = TSC.WorkbookItem("test")
    with BytesIO() as file_object:
        file_object.write(bytes.fromhex("89504E470D0A1A0A"))
        file_object.seek(0)
        with pytest.raises(ValueError):
            server.workbooks.publish(new_workbook, file_object, server.PublishMode.CreateNew)


def test_publish_multi_connection(server) -> None:
    new_workbook = TSC.WorkbookItem(name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    connection1 = TSC.ConnectionItem()
    connection1.server_address = "mysql.test.com"
    connection1.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)
    connection2 = TSC.ConnectionItem()
    connection2.server_address = "pgsql.test.com"
    connection2.connection_credentials = TSC.ConnectionCredentials("test", "secret", True)

    response = RequestFactory.Workbook._generate_xml(new_workbook, connections=[connection1, connection2])
    # Can't use ConnectionItem parser due to xml namespace problems
    connection_results = fromstring(response).findall(".//connection")

    assert connection_results[0].get("serverAddress", None) == "mysql.test.com"
    assert connection_results[0].find("connectionCredentials").get("name", None) == "test"
    assert connection_results[1].get("serverAddress", None) == "pgsql.test.com"
    assert connection_results[1].find("connectionCredentials").get("password", None) == "secret"


def test_publish_multi_connection_flat(server) -> None:
    new_workbook = TSC.WorkbookItem(name="Sample", show_tabs=False, project_id="ee8c6e70-43b6-11e6-af4f-f7b0d8e20760")
    connection1 = TSC.ConnectionItem()
    connection1.server_address = "mysql.test.com"
    connection1.username = "test"
    connection1.password = "secret"
    connection1.embed_password = True
    connection2 = TSC.ConnectionItem()
    connection2.server_address = "pgsql.test.com"
    connection2.username = "test"
    connection2.password = "secret"
    connection2.embed_password = True

    response = RequestFactory.Workbook._generate_xml(new_workbook, connections=[connection1, connection2])
    # Can't use ConnectionItem parser due to xml namespace problems
    connection_results = fromstring(response).findall(".//connection")

    assert connection_results[0].get("serverAddress", None) == "mysql.test.com"
    assert connection_results[0].find("connectionCredentials").get("name", None) == "test"
    assert connection_results[1].get("serverAddress", None) == "pgsql.test.com"
    assert connection_results[1].find("connectionCredentials").get("password", None) == "secret"


def test_synchronous_publish_timeout_error(server) -> None:
    with requests_mock.mock() as m:
        m.register_uri("POST", server.workbooks.baseurl, status_code=504)

        new_workbook = TSC.WorkbookItem(project_id="")
        publish_mode = server.PublishMode.CreateNew

        with pytest.raises(InternalServerError, match="Please use asynchronous publishing to avoid timeouts"):
            server.workbooks.publish(new_workbook, asset("SampleWB.twbx"), publish_mode)


def test_delete_extracts_all(server) -> None:
    server.version = "3.10"
    server.workbooks.baseurl

    response_xml = PUBLISH_ASYNC_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(
            server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/deleteExtract",
            status_code=200,
            text=response_xml,
        )
        server.workbooks.delete_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")


def test_create_extracts_all(server) -> None:
    server.version = "3.10"
    server.workbooks.baseurl

    response_xml = PUBLISH_ASYNC_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(
            server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract",
            status_code=200,
            text=response_xml,
        )
        server.workbooks.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42")


def test_create_extracts_one(server) -> None:
    server.version = "3.10"
    server.workbooks.baseurl

    datasource = TSC.DatasourceItem("test")
    datasource._id = "1f951daf-4061-451a-9df1-69a8062664f2"

    response_xml = PUBLISH_ASYNC_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.post(
            server.workbooks.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42/createExtract",
            status_code=200,
            text=response_xml,
        )
        server.workbooks.create_extract("3cc6cd06-89ce-4fdc-b935-5294135d6d42", False, datasource)


def test_revisions(server) -> None:
    server.workbooks.baseurl
    workbook = TSC.WorkbookItem("project", "test")
    workbook._id = "06b944d2-959d-4604-9305-12323c95e70e"

    response_xml = REVISION_XML.read_text(encoding="utf-8")
    with requests_mock.mock() as m:
        m.get(f"{server.workbooks.baseurl}/{workbook.id}/revisions", text=response_xml)
        server.workbooks.populate_revisions(workbook)
        revisions = workbook.revisions

    assert len(revisions) == 3
    assert "2016-07-26T20:34:56Z" == format_datetime(revisions[0].created_at)
    assert "2016-07-27T20:34:56Z" == format_datetime(revisions[1].created_at)
    assert "2016-07-28T20:34:56Z" == format_datetime(revisions[2].created_at)

    assert not revisions[0].deleted
    assert not revisions[0].current
    assert not revisions[1].deleted
    assert not revisions[1].current
    assert not revisions[2].deleted
    assert revisions[2].current

    assert "Cassie" == revisions[0].user_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == revisions[0].user_id
    assert revisions[1].user_name is None
    assert revisions[1].user_id is None
    assert "Cassie" == revisions[2].user_name
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == revisions[2].user_id


def test_delete_revision(server) -> None:
    server.workbooks.baseurl
    workbook = TSC.WorkbookItem("project", "test")
    workbook._id = "06b944d2-959d-4604-9305-12323c95e70e"

    with requests_mock.mock() as m:
        m.delete(f"{server.workbooks.baseurl}/{workbook.id}/revisions/3")
        server.workbooks.delete_revision(workbook.id, "3")


def test_download_revision(server) -> None:
    with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
        m.get(
            server.workbooks.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/revisions/3/content",
            headers={"Content-Disposition": 'name="tableau_datasource"; filename="Sample datasource.tds"'},
        )
        file_path = server.workbooks.download_revision("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", "3", td)
        assert os.path.exists(file_path)


def test_bad_download_response(server) -> None:
    with requests_mock.mock() as m, tempfile.TemporaryDirectory() as td:
        m.get(
            server.workbooks.baseurl + "/9dbd2263-16b5-46e1-9c43-a76bb8ab65fb/content",
            headers={"Content-Disposition": '''name="tableau_workbook"; filename*=UTF-8''"Sample workbook.twb"'''},
        )
        file_path = server.workbooks.download("9dbd2263-16b5-46e1-9c43-a76bb8ab65fb", td)
        assert os.path.exists(file_path)


def test_odata_connection(server) -> None:
    server.workbooks.baseurl
    workbook = TSC.WorkbookItem("project", "test")
    workbook._id = "06b944d2-959d-4604-9305-12323c95e70e"
    connection = TSC.ConnectionItem()
    url = "https://odata.website.com/TestODataEndpoint"
    connection.server_address = url
    connection._connection_type = "odata"
    connection._id = "17376070-64d1-4d17-acb4-a56e4b5b1768"

    creds = TSC.ConnectionCredentials("", "", True)
    connection.connection_credentials = creds
    response_xml = ODATA_XML.read_text(encoding="utf-8")

    with requests_mock.mock() as m:
        m.put(f"{server.workbooks.baseurl}/{workbook.id}/connections/{connection.id}", text=response_xml)
        server.workbooks.update_connection(workbook, connection)

        history = m.request_history

    request = history[0]
    xml = fromstring(request.body)
    xml_connection = xml.find(".//connection")

    assert xml_connection is not None
    assert xml_connection.get("serverAddress") == url


def test_update_workbook_connections(server) -> None:
    populate_xml, response_xml = read_xml_assets(POPULATE_CONNECTIONS_XML, UPDATE_CONNECTIONS_XML)

    with requests_mock.Mocker() as m:
        workbook_id = "1a2b3c4d-5e6f-7a8b-9c0d-112233445566"
        connection_luids = ["abc12345-def6-7890-gh12-ijklmnopqrst", "1234abcd-5678-efgh-ijkl-0987654321mn"]

        workbook = TSC.WorkbookItem(workbook_id)
        workbook._id = workbook_id
        server.version = "3.26"
        url = f"{server.baseurl}/{workbook_id}/connections"
        m.get(
            "http://test/api/3.26/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks/1a2b3c4d-5e6f-7a8b-9c0d-112233445566/connections",
            text=populate_xml,
        )
        m.put(
            "http://test/api/3.26/sites/dad65087-b08b-4603-af4e-2887b8aafc67/workbooks/1a2b3c4d-5e6f-7a8b-9c0d-112233445566/connections",
            text=response_xml,
        )

        connection_items = server.workbooks.update_connections(
            workbook_item=workbook,
            connection_luids=connection_luids,
            authentication_type="AD Service Principal",
            username="svc-client",
            password="secret-token",
            embed_password=True,
        )
        updated_ids = [conn.id for conn in connection_items]

        assert updated_ids == connection_luids
        assert "AD Service Principal" == connection_items[0].auth_type


def test_get_workbook_all_fields(server) -> None:
    server.version = "3.21"
    baseurl = server.workbooks.baseurl

    response = GET_XML_ALL_FIELDS.read_text(encoding="utf-8")

    ro = TSC.RequestOptions()
    ro.all_fields = True

    with requests_mock.mock() as m:
        m.get(f"{baseurl}?fields=_all_", text=response)
        workbooks, _ = server.workbooks.get(req_options=ro)

    assert workbooks[0].id == "9df3e2d1-070e-497a-9578-8cc557ced9df"
    assert workbooks[0].name == "Superstore"
    assert workbooks[0].content_url == "Superstore"
    assert workbooks[0].webpage_url == "https://10ax.online.tableau.com/#/site/exampledev/workbooks/265605"
    assert workbooks[0].show_tabs
    assert workbooks[0].size == 2
    assert workbooks[0].created_at == parse_datetime("2024-02-14T04:42:09Z")
    assert workbooks[0].updated_at == parse_datetime("2024-02-14T04:42:10Z")
    assert workbooks[0].sheet_count == 9
    assert not workbooks[0].has_extracts
    assert not workbooks[0].encrypt_extracts
    assert workbooks[0].default_view_id == "2bdcd787-dcc6-4a5d-bc61-2846f1ef4534"
    assert workbooks[0].share_description == "Superstore"
    assert workbooks[0].last_published_at == parse_datetime("2024-02-14T04:42:09Z")
    assert isinstance(workbooks[0].project, TSC.ProjectItem)
    assert workbooks[0].project.id == "669ca36b-492e-4ccf-bca1-3614fe6a9d7a"
    assert workbooks[0].project.name == "Samples"
    assert workbooks[0].project.description == "This project includes automatically uploaded samples."
    assert isinstance(workbooks[0].location, TSC.LocationItem)
    assert workbooks[0].location.id == "669ca36b-492e-4ccf-bca1-3614fe6a9d7a"
    assert workbooks[0].location.type == "Project"
    assert workbooks[0].location.name == "Samples"
    assert isinstance(workbooks[0].owner, TSC.UserItem)
    assert workbooks[0].owner.email == "bob@example.com"
    assert workbooks[0].owner.fullname == "Bob Smith"
    assert workbooks[0].owner.id == "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
    assert workbooks[0].owner.last_login == parse_datetime("2025-02-04T06:39:20Z")
    assert workbooks[0].owner.name == "bob@example.com"
    assert workbooks[0].owner.site_role == "SiteAdministratorCreator"
    assert workbooks[1].id == "6693cb26-9507-4174-ad3e-9de81a18c971"
    assert workbooks[1].name == "World Indicators"
    assert workbooks[1].content_url == "WorldIndicators"
    assert workbooks[1].webpage_url == "https://10ax.online.tableau.com/#/site/exampledev/workbooks/265606"
    assert workbooks[1].show_tabs
    assert workbooks[1].size == 1
    assert workbooks[1].created_at == parse_datetime("2024-02-14T04:42:11Z")
    assert workbooks[1].updated_at == parse_datetime("2024-02-14T04:42:12Z")
    assert workbooks[1].sheet_count == 8
    assert not workbooks[1].has_extracts
    assert not workbooks[1].encrypt_extracts
    assert workbooks[1].default_view_id == "3d10dbcf-a206-47c7-91ba-ebab3ab33d7c"
    assert workbooks[1].share_description == "World Indicators"
    assert workbooks[1].last_published_at == parse_datetime("2024-02-14T04:42:11Z")
    assert isinstance(workbooks[1].project, TSC.ProjectItem)
    assert workbooks[1].project.id == "669ca36b-492e-4ccf-bca1-3614fe6a9d7a"
    assert workbooks[1].project.name == "Samples"
    assert workbooks[1].project.description == "This project includes automatically uploaded samples."
    assert isinstance(workbooks[1].location, TSC.LocationItem)
    assert workbooks[1].location.id == "669ca36b-492e-4ccf-bca1-3614fe6a9d7a"
    assert workbooks[1].location.type == "Project"
    assert workbooks[1].location.name == "Samples"
    assert isinstance(workbooks[1].owner, TSC.UserItem)
    assert workbooks[1].owner.email == "bob@example.com"
    assert workbooks[1].owner.fullname == "Bob Smith"
    assert workbooks[1].owner.id == "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
    assert workbooks[1].owner.last_login == parse_datetime("2025-02-04T06:39:20Z")
    assert workbooks[1].owner.name == "bob@example.com"
    assert workbooks[1].owner.site_role == "SiteAdministratorCreator"
    assert workbooks[2].id == "dbc0f162-909f-4edf-8392-0d12a80af955"
    assert workbooks[2].name == "Superstore"
    assert workbooks[2].description == "This is a superstore workbook"
    assert workbooks[2].content_url == "Superstore_17078880698360"
    assert workbooks[2].webpage_url == "https://10ax.online.tableau.com/#/site/exampledev/workbooks/265621"
    assert not workbooks[2].show_tabs
    assert workbooks[2].size == 1
    assert workbooks[2].created_at == parse_datetime("2024-02-14T05:21:09Z")
    assert workbooks[2].updated_at == parse_datetime("2024-07-02T02:19:59Z")
    assert workbooks[2].sheet_count == 7
    assert workbooks[2].has_extracts
    assert not workbooks[2].encrypt_extracts
    assert workbooks[2].default_view_id == "8c4b1d3e-3f31-4d2a-8b9f-492b92f27987"
    assert workbooks[2].share_description == "Superstore"
    assert workbooks[2].last_published_at == parse_datetime("2024-07-02T02:19:58Z")
    assert isinstance(workbooks[2].project, TSC.ProjectItem)
    assert workbooks[2].project.id == "9836791c-9468-40f0-b7f3-d10b9562a046"
    assert workbooks[2].project.name == "default"
    assert workbooks[2].project.description == "The default project that was automatically created by Tableau."
    assert isinstance(workbooks[2].location, TSC.LocationItem)
    assert workbooks[2].location.id == "9836791c-9468-40f0-b7f3-d10b9562a046"
    assert workbooks[2].location.type == "Project"
    assert workbooks[2].location.name == "default"
    assert isinstance(workbooks[2].owner, TSC.UserItem)
    assert workbooks[2].owner.email == "bob@example.com"
    assert workbooks[2].owner.fullname == "Bob Smith"
    assert workbooks[2].owner.id == "ee8bc9ca-77fe-4ae0-8093-cf77f0ee67a9"
    assert workbooks[2].owner.last_login == parse_datetime("2025-02-04T06:39:20Z")
    assert workbooks[2].owner.name == "bob@example.com"
    assert workbooks[2].owner.site_role == "SiteAdministratorCreator"
