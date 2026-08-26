"""Direct coverage for ``tableauserverclient.datetime_helpers.parse_datetime``
and the setter-side ``property_is_datetime`` decorator.

Motivation:

``parse_datetime`` is called from every ``ScheduleItem`` / ``SubscriptionItem`` /
property-decorator site that turns a date attribute into a ``datetime``. Its
contract is deliberately lenient on the read side and strict on the write side:

* Absent input (``None``) -> ``None``.
* Well-formed Server form -> UTC-aware ``datetime``.
* Well-formed Cloud form -> aware ``datetime`` with the on-the-wire offset
  preserved (**not** normalised to UTC).
* Unparseable non-empty input -> ``None``. A malformed server response should
  not crash a page-through of unrelated data. This matches the pre-Cloud
  behaviour.

The strictness lives one layer up, in ``property_is_datetime``: an unparseable
*setter* value (user assigning garbage to ``item.created_at``) raises
``ValueError`` so it surfaces at the assignment site rather than silently
nulling the attribute. Server-response paths go through ``parse_datetime``
directly and get the lenient contract.

The tests below lock in each of those behaviours so a future edit can't shift
strictness across the boundary.
"""

from datetime import datetime, timedelta

import pytest

from tableauserverclient.datetime_helpers import (
    TABLEAU_CLOUD_DATE_FORMAT,
    TABLEAU_DATE_FORMAT,
    parse_datetime,
    utc,
)
from tableauserverclient.models.property_decorators import property_is_datetime


def test_parse_datetime_none_returns_none():
    assert parse_datetime(None) is None


def test_parse_datetime_empty_string_returns_none():
    # Empty string does not match either format. parse_datetime is lenient on
    # the read side (server response) and returns None. Strictness on the
    # write side lives in property_is_datetime -- see below.
    assert parse_datetime("") is None


def test_parse_datetime_garbage_returns_none():
    assert parse_datetime("garbage") is None


def test_parse_datetime_server_z_form():
    result = parse_datetime("2026-08-29T16:55:00Z")
    assert result == datetime(2026, 8, 29, 16, 55, 0, tzinfo=utc)
    # Server form is normalised to UTC.
    assert timedelta(0) == result.utcoffset()


def test_parse_datetime_cloud_offset_form_preserved():
    result = parse_datetime("2026-08-29T16:55:00-0700")
    assert result is not None
    # Cloud offsets are deliberately kept -- a future .replace(tzinfo=utc)
    # after strptime would silently shift the instant. Lock that in.
    assert timedelta(hours=-7) == result.utcoffset()
    assert 2026 == result.year
    assert 16 == result.hour


def test_parse_datetime_cloud_offset_with_colon():
    # Python 3.7+ %z accepts the `+HH:MM` colon form as well.
    result = parse_datetime("2026-08-29T16:55:00+00:00")
    assert result is not None
    assert timedelta(0) == result.utcoffset()


def test_parse_datetime_microseconds_returns_none():
    # Neither format has ``%f`` / ``.ffffff`` -- the current implementation
    # rejects the microsecond form. Because parse_datetime is lenient it
    # returns None rather than raising. Locking that in so a broad "add more
    # formats" patch doesn't slip in without a decision.
    assert parse_datetime("2026-08-29T16:55:00.123456Z") is None


def test_format_constants_shape():
    # Guard against a rename regressing the module's public surface -- both
    # constants are documented as module-level and are imported by the
    # subscription/schedule parsers.
    assert TABLEAU_DATE_FORMAT.endswith("Z")
    assert TABLEAU_CLOUD_DATE_FORMAT.endswith("%z")


# ---------------------------------------------------------------------------
# property_is_datetime: the strictness that used to live in parse_datetime
# now lives here. Setter-side unparseable strings raise; server-response-side
# unparseable strings are silently None (covered above).
# ---------------------------------------------------------------------------


class _DateHolder:
    """Minimal host for the ``property_is_datetime`` decorator so we can
    exercise its wrapper directly. Mirrors the ``@X.setter`` +
    ``@property_is_datetime`` stacking used on real model classes (see
    ``MetricItem.created_at``)."""

    def __init__(self):
        self._value = "unset"

    @property
    def created_at(self):
        return self._value

    @created_at.setter
    @property_is_datetime
    def created_at(self, value):
        self._value = value


def test_property_is_datetime_accepts_valid_server_string():
    holder = _DateHolder()
    holder.created_at = "2026-08-29T16:55:00Z"
    assert holder._value == datetime(2026, 8, 29, 16, 55, 0, tzinfo=utc)


def test_property_is_datetime_accepts_valid_cloud_string():
    holder = _DateHolder()
    holder.created_at = "2026-08-29T16:55:00-0700"
    assert holder._value is not None
    assert timedelta(hours=-7) == holder._value.utcoffset()


def test_property_is_datetime_accepts_datetime_instance():
    holder = _DateHolder()
    dt = datetime(2026, 1, 1, tzinfo=utc)
    holder.created_at = dt
    assert holder._value is dt


def test_property_is_datetime_raises_on_garbage_string():
    holder = _DateHolder()
    with pytest.raises(ValueError, match="Cannot parse"):
        holder.created_at = "garbage"


def test_property_is_datetime_raises_on_empty_string():
    holder = _DateHolder()
    with pytest.raises(ValueError, match="Cannot parse"):
        holder.created_at = ""


def test_property_is_datetime_raises_on_non_string_non_datetime():
    holder = _DateHolder()
    with pytest.raises(ValueError, match="Cannot convert"):
        holder.created_at = 12345
