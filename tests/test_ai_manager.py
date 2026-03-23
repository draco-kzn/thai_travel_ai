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
                city: manager.get_bgm(city)
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


if __name__ == "__main__":
    unittest.main()
