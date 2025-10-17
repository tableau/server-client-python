from contextlib import ExitStack
import io
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.config import BYTES_PER_MB
from tableauserverclient.datetime_helpers import format_datetime

TEST_ASSET_DIR = Path(__file__).parent / "assets"

GET_XML = TEST_ASSET_DIR / "custom_view_get.xml"
GET_XML_ID = TEST_ASSET_DIR / "custom_view_get_id.xml"
POPULATE_PREVIEW_IMAGE = TEST_ASSET_DIR / "Sample View Image.png"
CUSTOM_VIEW_UPDATE_XML = TEST_ASSET_DIR / "custom_view_update.xml"
CUSTOM_VIEW_POPULATE_PDF = TEST_ASSET_DIR / "populate_pdf.pdf"
CUSTOM_VIEW_POPULATE_CSV = TEST_ASSET_DIR / "populate_csv.csv"
CUSTOM_VIEW_DOWNLOAD = TEST_ASSET_DIR / "custom_view_download.json"
FILE_UPLOAD_INIT = TEST_ASSET_DIR / "fileupload_initialize.xml"
FILE_UPLOAD_APPEND = TEST_ASSET_DIR / "fileupload_append.xml"


@pytest.fixture(scope="function")
def server() -> TSC.Server:
    server = TSC.Server("http://test", False)
    server.version = "3.21"  # custom views only introduced in 3.19

    # Fake sign in
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"

    return server


def test_get(server: TSC.Server) -> None:
    response_xml = GET_XML.read_text()
    print(response_xml)
    with requests_mock.mock() as m:
        m.get(server.custom_views.baseurl, text=response_xml)
        all_views, pagination_item = server.custom_views.get()

    assert 2 == pagination_item.total_available
    assert "d79634e1-6063-4ec9-95ff-50acbf609ff5" == all_views[0].id
    assert "ENDANGERED SAFARI" == all_views[0].name
    assert "SafariSample/sheets/ENDANGEREDSAFARI" == all_views[0].content_url
    assert "3cc6cd06-89ce-4fdc-b935-5294135d6d42" == all_views[0].workbook.id
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_views[0].owner.id
    assert all_views[0].created_at is None
    assert all_views[0].updated_at is None
    assert not all_views[0].shared

    assert "fd252f73-593c-4c4e-8584-c032b8022adc" == all_views[1].id
    assert "Overview" == all_views[1].name
    assert "6d13b0ca-043d-4d42-8c9d-3f3313ea3a00" == all_views[1].workbook.id
    assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == all_views[1].owner.id
    assert "2002-05-30T09:00:00Z" == format_datetime(all_views[1].created_at)
    assert "2002-06-05T08:00:59Z" == format_datetime(all_views[1].updated_at)
    assert all_views[1].shared


