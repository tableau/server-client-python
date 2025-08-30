import tableauserverclient as TSC

import pytest


def test_require_boolean_query_tag_fails():
    conn = TSC.ConnectionItem()
    conn._connection_type = "postgres"
    with pytest.raises(ValueError):
        conn.query_tagging = "no"


def test_set_query_tag_normal_conn():
    conn = TSC.ConnectionItem()
    conn._connection_type = "postgres"
    conn.query_tagging = True
    assert conn.query_tagging


@pytest.mark.parametrize("conn_type", ["hyper", "teradata", "snowflake"])
def test_ignore_query_tag(conn_type):
    conn = TSC.ConnectionItem()
    conn._connection_type = conn_type
    conn.query_tagging = True
    assert conn.query_tagging is None
