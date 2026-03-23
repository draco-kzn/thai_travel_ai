import streamlit as st
import random
from data_store import GAME_DATA, TRAVEL_ROUTES, CITY_PRICE_MULTIPLIER
from ai_manager import ai_bot # 👈 引入我们的大脑

class GameState:
    def __init__(self):
        if "player" not in st.session_state:
            st.session_state.player = None

    @property
    def data(self):
        return st.session_state.player

    # === 1. 游戏初始化 (新增: start_month) ===
    def start_game(self, start_city, budget, start_time, total_days, start_month):
        st.session_state.player = {
            "money": budget,
            "stamina": 100,
            "max_stamina": 100,
            "day": 1,
            "max_days": total_days,
            "time": start_time,
            "city": start_city,
            "month": start_month, # ✅ 记录月份
            "weather": "sunny",   # ✅ 默认为晴，马上会刷新
            "hotel_settled": False,
            "history": [f"✈️ {start_month}月，落地 {GAME_DATA[start_city]['name_cn']}，旅程开始！"],
            "game_over": False,
            "fail_reason": "",
            "success": False,
            "visited_activities": set()
        }
        # 开局立刻刷新一次天气
        self.refresh_weather()

    # === 2. 核心：刷新天气 (调用 AI) ===
    def refresh_weather(self):
        city = self.data["city"]
        month = self.data["month"]
        
        # 调用 AI 获取概率
        probs = ai_bot.get_weather_probabilities(city, month)
        
        # 随机生成
        types = ["sunny", "cloudy", "rainy"]
        weights = [probs.get("sunny", 0.6), probs.get("cloudy", 0.3), probs.get("rainy", 0.1)]
        new_weather = random.choices(types, weights=weights, k=1)[0]
        
        self.data["weather"] = new_weather
        # (可选) 可以在日志里写一句天气预报，或者只在 UI 显示

    # === 3. 核心：更新数值 ===
    def _update(self, money=0, stamina=0, time=0):
        self.data["money"] -= money
        self.data["stamina"] -= stamina
        self.data["time"] += time
        self._check_game_over()
        self._check_force_sleep()
    
    def do_activity(self, act_id, money, stamina, time, name):
        # 雨天体力惩罚逻辑 (可选)
        if self.data["weather"] == "rainy" and stamina > 0:
            stamina = int(stamina * 1.2) # 雨天多耗 20% 体力
            
        self._update(money=money, stamina=stamina, time=time)
        self.data["visited_activities"].add(act_id)
        self.log(f"✨ 体验了 {name}")

    # === 4. 核心：睡觉 ===
    def sleep(self, hours=None):
        if hours:
            # 小憩
            recover = hours * 10
            self.data["stamina"] = min(100, self.data["stamina"] + recover)
            self.data["time"] += hours
            self.log(f"🛌 休息了 {hours} 小时。")
            if self.data["time"] >= 22:
                self.sleep() # 睡过头了，触发过夜
        else:
            # 过夜
            current = self.data["time"]
            if current >= 24: hours_slept = max(4, 32 - current)
            else: hours_slept = (24 - current) + 8
            
            recover = hours_slept * 15
            self.data["stamina"] = min(100, self.data["stamina"] + recover)
            self.data["day"] += 1
            self.data["time"] = 8
            self.data["hotel_settled"] = False
            
            self.log(f"💤 睡到自然醒 (第{self.data['day']}天)。")
            
            # ☀️ 新的一天，刷新天气！
            self.refresh_weather()
            
            if self.data["day"] > self.data["max_days"]:
                self.data["game_over"] = True
                self.data["fail_reason"] = "📅 签证到期，必须回国了。"

    # === 5. 核心：移动 ===
    def travel_to(self, target_city):
        start_city = self.data["city"]
        route = TRAVEL_ROUTES[start_city].get(target_city)
        
        self.data["stamina"] -= route["cost_stamina"]
        arrival = self.data["time"] + route["cost_time"]
        
        if arrival >= 22:
            self.data["day"] += 1
            self.data["time"] = 8
            self.data["hotel_settled"] = False
            self.log(f"🚌 抵达 {target_city} (过夜抵达)。")
        else:
            self.data["time"] = arrival
            self.log(f"🚌 抵达 {target_city}。")

        self.data["city"] = target_city
        
        # ☀️ 到了新城市，刷新天气！
        self.refresh_weather()
        self._check_game_over()

    def finish_game(self):
        self.data["game_over"] = True
        self.data["success"] = True
        self.data["fail_reason"] = "🎉 完美收官！带着回忆回家了。"

    def _check_game_over(self):
        if self.data["money"] < 0:
            self.data["game_over"] = True
            self.data["fail_reason"] = "💸 破产了！钱花光了。"

    def _check_force_sleep(self):
        if self.data["game_over"]: return
        if self.data["stamina"] <= 0:
            self.log("😫 累晕了，强制休息。")
            self.sleep()
        elif self.data["time"] >= 22:
            self.log("🌙 22:00 强制就寝。")
            self.sleep()

    # === Helper Methods ===
    def get_current_city_data(self): return GAME_DATA.get(self.data["city"], {})
    def get_travel_choices(self): return TRAVEL_ROUTES.get(self.data["city"], {})
    def log(self, msg): self.data["history"].insert(0, f"[Day{self.data['day']} {int(self.data['time'])}:00] {msg}")
    
    def get_hotel_options(self):
        city = self.data["city"]
        m = CITY_PRICE_MULTIPLIER.get(city, 1.0)
        return [
            {"name": "背包客栈", "price": int(300*m), "desc": "省钱首选"},
            {"name": "标准酒店", "price": int(1500*m), "desc": "舒适安全"},
            {"name": "豪华度假村", "price": int(5000*m), "desc": "奢华享受"}
        ]

game = GameState()