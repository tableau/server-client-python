import datetime

# This code below is from the python documentation for
# tzinfo: https://docs.python.org/2.3/lib/datetime-tzinfo.html

ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)


class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()
TABLEAU_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def parse_datetime(date):
    if date is None:
        return None

    try:
        return datetime.datetime.strptime(date, TABLEAU_DATE_FORMAT).replace(tzinfo=utc)
    except ValueError:
        return None


def format_datetime(date):
    if date is None:
        return None

    return date.astimezone(tz=utc).strftime(TABLEAU_DATE_FORMAT)
