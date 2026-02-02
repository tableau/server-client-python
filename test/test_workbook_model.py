import pytest

import tableauserverclient as TSC


def test_invalid_show_tabs():
    workbook = TSC.WorkbookItem("10")
    with pytest.raises(ValueError):
        workbook.show_tabs = "Hello"

    with pytest.raises(ValueError):
        workbook.show_tabs = None
