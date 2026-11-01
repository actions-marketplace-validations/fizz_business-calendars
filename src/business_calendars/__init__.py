"""Business days from holiday calendars that every tool in an estate shares.

A calendar is a JSON list of {"date": "YYYY-MM-DD", "name": ...}, observed dates
included. A resource reads a list of calendars, and a day is a business day for it
when it is a weekday and no calendar in its list has that date.
"""

from .days import (
    Calendar,
    business_days_in_month,
    is_business_day,
    load,
    next_business_day,
)

__all__ = ["Calendar", "business_days_in_month", "is_business_day", "load", "next_business_day"]
__version__ = "0.1.0"
