from datetime import datetime, timezone


def as_utc(value):
    """
    PyMongo returns datetimes as timezone-naive values (they are
    stored in UTC). Mark them as UTC so they can be compared and
    serialised correctly.
    """

    if not isinstance(value, datetime):
        return None

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def iso_utc(value):
    """
    ISO string that always ends with +00:00, so the browser converts
    it to the user's local time correctly. A naive ISO string would
    be read as local time and show the wrong "time ago".
    """

    value = as_utc(value)

    if value is None:
        return None

    return value.isoformat()
