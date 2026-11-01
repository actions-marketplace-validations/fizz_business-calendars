"""Load holiday calendars and answer business-day questions. Standard library only."""

import calendar as _cal
import datetime as dt
import json
from pathlib import Path

Calendar = dict  # date -> holiday name


def load(*paths):
    """Merge holiday files into one calendar. A date in any file is a holiday."""
    days = {}
    for path in paths:
        for h in json.loads(Path(path).read_text()):
            day = dt.date.fromisoformat(h["date"])
            name = h.get("name", "holiday")
            days[day] = f"{days[day]}; {name}" if day in days and name not in days[day] else name
    return days


def is_business_day(day, holidays):
    """Return (is_business_day, reason) for one date."""
    if day.weekday() >= 5:
        return False, day.strftime("%A")
    if day in holidays:
        return False, holidays[day]
    return True, "business day"


def next_business_day(day, holidays):
    """The first business day after day."""
    day += dt.timedelta(days=1)
    while not is_business_day(day, holidays)[0]:
        day += dt.timedelta(days=1)
    return day


def business_days_in_month(year, month, holidays):
    """Weekdays in the month that no calendar marks as a holiday."""
    last = _cal.monthrange(year, month)[1]
    return sum(
        1 for d in range(1, last + 1) if is_business_day(dt.date(year, month, d), holidays)[0]
    )
