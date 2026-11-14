import datetime
from pathlib import Path

import pytest
import requests_mock

import tableauserverclient as TSC
from tableauserverclient.server.exceptions import EndpointUnavailableError

TEST_ASSET_DIR = Path(__file__).parent / "assets"
RECYCLE_BIN_GET = TEST_ASSET_DIR / "recycle_bin_get.xml"
RECYCLE_BIN_GET_BY_ID = TEST_ASSET_DIR / "recycle_bin_get_by_id.xml"
RECYCLE_BIN_EMPTY_JOB = TEST_ASSET_DIR / "recycle_bin_empty_job.xml"

ITEM_ID = "a1b2c3d4-0000-4000-8000-000000000001"
PROJECT_ID = "44444444-4444-4444-8444-444444444444"


@pytest.fixture(scope="function")
def server():
    server = TSC.Server("http://test", False)

    # Fake signin
    server._site_id = "dad65087-b08b-4603-af4e-2887b8aafc67"
    server._auth_token = "j80k54ll2lfMZ0tv97mlPvvSCRyD0DOM"
    server.version = "3.29"

    return server


def test_baseurl(server: TSC.Server) -> None:
    assert server.recycle_bin.baseurl == f"{server.baseurl}/sites/{server.site_id}/recyclebin"


def test_requires_api_3_29(server: TSC.Server) -> None:
    server.version = "3.28"
    with pytest.raises(EndpointUnavailableError):
        server.recycle_bin.get("workbooks")


def test_get(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(f"{server.recycle_bin.baseurl}/workbooks", text=RECYCLE_BIN_GET.read_text())
        items, pagination = server.recycle_bin.get("workbooks")

    assert pagination.total_available == 2
    assert len(items) == 2
    first = items[0]
    assert first.id == ITEM_ID
    assert first.name == "Sales Dashboard"
    assert first.content_type == "workbook"
    assert first.original_path == "Finance/Reports"
    assert first.is_read_only is False
    assert first.owner_id == "11111111-1111-4111-8111-111111111111"
    assert first.deleter_id == "22222222-2222-4222-8222-222222222222"
    assert first.created_at == datetime.datetime(2026, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)
    assert first.updated_at == datetime.datetime(2026, 2, 3, 4, 5, 6, tzinfo=datetime.timezone.utc)
    assert items[1].is_read_only is True


def test_get_with_request_options(server: TSC.Server) -> None:
    options = TSC.RequestOptions(pagesize=5)
    options.filter.add(TSC.Filter(TSC.RequestOptions.Field.DeleterId, TSC.RequestOptions.Operator.Equals, "22222222"))
    with requests_mock.mock() as m:
        m.get(f"{server.recycle_bin.baseurl}/flows", text=RECYCLE_BIN_GET.read_text())
        server.recycle_bin.get("flows", options)

    assert m.last_request.qs["pagesize"] == ["5"]
    assert m.last_request.qs["filter"] == ["deleterid:eq:22222222"]


@pytest.mark.parametrize("content_type", ["datasources", "datasource", "projects", "flows", "workbook"])
def test_get_accepts_plural_and_singular_content_types(server: TSC.Server, content_type: str) -> None:
    expected = content_type if content_type.endswith("s") else f"{content_type}s"
    with requests_mock.mock() as m:
        m.get(f"{server.recycle_bin.baseurl}/{expected}", text=RECYCLE_BIN_GET.read_text())
        items, _ = server.recycle_bin.get(content_type)  # type: ignore[arg-type]
    assert len(items) == 2


def test_get_rejects_unknown_content_type(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.recycle_bin.get("views")  # type: ignore[arg-type]


def test_get_by_id(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.get(f"{server.recycle_bin.baseurl}/workbooks/{ITEM_ID}", text=RECYCLE_BIN_GET_BY_ID.read_text())
        item = server.recycle_bin.get_by_id("workbooks", ITEM_ID)

    assert item.id == ITEM_ID
    assert item.name == "Sales Dashboard"


def test_get_by_id_requires_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.recycle_bin.get_by_id("workbooks", "")


def test_restore_by_id(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.post(f"{server.recycle_bin.baseurl}/workbooks/{ITEM_ID}/restore", status_code=204)
        server.recycle_bin.restore(ITEM_ID, PROJECT_ID, content_type="workbooks")

    assert m.last_request.qs["projectid"] == [PROJECT_ID]


def test_restore_item_uses_its_content_type_and_project_item(server: TSC.Server) -> None:
    item = TSC.RecycleBinItem(id_=ITEM_ID, content_type="datasource")
    project = TSC.ProjectItem("Restored")
    project._id = PROJECT_ID
    with requests_mock.mock() as m:
        m.post(f"{server.recycle_bin.baseurl}/datasources/{ITEM_ID}/restore", status_code=204)
        server.recycle_bin.restore(item, project)

    assert m.last_request.qs["projectid"] == [PROJECT_ID]


def test_restore_requires_content_type_for_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.recycle_bin.restore(ITEM_ID, PROJECT_ID)


def test_restore_requires_project(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.recycle_bin.restore(ITEM_ID, TSC.ProjectItem("No id"), content_type="workbooks")


def test_delete_by_id(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(f"{server.recycle_bin.baseurl}/workbooks/{ITEM_ID}", status_code=204)
        server.recycle_bin.delete(ITEM_ID, content_type="workbooks")

    assert m.called


def test_delete_item(server: TSC.Server) -> None:
    item = TSC.RecycleBinItem(id_=ITEM_ID, content_type="flow")
    with requests_mock.mock() as m:
        m.delete(f"{server.recycle_bin.baseurl}/flows/{ITEM_ID}", status_code=204)
        server.recycle_bin.delete(item)

    assert m.called


def test_delete_requires_content_type_for_id(server: TSC.Server) -> None:
    with pytest.raises(ValueError):
        server.recycle_bin.delete(ITEM_ID)


def test_empty(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.recycle_bin.baseurl, status_code=204)
        result = server.recycle_bin.empty()

    assert result is None
    assert m.last_request.method == "DELETE"
    assert "asjob" not in m.last_request.qs


def test_empty_as_job(server: TSC.Server) -> None:
    with requests_mock.mock() as m:
        m.delete(server.recycle_bin.baseurl, status_code=202, text=RECYCLE_BIN_EMPTY_JOB.read_text())
        job = server.recycle_bin.empty(as_job=True)

    assert m.last_request.qs["asjob"] == ["true"]
    assert job.id == "33333333-3333-4333-8333-333333333333"
    assert job.type == "EmptyRecycleBin"
