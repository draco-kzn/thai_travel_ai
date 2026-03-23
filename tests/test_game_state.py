import unittest
from types import SimpleNamespace
from unittest.mock import patch

import game_state


class FakeSessionState(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class GameStateLogicTests(unittest.TestCase):
    def setUp(self):
        self.fake_st = SimpleNamespace(session_state=FakeSessionState())
        self.fake_ai_bot = SimpleNamespace(
            get_weather_probabilities=lambda city, month: {"sunny": 1.0, "cloudy": 0.0, "rainy": 0.0}
        )

        self.st_patcher = patch.object(game_state, "st", self.fake_st)
        self.ai_patcher = patch.object(game_state, "ai_bot", self.fake_ai_bot)
        self.st_patcher.start()
        self.ai_patcher.start()

        self.game = game_state.GameState()

    def tearDown(self):
        self.ai_patcher.stop()
        self.st_patcher.stop()

    def test_start_game_initializes_player_state(self):
        self.game.start_game("Bangkok", 30000, 10, 5, 10)

        player = self.game.data
        self.assertEqual(player["city"], "Bangkok")
        self.assertEqual(player["money"], 30000)
        self.assertEqual(player["day"], 1)
        self.assertEqual(player["weather"], "sunny")
        self.assertFalse(player["game_over"])

    def test_settle_hotel_updates_state(self):
        self.game.start_game("Bangkok", 30000, 8, 5, 10)
        hotel = {"name": "标准酒店", "price": 1500}

        settled = self.game.settle_hotel(hotel)

        self.assertTrue(settled)
        self.assertEqual(self.game.data["money"], 28500)
        self.assertEqual(self.game.data["time"], 9)
        self.assertTrue(self.game.data["hotel_settled"])

    def test_rainy_activity_costs_more_stamina(self):
        self.game.start_game("Bangkok", 30000, 10, 5, 10)
        self.game.data["weather"] = "rainy"

        self.game.do_activity("test", 100, 10, 2, "测试活动")

        self.assertEqual(self.game.data["money"], 29900)
        self.assertEqual(self.game.data["stamina"], 88)
        self.assertIn("test", self.game.data["visited_activities"])

    def test_overnight_travel_can_end_game_when_days_exceeded(self):
        self.game.start_game("Bangkok", 30000, 20, 1, 10)

        self.game.travel_to("Chiang Mai")

        self.assertTrue(self.game.data["game_over"])
        self.assertIn("签证到期", self.game.data["fail_reason"])

    def test_invalid_route_raises_value_error(self):
        self.game.start_game("Bangkok", 30000, 10, 5, 10)

        with self.assertRaises(ValueError):
            self.game.travel_to("Atlantis")

    def test_reset_game_clears_player_and_cached_images(self):
        self.game.start_game("Bangkok", 30000, 10, 5, 10)
        self.fake_st.session_state["bg_image_url"] = "demo"
        self.fake_st.session_state["bg_state_key"] = "demo_key"

        self.game.reset_game()

        self.assertIsNone(self.fake_st.session_state["player"])
        self.assertNotIn("bg_image_url", self.fake_st.session_state)
        self.assertNotIn("bg_state_key", self.fake_st.session_state)


if __name__ == "__main__":
    unittest.main()
