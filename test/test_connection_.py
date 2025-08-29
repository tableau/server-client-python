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


def test_ignore_query_tag_for_hyper():
    conn = TSC.ConnectionItem()
    conn._connection_type = "hyper"
    conn.query_tagging = True
    assert conn.query_tagging is None


def test_ignore_query_tag_for_teradata():
    conn = TSC.ConnectionItem()
    conn._connection_type = "teradata"
    conn.query_tagging = True
    assert conn.query_tagging is None


def test_ignore_query_tag_for_snowflake():
    conn = TSC.ConnectionItem()
    conn._connection_type = "snowflake"
    conn.query_tagging = True
    assert conn.query_tagging is None
