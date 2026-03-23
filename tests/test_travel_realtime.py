import unittest
from datetime import date

from travel_realtime import format_date_for_api, infer_hotel_dates, infer_trip_date


class TravelRealtimeTests(unittest.TestCase):
    def test_infer_trip_date_uses_current_year_when_month_is_upcoming(self):
        trip_date = infer_trip_date(10, 3, today=date(2026, 3, 23))
        self.assertEqual(trip_date, date(2026, 10, 3))

    def test_infer_trip_date_rolls_to_next_year_for_past_month(self):
        trip_date = infer_trip_date(1, 2, today=date(2026, 3, 23))
        self.assertEqual(trip_date, date(2027, 1, 2))

    def test_infer_hotel_dates_returns_one_night_window(self):
        player = {"month": 11, "day": 5}
        check_in, check_out = infer_hotel_dates(player)
        self.assertEqual((check_out - check_in).days, 1)

    def test_format_date_for_api_returns_iso_string(self):
        self.assertEqual(format_date_for_api(date(2026, 10, 3)), "2026-10-03")


if __name__ == "__main__":
    unittest.main()
