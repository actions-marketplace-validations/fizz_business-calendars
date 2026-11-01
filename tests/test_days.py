import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from business_calendars import business_days_in_month, is_business_day, load, next_business_day
from business_calendars.cli import main

D = dt.date


class CalendarTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.us = Path(self.dir.name, "us.json")
        self.us.write_text(json.dumps([
            {"date": "2026-11-11", "name": "Veterans Day"},
            {"date": "2026-11-26", "name": "Thanksgiving Day"},
            {"date": "2027-01-18", "name": "Martin Luther King Jr. Day"},
        ]))
        self.india = Path(self.dir.name, "in.json")
        self.india.write_text(json.dumps([
            {"date": "2027-03-22", "name": "Holi"},
            {"date": "2026-11-11", "name": "Example shared day"},
        ]))

    def tearDown(self):
        self.dir.cleanup()

    def test_weekends_and_holidays_are_not_business_days(self):
        h = load(self.us)
        self.assertEqual(is_business_day(D(2026, 11, 7), h), (False, "Saturday"))
        self.assertEqual(is_business_day(D(2026, 11, 11), h), (False, "Veterans Day"))
        self.assertEqual(is_business_day(D(2026, 11, 2), h), (True, "business day"))

    def test_a_date_in_any_calendar_is_a_holiday(self):
        self.assertTrue(is_business_day(D(2027, 3, 22), load(self.us))[0])
        self.assertFalse(is_business_day(D(2027, 3, 22), load(self.us, self.india))[0])

    def test_a_shared_date_keeps_both_names(self):
        h = load(self.us, self.india)
        self.assertEqual(h[D(2026, 11, 11)], "Veterans Day; Example shared day")

    def test_next_business_day_skips_a_monday_holiday(self):
        self.assertEqual(next_business_day(D(2027, 1, 15), load(self.us)), D(2027, 1, 19))

    def test_business_days_in_month(self):
        # November 2026: 21 weekdays, less Veterans Day and Thanksgiving.
        self.assertEqual(business_days_in_month(2026, 11, load(self.us)), 19)

    def test_cli_exit_codes(self):
        self.assertEqual(main(["--when", "2026-11-02", str(self.us)]), 0)
        self.assertEqual(main(["--when", "2026-11-11", str(self.us)]), 1)
        self.assertEqual(main(["--when", "2026-11-02", str(Path(self.dir.name, "nope.json"))]), 2)
        self.assertEqual(main(["--count", "2026-11", str(self.us)]), 0)


if __name__ == "__main__":
    unittest.main()
