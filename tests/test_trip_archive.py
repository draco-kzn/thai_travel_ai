import unittest
from pathlib import Path
import shutil
from unittest.mock import patch

import trip_archive


class TripArchiveTests(unittest.TestCase):
    def setUp(self):
        self.archive_dir = Path(__file__).resolve().parent / "_tmp_trip_archive"
        self.archive_file = self.archive_dir / "trip_journals.json"
        if self.archive_dir.exists():
            shutil.rmtree(self.archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.dir_patcher = patch.object(trip_archive, "ARCHIVE_DIR", self.archive_dir)
        self.file_patcher = patch.object(trip_archive, "ARCHIVE_FILE", self.archive_file)
        self.dir_patcher.start()
        self.file_patcher.start()

    def tearDown(self):
        self.file_patcher.stop()
        self.dir_patcher.stop()
        if self.archive_dir.exists():
            shutil.rmtree(self.archive_dir)

    def test_build_trip_journal_includes_route_and_summary(self):
        player = {
            "route_path": ["Bangkok", "Phuket", "Phi Phi Islands"],
            "visited_activities": {"hkt_patong", "pp_view"},
            "fail_reason": "🎉 完美收官，带着回忆回家了。",
            "success": True,
            "day": 4,
            "max_days": 5,
            "money": 12345,
            "month": 10,
            "city": "Phi Phi Islands",
            "history": ["[Day 4 18:00] 完成行程"],
        }

        journal = trip_archive.build_trip_journal(player, "https://example.com/cover.jpg")

        self.assertEqual(journal["route_path"], ["曼谷", "普吉岛", "皮皮岛"])
        self.assertEqual(journal["activity_count"], 2)
        self.assertIn("曼谷", journal["summary"])
        self.assertEqual(journal["cover_image_url"], "https://example.com/cover.jpg")

    def test_save_list_and_delete_trip_journal(self):
        journal = {
            "id": "abc",
            "title": "Test Trip",
            "saved_at": "2026-03-23T20:00:00",
            "days": 2,
            "activity_count": 1,
            "final_city": "曼谷",
            "summary": "summary",
            "activities": [],
            "history": [],
            "route_path": ["曼谷"],
            "fail_reason": "",
            "outcome": "完美收官",
            "cover_image_url": "",
        }

        trip_archive.save_trip_journal(journal)
        items = trip_archive.list_trip_journals()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "abc")

        selected = trip_archive.get_trip_journal("abc")
        self.assertIsNotNone(selected)
        self.assertEqual(selected["title"], "Test Trip")

        deleted = trip_archive.delete_trip_journal("abc")
        self.assertTrue(deleted)
        self.assertEqual(trip_archive.list_trip_journals(), [])


if __name__ == "__main__":
    unittest.main()
