import unittest

from data_store import CITY_PRICE_MULTIPLIER, GAME_DATA, TRAVEL_ROUTES


class TravelSimulatorDataTests(unittest.TestCase):
    def test_city_multipliers_cover_every_city(self):
        self.assertEqual(set(CITY_PRICE_MULTIPLIER), set(GAME_DATA))

    def test_each_city_has_activities(self):
        for city, city_data in GAME_DATA.items():
            with self.subTest(city=city):
                activities = city_data.get("activities", [])
                self.assertGreater(len(activities), 0)

    def test_activities_have_required_fields(self):
        required_fields = {"id", "name", "desc", "cost_money", "cost_stamina", "cost_time", "type"}

        for city, city_data in GAME_DATA.items():
            for activity in city_data["activities"]:
                with self.subTest(city=city, activity=activity.get("id")):
                    self.assertTrue(required_fields.issubset(activity.keys()))

    def test_travel_routes_exist_between_distinct_cities(self):
        cities = set(GAME_DATA)

        for start_city, routes in TRAVEL_ROUTES.items():
            with self.subTest(start_city=start_city):
                self.assertEqual(set(routes.keys()), cities - {start_city})

    def test_travel_routes_have_positive_costs(self):
        for start_city, routes in TRAVEL_ROUTES.items():
            for end_city, route in routes.items():
                with self.subTest(start_city=start_city, end_city=end_city):
                    self.assertGreater(route["cost_time"], 0)
                    self.assertGreater(route["cost_stamina"], 0)
                    self.assertIsInstance(route["mode"], str)
                    self.assertTrue(route["mode"].strip())


if __name__ == "__main__":
    unittest.main()
