import random

import streamlit as st

from ai_manager import ai_bot
from data_store import CITY_PRICE_MULTIPLIER, GAME_DATA, TRAVEL_ROUTES


DEFAULT_WEATHER_PROBS = {"sunny": 0.6, "cloudy": 0.3, "rainy": 0.1}


class GameState:
    def __init__(self):
        if "player" not in st.session_state:
            st.session_state.player = None

    @property
    def data(self):
        return st.session_state.player

    def reset_game(self):
        st.session_state.player = None
        st.session_state.pop("bg_image_url", None)
        st.session_state.pop("bg_state_key", None)

    def start_game(self, start_city, budget, start_time, total_days, start_month):
        st.session_state.player = {
            "money": budget,
            "stamina": 100,
            "max_stamina": 100,
            "day": 1,
            "max_days": total_days,
            "time": start_time,
            "city": start_city,
            "month": start_month,
            "weather": "sunny",
            "hotel_settled": False,
            "history": [f"✈️ {start_month} 月抵达 {GAME_DATA[start_city]['name_cn']}，旅程开始。"],
            "game_over": False,
            "fail_reason": "",
            "success": False,
            "visited_activities": set(),
        }
        self.refresh_weather()

    def refresh_weather(self):
        if not self.data:
            return

        probs = ai_bot.get_weather_probabilities(self.data["city"], self.data["month"])
        weights = []
        for weather_type in ("sunny", "cloudy", "rainy"):
            try:
                weight = float(probs.get(weather_type, DEFAULT_WEATHER_PROBS[weather_type]))
            except (TypeError, ValueError, AttributeError):
                weight = DEFAULT_WEATHER_PROBS[weather_type]
            weights.append(max(weight, 0.0))

        if sum(weights) <= 0:
            weights = [DEFAULT_WEATHER_PROBS[k] for k in ("sunny", "cloudy", "rainy")]

        self.data["weather"] = random.choices(["sunny", "cloudy", "rainy"], weights=weights, k=1)[0]

    def settle_hotel(self, hotel):
        if self.data["money"] < hotel["price"]:
            return False

        self._update(money=hotel["price"], time=1)
        self.data["hotel_settled"] = True
        self.log(f"🏨 入住了 {hotel['name']}")
        return True

    def do_activity(self, act_id, money, stamina, time, name):
        if self.data["weather"] == "rainy" and stamina > 0:
            stamina = int(round(stamina * 1.2))

        self._update(money=money, stamina=stamina, time=time)
        self.data["visited_activities"].add(act_id)
        self.log(f"✅ 体验了 {name}")

    def sleep(self, hours=None):
        if hours:
            recover = hours * 10
            self._recover_stamina(recover)
            self.data["time"] += hours
            self.log(f"🛌 休息了 {hours} 小时。")
            if not self.data["game_over"] and self.data["time"] >= 22:
                self.sleep()
            return

        self._overnight_rest()

    def travel_to(self, target_city):
        start_city = self.data["city"]
        route = TRAVEL_ROUTES.get(start_city, {}).get(target_city)
        if not route:
            raise ValueError(f"Unknown travel route: {start_city} -> {target_city}")

        self.data["stamina"] -= route["cost_stamina"]
        self.data["city"] = target_city

        arrival = self.data["time"] + route["cost_time"]
        if arrival >= 22:
            self.data["day"] += 1
            self.data["time"] = 8
            self.data["hotel_settled"] = False
            self.log(f"🚆 抵达 {GAME_DATA[target_city]['name_cn']}（过夜到达）。")
        else:
            self.data["time"] = arrival
            self.log(f"🚆 抵达 {GAME_DATA[target_city]['name_cn']}。")

        self.refresh_weather()
        self._check_day_limit()
        self._check_game_over()
        self._check_force_sleep()

    def finish_game(self):
        self.data["game_over"] = True
        self.data["success"] = True
        self.data["fail_reason"] = "🎉 完美收官，带着回忆回家了。"

    def _update(self, money=0, stamina=0, time=0):
        self.data["money"] -= money
        self.data["stamina"] -= stamina
        self.data["time"] += time
        self._check_game_over()
        self._check_force_sleep()

    def _overnight_rest(self):
        current_time = self.data["time"]
        if current_time >= 24:
            hours_slept = max(4, 32 - current_time)
        else:
            hours_slept = (24 - current_time) + 8

        self._recover_stamina(hours_slept * 15)
        self.data["day"] += 1
        self.data["time"] = 8
        self.data["hotel_settled"] = False
        self.log(f"🌙 睡到了自然醒（第 {self.data['day']} 天）。")
        self.refresh_weather()
        self._check_day_limit()

    def _recover_stamina(self, amount):
        self.data["stamina"] = min(self.data["max_stamina"], self.data["stamina"] + amount)

    def _check_day_limit(self):
        if self.data["day"] > self.data["max_days"]:
            self._mark_game_over("🛂 签证到期，必须回国了。")

    def _check_game_over(self):
        if self.data["money"] < 0:
            self._mark_game_over("💸 破产了，旅费已经见底。")

    def _check_force_sleep(self):
        if self.data["game_over"]:
            return

        if self.data["stamina"] <= 0:
            self.log("😵 累到不行，强制休息。")
            self.sleep()
        elif self.data["time"] >= 22:
            self.log("🌙 太晚了，强制睡觉。")
            self.sleep()

    def _mark_game_over(self, reason):
        self.data["game_over"] = True
        self.data["fail_reason"] = reason

    def get_current_city_data(self):
        return GAME_DATA.get(self.data["city"], {})

    def get_travel_choices(self):
        return TRAVEL_ROUTES.get(self.data["city"], {})

    def log(self, msg):
        self.data["history"].insert(0, f"[Day {self.data['day']} {int(self.data['time']):02d}:00] {msg}")

    def get_hotel_options(self):
        city = self.data["city"]
        multiplier = CITY_PRICE_MULTIPLIER.get(city, 1.0)
        return [
            {"name": "背包客栈", "price": int(300 * multiplier), "desc": "省钱首选"},
            {"name": "标准酒店", "price": int(1500 * multiplier), "desc": "舒适安全"},
            {"name": "豪华度假村", "price": int(5000 * multiplier), "desc": "奢华享受"},
        ]


game = GameState()
