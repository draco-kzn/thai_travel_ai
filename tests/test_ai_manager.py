import unittest
from types import SimpleNamespace
from unittest.mock import patch

import ai_manager


class AIManagerTests(unittest.TestCase):
    def test_each_city_has_dedicated_bgm_mapping(self):
        fake_st = SimpleNamespace(session_state={})
        with patch.object(ai_manager, "st", fake_st):
            manager = ai_manager.AIManager()
            bgm_by_city = {
                city: manager.get_bgm(city, "noon")
                for city in [
                    "Bangkok",
                    "Chiang Mai",
                    "Pattaya",
                    "Hua Hin",
                    "Phuket",
                    "Krabi",
                    "Koh Samui",
                    "Phi Phi Islands",
                    "Koh Lanta",
                    "Koh Lipe",
                ]
            }

        self.assertEqual(len(bgm_by_city), 10)
        self.assertGreaterEqual(len(set(bgm_by_city.values())), 8)
        for city, url in bgm_by_city.items():
            with self.subTest(city=city):
                self.assertTrue(url.startswith("https://"))
                self.assertTrue(url.endswith(".mp3"))

    def test_bgm_changes_by_time_phase_for_multiple_cities(self):
        fake_st = SimpleNamespace(session_state={})
        with patch.object(ai_manager, "st", fake_st):
            manager = ai_manager.AIManager()
            changed_cities = 0
            for city in ["Bangkok", "Pattaya", "Phuket", "Koh Samui", "Koh Lipe"]:
                day_track = manager.get_bgm(city, "noon")
                night_track = manager.get_bgm(city, "night")
                if day_track != night_track:
                    changed_cities += 1

        self.assertGreaterEqual(changed_cities, 4)


if __name__ == "__main__":
    unittest.main()
