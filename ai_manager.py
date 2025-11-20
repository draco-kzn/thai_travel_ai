import os
import json
import streamlit as st
from zhipuai import ZhipuAI
from dotenv import load_dotenv

load_dotenv()

class AIManager:
    def __init__(self):
        self.cache = {
            "weather_probs": {}, 
            "city_images": {}
        }

    # === 🔐 核心：动态获取客户端 ===
    def _get_client(self):
        # 1. 优先检查用户是否在网页侧边栏填了 Key
        user_key = st.session_state.get("user_api_key", "").strip()
        if user_key:
            return ZhipuAI(api_key=user_key)
        
        # 2. 如果没填，尝试获取开发者预设的 Key (本地 .env 或 云端 Secrets)
        # st.secrets 是 Streamlit Cloud 专门存密钥的地方
        system_key = os.getenv("ZHIPUAI_API_KEY")
        if not system_key and hasattr(st, "secrets"):
             system_key = st.secrets.get("ZHIPUAI_API_KEY")
             
        if system_key:
            return ZhipuAI(api_key=system_key)
            
        return None

    # === 1. 天气预测 ===
    def get_weather_probabilities(self, city_name, month):
        cache_key = f"{city_name}_{month}"
        if cache_key in self.cache["weather_probs"]:
            return self.cache["weather_probs"][cache_key]

        client = self._get_client()
        if not client:
            # 既没填Key，系统Key也挂了，直接兜底
            return {"sunny": 0.7, "cloudy": 0.2, "rainy": 0.1}

        prompt = f"""
        判断泰国城市 {city_name} 在 {month} 月份的天气概率。
        Strict JSON format only: {{"sunny": 0.6, "cloudy": 0.3, "rainy": 0.1}}
        """
        try:
            response = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except:
            return {"sunny": 0.6, "cloudy": 0.3, "rainy": 0.1}

    # === 2. 画图 ===
    def generate_city_card(self, city_name, city_desc, weather, time_of_day="day"):
        cache_key = f"{city_name}_{weather}_{time_of_day}"
        if cache_key in self.cache["city_images"]:
            print(f"🎯 [缓存] 使用已有图片: {city_name}")
            return self.cache["city_images"][cache_key]

        client = self._get_client()
        if not client:
            print("⚠️ 未检测到任何 API Key，使用兜底图")
            return "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"

        print(f"🎨 [AI绘画] 正在生成: {city_name}...")

        weather_prompt = {
            "sunny": "sunny day, clear blue sky",
            "cloudy": "cloudy sky, soft lighting",
            "rainy": "raining, wet streets, umbrella"
        }
        time_prompt = "daytime" if time_of_day == "day" else "night time, neon lights"
        
        prompt = f"""
        Anime style landscape wallpaper of {city_name}, Thailand.
        KEY FEATURES: {city_desc}. 
        ENVIRONMENT: {weather_prompt.get(weather)}, {time_prompt}.
        Makoto Shinkai style, high resolution, masterpiece, 8k.
        No text.
        """

        try:
            # 兼容性调用
            try:
                response = client.images.generations.create(
                    model="cogview-3-plus",
                    prompt=prompt
                )
            except AttributeError:
                response = client.images.generations(
                    model="cogview-3-plus",
                    prompt=prompt
                )
            
            if hasattr(response, 'data'): image_url = response.data[0].url
            else: image_url = response['data'][0]['url']
            
            self.cache["city_images"][cache_key] = image_url
            return image_url

        except Exception as e:
            print(f"❌ 画图失败: {e}")
            # 如果是用户填了Key但没钱了，或者你的Key没钱了
            return "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"

    # === 3. 结局图 ===
    def generate_ending_card(self, is_success, city_name):
        cache_key = f"ending_{city_name}_{is_success}"
        if cache_key in self.cache["city_images"]: return self.cache["city_images"][cache_key]
        
        client = self._get_client()
        if not client: return "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200"

        if is_success:
            prompt = f"Anime style, happy travel memories, Thailand passport, photos of {city_name}, warm light."
        else:
            prompt = f"Anime style, sad ending, lonely figure in {city_name}, raining, empty wallet."

        try:
            try:
                response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
            except AttributeError:
                response = client.images.generations(model="cogview-3-plus", prompt=prompt)
            
            if hasattr(response, 'data'): url = response.data[0].url
            else: url = response['data'][0]['url']
            
            self.cache["city_images"][cache_key] = url
            return url
        except:
            return "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200"

    # === 4. 音乐 (不变) ===
    def get_bgm(self, city_name):
        bgm_library = {
            "Bangkok": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
            "Chiang Mai": "https://cdn.pixabay.com/download/audio/2022/11/22/audio_febc508520.mp3",
            "Phuket": "https://cdn.pixabay.com/download/audio/2022/03/09/audio_822ca01d29.mp3",
            "default": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3"
        }
        return bgm_library.get(city_name, bgm_library["default"])

ai_bot = AIManager()