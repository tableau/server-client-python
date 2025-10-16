import pytest

import tableauserverclient as TSC


def test_nullable_project_id():
    datasource = TSC.DatasourceItem(name="10")
    assert datasource.project_id is None


def test_require_boolean_flag_bridge_fail():
    datasource = TSC.DatasourceItem("10")
    with pytest.raises(ValueError):
        datasource.use_remote_query_agent = "yes"


def test_require_boolean_flag_bridge_ok():
    datasource = TSC.DatasourceItem("10")
    datasource.use_remote_query_agent = True
    assert datasource.use_remote_query_agent
