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

    def _get_client(self):
        user_key = st.session_state.get("user_api_key", "").strip()
        if user_key: return ZhipuAI(api_key=user_key)
        
        system_key = os.getenv("ZHIPUAI_API_KEY")
        if not system_key and hasattr(st, "secrets"):
             system_key = st.secrets.get("ZHIPUAI_API_KEY")
             
        if system_key: return ZhipuAI(api_key=system_key)
        return None

    # === 1. 天气 (不变) ===
    def get_weather_probabilities(self, city_name, month):
        cache_key = f"{city_name}_{month}"
        if cache_key in self.cache["weather_probs"]:
            return self.cache["weather_probs"][cache_key]

        client = self._get_client()
        if not client: return {"sunny": 0.7, "cloudy": 0.2, "rainy": 0.1}

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

    # === 2. 画图 (升级：支持 time_phase 细分) ===
    def generate_city_card(self, city_name, city_desc, weather, time_phase):
        """
        time_phase: "morning", "noon", "sunset", "night"
        """
        cache_key = f"{city_name}_{weather}_{time_phase}"
        if cache_key in self.cache["city_images"]:
            print(f"🎯 [缓存] 使用已有图片: {city_name}")
            return self.cache["city_images"][cache_key]

        client = self._get_client()
        if not client:
            return "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"

        print(f"🎨 [AI绘画] 正在生成: {city_name} ({time_phase})...")

        weather_prompt = {
            "sunny": "sunny day, clear blue sky",
            "cloudy": "cloudy sky, soft lighting",
            "rainy": "raining, wet streets, umbrella"
        }
        
        # 细化时间光影
        phase_prompts = {
            "morning": "early morning light, soft shadows, fresh atmosphere",
            "noon": "bright midday sun, high contrast, harsh shadows",
            "sunset": "golden hour, sunset, orange and purple sky, dramatic lighting, silhouettes",
            "night": "night time, dark sky, glowing neon lights, city lights"
        }
        
        prompt = f"""
        Anime style landscape wallpaper of {city_name}, Thailand.
        KEY FEATURES: {city_desc}. 
        ENVIRONMENT: {weather_prompt.get(weather)}, {phase_prompts.get(time_phase)}.
        Makoto Shinkai style, high resolution, masterpiece, 8k.
        No text.
        """

        try:
            try:
                response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
            except AttributeError:
                response = client.images.generations(model="cogview-3-plus", prompt=prompt)
            
            if hasattr(response, 'data'): image_url = response.data[0].url
            else: image_url = response['data'][0]['url']
            
            self.cache["city_images"][cache_key] = image_url
            return image_url

        except Exception as e:
            print(f"❌ 画图失败: {e}")
            return "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"

    # ... (结局图和音乐保持不变) ...
    def generate_ending_card(self, is_success, city_name):
        # (代码同上个版本，为了节省篇幅省略，请保留原有的逻辑)
        cache_key = f"ending_{city_name}_{is_success}"
        if cache_key in self.cache["city_images"]: return self.cache["city_images"][cache_key]
        client = self._get_client()
        if not client: return "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200"
        if is_success: prompt = f"Anime style, happy travel memories, Thailand passport, photos of {city_name}."
        else: prompt = f"Anime style, sad ending, lonely figure in {city_name}, raining."
        try:
            try: response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
            except AttributeError: response = client.images.generations(model="cogview-3-plus", prompt=prompt)
            if hasattr(response, 'data'): url = response.data[0].url
            else: url = response['data'][0]['url']
            self.cache["city_images"][cache_key] = url
            return url
        except: return "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200"

    def get_bgm(self, city_name):
        bgm_library = {
            "Bangkok": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
            "Chiang Mai": "https://cdn.pixabay.com/download/audio/2022/11/22/audio_febc508520.mp3",
            "Phuket": "https://cdn.pixabay.com/download/audio/2022/03/09/audio_822ca01d29.mp3",
            "default": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3"
        }
        return bgm_library.get(city_name, bgm_library["default"])

ai_bot = AIManager()
