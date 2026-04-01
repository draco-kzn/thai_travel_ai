import unittest
from types import SimpleNamespace
from pathlib import Path
import shutil
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

    def test_city_fallback_images_are_not_all_the_same(self):
        fallback_images = {
            city: ai_manager.get_city_fallback_image(city)
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

        self.assertEqual(len(fallback_images), 10)
        self.assertGreaterEqual(len(set(fallback_images.values())), 10)

    def test_city_fallback_images_change_with_weather_and_time(self):
        sunny_day = ai_manager.get_city_fallback_image("Krabi", "sunny", "noon")
        rainy_day = ai_manager.get_city_fallback_image("Krabi", "rainy", "noon")
        sunny_night = ai_manager.get_city_fallback_image("Krabi", "sunny", "night")

        self.assertNotEqual(sunny_day, rainy_day)
        self.assertNotEqual(sunny_day, sunny_night)

    def test_local_wallpaper_image_is_used_when_present(self):
        root = Path(__file__).resolve().parent / "_tmp_ai_manager"
        if root.exists():
            shutil.rmtree(root)

        wallpapers = root / "wallpapers" / "bangkok"
        wallpapers.mkdir(parents=True, exist_ok=True)
        image_path = wallpapers / "sunny_noon.jpg"
        image_path.write_bytes(b"fake-jpg-data")
        manifest_path = root / "wallpapers" / "manifest.json"
        manifest_path.write_text(
            '{"Bangkok|sunny|noon": {"path": "wallpapers/bangkok/sunny_noon.jpg"}}',
            encoding="utf-8",
        )

        with patch.object(ai_manager, "ROOT_DIR", root), patch.object(
            ai_manager, "WALLPAPER_MANIFEST_PATH", manifest_path
        ):
            result = ai_manager.get_local_wallpaper_image("Bangkok", "sunny", "noon")

        if root.exists():
            shutil.rmtree(root)

        self.assertTrue(result.startswith("data:image/jpeg;base64,"))


if __name__ == "__main__":
    unittest.main()
