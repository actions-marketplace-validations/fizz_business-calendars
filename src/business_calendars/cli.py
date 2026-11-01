"""business-day: say whether a day is a business day, for shell and CI gating.

Usage:
  business-day [--tz ZONE] [--when tomorrow|today|YYYY-MM-DD] CALENDAR.json [...]
  business-day --count YYYY-MM CALENDAR.json [...]

Prints the date and the reason ("business day", "Saturday", or the holiday's name).
Exit 0 for a business day, 1 for any other day, 2 on bad input. With --count, prints
the number of business days in the month and exits 0.
"""

import argparse
import datetime as dt
import sys
from zoneinfo import ZoneInfo

from .days import business_days_in_month, is_business_day, load


def main(argv=None):
    ap = argparse.ArgumentParser(prog="business-day", description=__doc__.splitlines()[0])
    ap.add_argument("calendars", nargs="+", help="holiday JSON files; a date in any of them is a holiday")
    ap.add_argument("--tz", default="UTC", help="time zone that decides today and tomorrow (default UTC)")
    ap.add_argument("--when", default="tomorrow", help="tomorrow (default), today, or YYYY-MM-DD")
    ap.add_argument("--count", metavar="YYYY-MM", help="print the month's business-day count instead")
    args = ap.parse_args(argv)

    try:
        holidays = load(*args.calendars)
        if args.count:
            year, month = (int(x) for x in args.count.split("-"))
            print(business_days_in_month(year, month, holidays))
            return 0
        today = dt.datetime.now(ZoneInfo(args.tz)).date()
        day = {
            "today": today,
            "tomorrow": today + dt.timedelta(days=1),
        }.get(args.when) or dt.date.fromisoformat(args.when)
    except (OSError, ValueError, KeyError) as e:
        print(f"business-day: {e}", file=sys.stderr)
        return 2

    ok, reason = is_business_day(day, holidays)
    print(f"{day.isoformat()} {reason}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
