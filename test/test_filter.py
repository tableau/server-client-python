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


def test_filter_in_single_value():
    """A single-element list produces valid bracket syntax."""
    filter = TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["sample"])

    assert str(filter) == "tags:in:[sample]"


def test_filter_in_multiple_values():
    """Multi-element list produces comma-separated values inside brackets."""
    filter = TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.In, ["a", "b", "c"])

    assert str(filter) == "tags:in:[a,b,c]"


def test_filter_integer_value():
    """Integer filter values are serialized as plain decimal strings."""
    filter = TSC.Filter(TSC.RequestOptions.Field.Size, TSC.RequestOptions.Operator.GreaterThan, 0)

    assert str(filter) == "size:gt:0"


def test_filter_integer_nonzero():
    filter = TSC.Filter(TSC.RequestOptions.Field.SheetCount, TSC.RequestOptions.Operator.GreaterThanOrEqual, 5)

    assert str(filter) == "sheetCount:gte:5"


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


def test_filter_date_uses_tableau_format():
    """Datetime values are serialized in Tableau ISO-8601 format, not Python default."""
    utc = datetime.timezone.utc
    dt = datetime.datetime(2024, 6, 15, 12, 30, 45, tzinfo=utc)
    filter = TSC.Filter(TSC.RequestOptions.Field.UpdatedAt, TSC.RequestOptions.Operator.GreaterThan, dt)

    result = str(filter)
    # Must use 'T' separator and 'Z' suffix, not Python's space-separated format
    assert result == "updatedAt:gt:2024-06-15T12:30:45Z"
    assert " " not in result.split(":", 2)[2], "Datetime value must not contain a space (Python default format)"


def test_filter_date_non_utc_converted():
    """Non-UTC datetime values are converted to UTC before serialization."""
    eastern = datetime.timezone(datetime.timedelta(hours=-5))
    dt = datetime.datetime(2023, 3, 10, 12, 0, 0, tzinfo=eastern)
    filter = TSC.Filter(TSC.RequestOptions.Field.CreatedAt, TSC.RequestOptions.Operator.Equals, dt)

    result = str(filter)
    assert result == "createdAt:eq:2023-03-10T17:00:00Z"


def test_filter_bool_true():
    """Boolean True is serialized as lowercase 'true' for Tableau REST API."""
    filter = TSC.Filter(TSC.RequestOptions.Field.IsCertified, TSC.RequestOptions.Operator.Equals, True)

    result = str(filter)
    assert result == "isCertified:eq:true"
    assert "True" not in result, "Boolean True must be lowercase 'true'"


def test_filter_bool_false():
    """Boolean False is serialized as lowercase 'false' for Tableau REST API."""
    filter = TSC.Filter(TSC.RequestOptions.Field.IsCertified, TSC.RequestOptions.Operator.Equals, False)

    result = str(filter)
    assert result == "isCertified:eq:false"
    assert "False" not in result, "Boolean False must be lowercase 'false'"


def test_filter_bool_has_extracts():
    """Boolean filter works for hasExtracts field."""
    filter = TSC.Filter(TSC.RequestOptions.Field.HasExtracts, TSC.RequestOptions.Operator.Equals, True)

    assert str(filter) == "hasExtracts:eq:true"


def test_filter_date_naive_raises():
    """A naive datetime (no tzinfo) raises ValueError with a helpful message."""
    import pytest

    naive_dt = datetime.datetime(2023, 1, 1, 12, 0, 0)  # no tzinfo
    f = TSC.Filter(TSC.RequestOptions.Field.CreatedAt, TSC.RequestOptions.Operator.Equals, naive_dt)
    with pytest.raises(ValueError, match="Naive datetime"):
        str(f)


def test_filter_list_rejects_non_in_operator():
    """A list value with a non-In operator raises ValueError."""
    import pytest

    with pytest.raises(ValueError):
        TSC.Filter(TSC.RequestOptions.Field.Tags, TSC.RequestOptions.Operator.Equals, ["a", "b"])
