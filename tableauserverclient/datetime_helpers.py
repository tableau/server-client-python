import datetime

ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)


def timestamp():
    """Return the current local time as an HH:MM:SS string."""
    return datetime.datetime.now().strftime("%H:%M:%S")


# This class is a concrete implementation of the abstract base class tzinfo
# docs: https://docs.python.org/2.3/lib/datetime-tzinfo.html
class UTC(datetime.tzinfo):
    """UTC timezone implementation for use with datetime objects."""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()
TABLEAU_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# Tableau Cloud emits some datetimes with a numeric UTC offset instead of the trailing "Z"
# used by Tableau Server -- e.g. the ``nextRunAt`` attribute inlined into a subscription's
# ``<schedule>`` element on Cloud looks like ``2026-08-29T16:55:00-0700``. Accept both.
TABLEAU_CLOUD_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def parse_datetime(date):
    """Parse a Tableau API datetime string into a timezone-aware datetime, or ``None``.

    Handles both the Server ``...Z`` form and the Cloud ``...+/-HHMM`` form. Returns
    ``None`` for both absent input (``None``) and unparseable non-empty input --
    matching the pre-Cloud lenient contract so a malformed server response cannot
    crash a page-through of unrelated data. User-supplied setter values are
    validated at the property-decorator boundary (see
    :func:`tableauserverclient.models.property_decorators.property_is_datetime`).
    """
    if date is None:
        return None
    try:
        return datetime.datetime.strptime(date, TABLEAU_DATE_FORMAT).replace(tzinfo=utc)
    except ValueError:
        pass
    try:
        return datetime.datetime.strptime(date, TABLEAU_CLOUD_DATE_FORMAT)
    except ValueError:
        return None


def format_datetime(date):
    """Format a datetime as a Tableau API datetime string, or None if absent."""
    if date is None:
        return None

    return date.astimezone(tz=utc).strftime(TABLEAU_DATE_FORMAT)
