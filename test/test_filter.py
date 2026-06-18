import datetime

import tableauserverclient as TSC


def test_filter_equal():
    filter = TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals, "Superstore")

    assert str(filter) == "name:eq:Superstore"


def test_filter_in():
    # create a IN filter condition with project names that
    # contain spaces and "special" characters
    projects_to_find = ["default", "Salesforce Sales Projeśt"]
    filter = TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.In, projects_to_find)

    assert str(filter) == "name:in:[default,Salesforce Sales Projeśt]"


def test_filter_date_no_encoding():
    """Date filter values should not have colons pre-encoded (fixes #1025).

    The requests library handles URL encoding of the whole filter parameter,
    so pre-encoding colons in datetime values causes double-encoding on the wire.
    """
    utc = datetime.timezone.utc
    dt = datetime.datetime(2023, 1, 1, 0, 0, 0, tzinfo=utc)
    filter = TSC.Filter(TSC.RequestOptions.Field.CreatedAt, TSC.RequestOptions.Operator.LessThan, dt)

    result = str(filter)
    assert result == "createdAt:lt:2023-01-01T00:00:00Z"
    assert "%3A" not in result, "Colons in datetime values must not be percent-encoded"
