import pytest

import tableauserverclient as TSC


def test_invalid_minimum_site_role():
    group = TSC.GroupItem("grp")
    with pytest.raises(ValueError):
        group.minimum_site_role = "Captain"


def test_invalid_license_mode():
    group = TSC.GroupItem("grp")
    with pytest.raises(ValueError):
        group.license_mode = "off"
