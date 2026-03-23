import unittest
from datetime import date

from travel_realtime import (
    _parse_iso_duration_to_minutes,
    build_realtime_flight_plan,
    format_date_for_api,
    infer_hotel_dates,
    infer_trip_date,
)


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

    def test_phi_phi_to_phuket_is_not_queryable_as_flight(self):
        plan = build_realtime_flight_plan("Phi Phi Islands", "Phuket")
        self.assertFalse(plan["queryable"])
        self.assertIn(plan["kind"], {"surface_only", "same_gateway_surface"})

    def test_bangkok_to_phi_phi_queries_gateway_flight(self):
        plan = build_realtime_flight_plan("Bangkok", "Phi Phi Islands")
        self.assertTrue(plan["queryable"])
        self.assertEqual(plan["kind"], "gateway_flight")
        self.assertEqual(plan["origin_code"], "BKK")
        self.assertEqual(plan["destination_code"], "HKT")

    def test_parse_iso_duration_to_minutes(self):
        self.assertEqual(_parse_iso_duration_to_minutes("PT2H35M"), 155)

    def test_bangkok_to_hua_hin_is_not_queryable_as_flight(self):
        plan = build_realtime_flight_plan("Bangkok", "Hua Hin")
        self.assertFalse(plan["queryable"])


if __name__ == "__main__":
    unittest.main()
