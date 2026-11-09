import datetime

from tableauserverclient.datetime_helpers import format_datetime
from .request_options import RequestOptions


class Filter:
    """Represents a single Tableau REST API filter clause.

    A `Filter` is one entry in a `?filter=` query parameter and serializes as
    ``<field>:<operator>:<value>``. Use one filter per attribute, and pass
    multiple filters via `RequestOptions.filter.add(...)` if you need to AND
    conditions.

    Special characters in filter values
    -----------------------------------
    The server splits the ``filter`` parameter on commas, so a value that
    contains a comma cannot be sent: the request fails with ``400065: Bad
    Request``. URL-encoding the comma or putting a backslash in front of it
    does not help. Other characters, including ``&``, ``:``, ``[`` and ``]``,
    are matched as written; TSC URL-encodes the query string for you.

    To find a name that contains a comma, replace the comma with ``*`` and
    check the results client-side. Tableau Cloud treats ``*`` as a wildcard
    in an ``Equals`` value on name fields, for example
    ``name="Calculations* Groups & Sets"`` finds the workbook
    ``Calculations, Groups & Sets``. The REST API documentation does not
    describe this behavior, so confirm it on your Tableau Server version.

    Parameters
    ----------
    field : str
        The field to filter on (e.g. ``RequestOptions.Field.Name``).

    operator : str
        The operator to apply (e.g. ``RequestOptions.Operator.Equals``,
        ``In``, ``GreaterThan``).

    value : str | int | bool | datetime | list
        The value to compare against. Lists require operator ``In``. Datetimes
        must be timezone-aware and serialize as ISO-8601 UTC. Bools serialize
        as lowercase ``true``/``false``.
    """

    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self._value = None
        self.value = value

    def __str__(self):
        """Return the filter as a Tableau REST API filter string.

        Format: ``<field>:<operator>:<value>``

        Value serialization rules:
        - datetime: ISO-8601 UTC, e.g. ``2023-01-01T00:00:00Z``.
          Naive datetimes (no tzinfo) are rejected with ValueError; always
          pass timezone-aware datetime objects.
        - bool: lowercase ``true`` or ``false`` as required by the REST API.
        - list: bracket-enclosed comma-separated values, e.g. ``[a,b,c]``.
          Only valid with the ``in`` operator.
        - All other types: ``str()`` of the value.
        """
        if isinstance(self._value, datetime.datetime):
            if self._value.tzinfo is None:
                raise ValueError(
                    "Naive datetime passed to Filter; Tableau Server requires UTC. "
                    "Use a timezone-aware datetime, e.g. "
                    "datetime.datetime(..., tzinfo=datetime.timezone.utc)."
                )
            return f"{self.field}:{self.operator}:{format_datetime(self._value)}"
        if isinstance(self._value, bool):
            # Tableau REST API requires lowercase 'true'/'false', not Python's 'True'/'False'
            return f"{self.field}:{self.operator}:{str(self._value).lower()}"
        value_string = str(self._value)
        if isinstance(self._value, list):
            # this should turn the string representation of the list
            # from ['<string1>', '<string2>', ...]
            # to [<string1>,<string2>]
            # so effectively, remove any spaces between "," and "'" and then remove all "'"
            value_string = value_string.replace(", '", ",'").replace("'", "")
        return f"{self.field}:{self.operator}:{value_string}"

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, filter_value):
        if isinstance(filter_value, list) and self.operator != RequestOptions.Operator.In:
            error = "Filter values can only be a list if the operator is 'in'."
            raise ValueError(error)
        else:
            self._value = filter_value
