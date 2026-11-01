# /// script
# requires-python = ">=3.11"
# dependencies = ["holidays"]
# ///
"""Build calendars/<country>.json from python-holidays (MIT), observed dates included.

The holidays dependency is left unpinned on purpose: this script exists to pick up
the newest data, including holidays a country adds in the middle of a year.

Usage: uv run scripts/build.py [--out calendars] [--years 2026 2027] US IN ...
Years default to this year and next. Prints one line per file that changed.
"""

import argparse
import datetime as dt
import json
from importlib.metadata import version
from pathlib import Path

import holidays


def build(country, years):
    days = {}
    for year in years:
        for day, name in holidays.country_holidays(country, years=year, observed=True).items():
            days[day.isoformat()] = name
    return [{"date": d, "name": days[d]} for d in sorted(days)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("countries", nargs="+", help="ISO 3166-1 alpha-2 codes")
    ap.add_argument("--out", type=Path, default=Path("calendars"))
    ap.add_argument("--years", nargs="*", type=int)
    args = ap.parse_args()

    this_year = dt.date.today().year
    years = args.years or [this_year, this_year + 1]
    args.out.mkdir(parents=True, exist_ok=True)
    for country in args.countries:
        path = args.out / f"{country.lower()}.json"
        text = json.dumps(build(country.upper(), years), indent=2, ensure_ascii=False) + "\n"
        if not path.exists() or path.read_text() != text:
            path.write_text(text)
            print(f"{path} changed (python-holidays {version('holidays')}, years {years})")


if __name__ == "__main__":
    main()
