# business-calendars

A schedule that says "every Monday" spends money on a Monday holiday and runs a report nobody reads. This repo makes the business day data: holiday calendars that every tool in an estate reads, so a spend limit, a report and an approval gate agree on which days count.

Trading firms work this way. A firm is open when its market is open, and every dataset it ingests carries the calendar of its own market. Here, every resource carries the calendars of the people it serves: a US government workload reads the US calendar, and a dev cluster for a team in the US and India reads both.

## Calendars

`calendars/` has one JSON file for each country, built from [python-holidays](https://github.com/vacanza/holidays) (MIT), observed dates included:

```json
[
  { "date": "2026-11-11", "name": "Veterans Day" },
  { "date": "2026-11-26", "name": "Thanksgiving Day" }
]
```

| File | Country |
|---|---|
| `calendars/us.json` | United States (federal) |
| `calendars/in.json` | India (national) |

A day is a business day for a list of calendars when it is a weekday and no calendar in the list has that date.

Countries add holidays in the middle of a year: Juneteenth was signed on 2021-06-17 and observed the next day. So the `Refresh` workflow rebuilds the calendars every day. When a date changes, it commits the calendars, tags the next patch version and publishes a release that lists the changed dates.

## Use it in GitHub Actions

Run a job only on the evening before a business day:

```yaml
on:
  schedule:
    - cron: '7 1 * * *'   # 01:07 UTC

jobs:
  ask:
    runs-on: ubuntu-latest
    steps:
      - id: day
        uses: fizz/business-calendars@<commit SHA> # vX.Y.Z
        with:
          calendars: us in          # built-in names, or paths in your repo
          when: tomorrow
          tz: America/Chicago

      - if: steps.day.outputs.business == 'true'
        run: echo "Tomorrow, ${{ steps.day.outputs.date }}, is a business day."
```

Outputs: `business` (`true` or `false`), `date`, and `reason` (`business day`, the weekday name, or the holiday name).

Pin a commit SHA, not a tag. Dependabot's `github-actions` updater moves the pin when a release changes a calendar, so a new holiday comes to your repo as a pull request that you review.

## Use it from the shell

```sh
PYTHONPATH=src python -m business_calendars.cli --tz America/Chicago calendars/us.json
# 2026-11-02 business day          (exit 0)

python -m business_calendars.cli --when 2027-03-22 calendars/us.json calendars/in.json
# 2027-03-22 Holi                  (exit 1)

python -m business_calendars.cli --count 2026-11 calendars/us.json
# 19
```

Exit 0 for a business day, 1 for any other day, 2 on bad input. The package has no dependencies, and `pip install` gives the same command as `business-day`.

## Use it in Terraform

```hcl
locals {
  holidays = [for h in jsondecode(file("${path.module}/calendars/us.json")) : h.date]
}
```

If the calendars live outside the module, add their directory to the plan workflow's path filter, so a new holiday plans every module that reads it.

## Calendars from holidaydb

[holidaydb](https://holidaydb.com) updates its data every day. Its terms give each account a non-transferable licence, so this repo does not publish holidaydb data. To use it, get an API key for your organization, then build your own calendars in your own repo:

```sh
HOLIDAYDB_API_KEY=... uv run scripts/holidaydb.py calendars/us.json --country US
python scripts/compare.py calendars/us.json /path/to/business-calendars/calendars/us.json --label US
```

`compare.py` prints the dates that the two sources do not agree on, and exits 1 when they differ. For 2026 and 2027, holidaydb and python-holidays have the same 27 US dates. Only five names are different, for example "Presidents' Day" and "Washington's Birthday".

## Tests

```sh
PYTHONPATH=src python -m unittest discover -s tests -v
```

## License

MIT. The calendars come from python-holidays, which is also MIT.