def test_get_by_id(server: TSC.Server) -> None:
    response_xml = GET_XML_ID.read_text()
    with requests_mock.mock() as m:
        m.get(server.custom_views.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5", text=response_xml)
        view: TSC.CustomViewItem = server.custom_views.get_by_id("d79634e1-6063-4ec9-95ff-50acbf609ff5")

    assert "d79634e1-6063-4ec9-95ff-50acbf609ff5" == view.id
    assert "ENDANGERED SAFARI" == view.name
    assert "SafariSample/sheets/ENDANGEREDSAFARI" == view.content_url
    if view.workbook:
        assert "3cc6cd06-89ce-4fdc-b935-5294135d6d42" == view.workbook.id
    if view.owner:
        assert "5de011f8-5aa9-4d5b-b991-f462c8dd6bb7" == view.owner.id
    if view.view:
        assert "5241e88d-d384-4fd7-9c2f-648b5247efc5" == view.view.id
    assert "2002-05-30T09:00:00Z" == format_datetime(view.created_at)
    assert "2002-06-05T08:00:59Z" == format_datetime(view.updated_at)


def test_get_by_id_missing_id(server: TSC.Server) -> None:
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.custom_views.get_by_id(None)


def test_get_before_signin(server: TSC.Server) -> None:
    server._auth_token = None
    with pytest.raises(TSC.NotSignedInError):
        server.custom_views.get()


def test_populate_image(server: TSC.Server) -> None:
    response = POPULATE_PREVIEW_IMAGE.read_bytes()
    with requests_mock.mock() as m:
        m.get(server.custom_views.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/image", content=response)
        single_view = TSC.CustomViewItem()
        single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
        server.custom_views.populate_image(single_view)
        assert response == single_view.image


def test_populate_image_with_options(server: TSC.Server) -> None:
    response = POPULATE_PREVIEW_IMAGE.read_bytes()
    with requests_mock.mock() as m:
        m.get(
            server.custom_views.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/image?resolution=high&maxAge=10",
            content=response,
        )
        single_view = TSC.CustomViewItem()
        single_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
        req_option = TSC.ImageRequestOptions(imageresolution=TSC.ImageRequestOptions.Resolution.High, maxage=10)
        server.custom_views.populate_image(single_view, req_option)
        assert response == single_view.image


def test_populate_image_missing_id(server: TSC.Server) -> None:
    single_view = TSC.CustomViewItem()
    single_view._id = None
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.custom_views.populate_image(single_view)


def test_delete(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.custom_views.baseurl + "/3cc6cd06-89ce-4fdc-b935-5294135d6d42", status_code=204)
        server.custom_views.delete("3cc6cd06-89ce-4fdc-b935-5294135d6d42")


def test_delete_missing_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.custom_views.delete("")


def test_update(server: TSC.Server) -> None:
    response_xml = CUSTOM_VIEW_UPDATE_XML.read_text()
    with requests_mock.mock() as m:
        m.put(server.custom_views.baseurl + "/1f951daf-4061-451a-9df1-69a8062664f2", text=response_xml)
        the_custom_view = TSC.CustomViewItem("1d0304cd-3796-429f-b815-7258370b9b74", name="Best test ever")
        the_custom_view._id = "1f951daf-4061-451a-9df1-69a8062664f2"
        the_custom_view.owner = TSC.UserItem()
        the_custom_view.owner.id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
        the_custom_view = server.custom_views.update(the_custom_view)

    assert "1f951daf-4061-451a-9df1-69a8062664f2" == the_custom_view.id
    if the_custom_view.owner:
        assert "dd2239f6-ddf1-4107-981a-4cf94e415794" == the_custom_view.owner.id
    assert "Best test ever" == the_custom_view.name


def test_update_missing_id(server: TSC.Server) -> None:
    cv = TSC.CustomViewItem(name="test")
    with pytest.raises(TSC.MissingRequiredFieldError):
        server.custom_views.update(cv)


def test_download(server: TSC.Server) -> None:
    cv = TSC.CustomViewItem(name="test")
    cv._id = "1f951daf-4061-451a-9df1-69a8062664f2"
    content = CUSTOM_VIEW_DOWNLOAD.read_bytes()
    data = io.BytesIO()
    with requests_mock.mock() as m:
        m.get(f"{server.custom_views.expurl}/1f951daf-4061-451a-9df1-69a8062664f2/content", content=content)
        server.custom_views.download(cv, data)

    assert data.getvalue() == content


def test_publish_filepath(server: TSC.Server) -> None:
    cv = TSC.CustomViewItem(name="test")
    cv._owner = TSC.UserItem()
    cv._owner._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
    cv._workbook = TSC.WorkbookItem()
    cv._workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
    with requests_mock.mock() as m:
        m.post(server.custom_views.expurl, status_code=201, text=GET_XML.read_text())
        view = server.custom_views.publish(cv, CUSTOM_VIEW_DOWNLOAD)

    assert view is not None
    assert isinstance(view, TSC.CustomViewItem)
    assert view.id is not None
    assert view.name is not None


def test_publish_file_str(server: TSC.Server) -> None:
    cv = TSC.CustomViewItem(name="test")
    cv._owner = TSC.UserItem()
    cv._owner._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
    cv._workbook = TSC.WorkbookItem()
    cv._workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
    with requests_mock.mock() as m:
        m.post(server.custom_views.expurl, status_code=201, text=GET_XML.read_text())
        view = server.custom_views.publish(cv, str(CUSTOM_VIEW_DOWNLOAD))

    assert view is not None
    assert isinstance(view, TSC.CustomViewItem)
    assert view.id is not None
    assert view.name is not None


def test_publish_file_io(server: TSC.Server) -> None:
    cv = TSC.CustomViewItem(name="test")
    cv._owner = TSC.UserItem()
    cv._owner._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
    cv._workbook = TSC.WorkbookItem()
    cv._workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
    data = io.BytesIO(CUSTOM_VIEW_DOWNLOAD.read_bytes())
    with requests_mock.mock() as m:
        m.post(server.custom_views.expurl, status_code=201, text=GET_XML.read_text())
        view = server.custom_views.publish(cv, data)

    assert view is not None
    assert isinstance(view, TSC.CustomViewItem)
    assert view.id is not None
    assert view.name is not None


def test_publish_missing_owner_id(server: TSC.Server) -> None:
    cv = TSC.CustomViewItem(name="test")
    cv._owner = TSC.UserItem()
    cv._workbook = TSC.WorkbookItem()
    cv._workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
    with requests_mock.mock() as m:
        m.post(server.custom_views.expurl, status_code=201, text=GET_XML.read_text())
        with pytest.raises(ValueError):
            server.custom_views.publish(cv, CUSTOM_VIEW_DOWNLOAD)


def test_publish_missing_wb_id(server: TSC.Server) -> None:
    cv = TSC.CustomViewItem(name="test")
    cv._owner = TSC.UserItem()
    cv._owner._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
    cv._workbook = TSC.WorkbookItem()
    with requests_mock.mock() as m:
        m.post(server.custom_views.expurl, status_code=201, text=GET_XML.read_text())
        with pytest.raises(ValueError):
            server.custom_views.publish(cv, CUSTOM_VIEW_DOWNLOAD)


def test_large_publish(server: TSC.Server):
    cv = TSC.CustomViewItem(name="test")
    cv._owner = TSC.UserItem()
    cv._owner._id = "dd2239f6-ddf1-4107-981a-4cf94e415794"
    cv._workbook = TSC.WorkbookItem()
    cv._workbook._id = "1f951daf-4061-451a-9df1-69a8062664f2"
    with ExitStack() as stack:
        temp_dir = stack.enter_context(TemporaryDirectory())
        file_path = Path(temp_dir) / "test_file"
        file_path.write_bytes(os.urandom(65 * BYTES_PER_MB))
        mock = stack.enter_context(requests_mock.mock())
        # Mock initializing upload
        mock.post(server.fileuploads.baseurl, status_code=201, text=FILE_UPLOAD_INIT.read_text())
        # Mock the upload
        mock.put(
            f"{server.fileuploads.baseurl}/7720:170fe6b1c1c7422dadff20f944d58a52-1:0",
            text=FILE_UPLOAD_APPEND.read_text(),
        )
        # Mock the publish
        mock.post(server.custom_views.expurl, status_code=201, text=GET_XML.read_text())

        view = server.custom_views.publish(cv, file_path)

    assert view is not None
    assert isinstance(view, TSC.CustomViewItem)
    assert view.id is not None
    assert view.name is not None


def test_populate_pdf(server: TSC.Server) -> None:
    server.version = "3.23"
    response = CUSTOM_VIEW_POPULATE_PDF.read_bytes()
    with requests_mock.mock() as m:
        m.get(
            server.custom_views.baseurl
            + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/pdf?type=letter&orientation=portrait&maxAge=5",
            content=response,
        )
        custom_view = TSC.CustomViewItem()
        custom_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"

        size = TSC.PDFRequestOptions.PageType.Letter
        orientation = TSC.PDFRequestOptions.Orientation.Portrait
        req_option = TSC.PDFRequestOptions(size, orientation, 5)

        server.custom_views.populate_pdf(custom_view, req_option)
        assert response == custom_view.pdf


def test_populate_csv(server: TSC.Server) -> None:
    server.version = "3.23"
    response = CUSTOM_VIEW_POPULATE_CSV.read_bytes()
    with requests_mock.mock() as m:
        m.get(server.custom_views.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/data?maxAge=1", content=response)
        custom_view = TSC.CustomViewItem()
        custom_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
        request_option = TSC.CSVRequestOptions(maxage=1)
        server.custom_views.populate_csv(custom_view, request_option)

        csv_file = b"".join(custom_view.csv)
        assert response == csv_file


def test_populate_csv_default_maxage(server: TSC.Server) -> None:
    server.version = "3.23"
    response = CUSTOM_VIEW_POPULATE_CSV.read_bytes()
    with requests_mock.mock() as m:
        m.get(server.custom_views.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/data", content=response)
        custom_view = TSC.CustomViewItem()
        custom_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"
        server.custom_views.populate_csv(custom_view)

        csv_file = b"".join(custom_view.csv)
        assert response == csv_file


def test_pdf_height(server: TSC.Server) -> None:
    server.version = "3.23"
    response = CUSTOM_VIEW_POPULATE_PDF.read_bytes()
    with requests_mock.mock() as m:
        m.get(
            server.custom_views.baseurl + "/d79634e1-6063-4ec9-95ff-50acbf609ff5/pdf?vizHeight=1080&vizWidth=1920",
            content=response,
        )
        custom_view = TSC.CustomViewItem()
        custom_view._id = "d79634e1-6063-4ec9-95ff-50acbf609ff5"

        req_option = TSC.PDFRequestOptions(
            viz_height=1080,
            viz_width=1920,
        )

        server.custom_views.populate_pdf(custom_view, req_option)
        assert response == custom_view.pdf
