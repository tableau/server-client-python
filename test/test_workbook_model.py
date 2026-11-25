import pytest

import tableauserverclient as TSC


def test_invalid_show_tabs():
    workbook = TSC.WorkbookItem("10")
    with pytest.raises(ValueError):
        workbook.show_tabs = "Hello"

    with pytest.raises(ValueError):
        workbook.show_tabs = None


@pytest.mark.parametrize("value", [True, False, None])
def test_bridge_refresh_embedded_files_accepts_bool_or_none(value: bool | None) -> None:
    workbook = TSC.WorkbookItem("project_id", name="wb", bridge_refresh_embedded_files=value)
    assert workbook.bridge_refresh_embedded_files is value


def test_bridge_refresh_embedded_files_can_be_cleared() -> None:
    workbook = TSC.WorkbookItem("project_id", name="wb", bridge_refresh_embedded_files=True)
    workbook.bridge_refresh_embedded_files = None
    assert workbook.bridge_refresh_embedded_files is None


@pytest.mark.parametrize("value", ["yes", "true", 1, 0])
def test_bridge_refresh_embedded_files_rejects_non_boolean(value: object) -> None:
    workbook = TSC.WorkbookItem("project_id", name="wb")
    with pytest.raises(ValueError):
        workbook.bridge_refresh_embedded_files = value  # type: ignore[assignment]
    with pytest.raises(ValueError):
        TSC.WorkbookItem("project_id", name="wb", bridge_refresh_embedded_files=value)  # type: ignore[arg-type]
