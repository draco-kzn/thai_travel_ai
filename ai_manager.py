import json
import os
import re

import streamlit as st
from dotenv import load_dotenv
from zhipuai import ZhipuAI


load_dotenv()

DEFAULT_WEATHER_PROBS = {"sunny": 0.6, "cloudy": 0.3, "rainy": 0.1}
DEFAULT_CITY_IMAGE = "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"
DEFAULT_ENDING_IMAGE = "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200"


def get_zhipu_client():
    user_key = st.session_state.get("user_api_key", "").strip()
    if user_key:
        return ZhipuAI(api_key=user_key)

    system_key = os.getenv("ZHIPUAI_API_KEY")
    if not system_key and hasattr(st, "secrets"):
        system_key = st.secrets.get("ZHIPUAI_API_KEY")

    if system_key:
        return ZhipuAI(api_key=system_key)

    return None


def _extract_json_object(raw_text):
    if not isinstance(raw_text, str):
        return None

    content = raw_text.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return None

        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None


def _normalize_weather_probs(payload):
    if not isinstance(payload, dict):
        return DEFAULT_WEATHER_PROBS.copy()

    normalized = {}
    total = 0.0
    for key, fallback in DEFAULT_WEATHER_PROBS.items():
        try:
            value = float(payload.get(key, fallback))
        except (TypeError, ValueError):
            value = fallback
        value = max(value, 0.0)
        normalized[key] = value
        total += value

    if total <= 0:
        return DEFAULT_WEATHER_PROBS.copy()

    return {key: value / total for key, value in normalized.items()}


class AIManager:
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_weather_probabilities(city_name: str, month: int):
        client = get_zhipu_client()
        if not client:
            return DEFAULT_WEATHER_PROBS.copy()

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
            content = response.choices[0].message.content
            parsed = _extract_json_object(content)
            return _normalize_weather_probs(parsed)
        except Exception as exc:
            print(f"天气预测失败: {exc}")
            return DEFAULT_WEATHER_PROBS.copy()

    @staticmethod
    @st.cache_data(persist="disk", show_spinner=False)
    def generate_city_card(city_name: str, city_desc: str, weather: str, time_phase: str):
        client = get_zhipu_client()
        if not client:
            return DEFAULT_CITY_IMAGE

        weather_prompt = {
            "sunny": "sunny day, clear blue sky, vibrant, dynamic shadows",
            "cloudy": "cloudy sky, soft lighting, misty atmosphere",
            "rainy": "raining, wet streets, umbrella, strong reflections on the pavement",
        }
        time_prompt = {
            "morning": "early morning light, soft golden glow, fresh atmosphere",
            "noon": "bright midday sun, high contrast, vivid colors",
            "sunset": "golden hour sunset, orange and purple sky, dramatic lighting, epic view",
            "night": "night time, cyberpunk neon lights, glowing city signs, dark sky",
        }

        prompt = f"""
        Anime style landscape wallpaper of {city_name}, Thailand.
        KEY FEATURES: {city_desc}.
        ENVIRONMENT: {weather_prompt.get(weather)}, {time_prompt.get(time_phase, 'day')}.
        Makoto Shinkai style, high resolution, masterpiece, 8k, wide angle.
        No text, no watermarks.
        """

        try:
            try:
                response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
            except AttributeError:
                response = client.images.generations(model="cogview-3-plus", prompt=prompt)

            if hasattr(response, "data"):
                return response.data[0].url
            return response["data"][0]["url"]
        except Exception as exc:
            print(f"生成城市图片失败: {exc}")
            return DEFAULT_CITY_IMAGE

    @staticmethod
    @st.cache_data(persist="disk", show_spinner=False)
    def generate_ending_card(is_success: bool, city_name: str):
        client = get_zhipu_client()
        if not client:
            return DEFAULT_ENDING_IMAGE

        if is_success:
            prompt = (
                f"Anime style, happy travel memories, Thailand passport, sunglasses, photos of "
                f"{city_name} on wooden table, warm sunset light, cozy atmosphere, perfect journey."
            )
        else:
            prompt = (
                f"Anime style, sad ending, lonely figure sitting on a bench in {city_name}, "
                "raining, holding empty wallet, melancholic, washed out colors."
            )

        try:
            try:
                response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
            except AttributeError:
                response = client.images.generations(model="cogview-3-plus", prompt=prompt)

            if hasattr(response, "data"):
                return response.data[0].url
            return response["data"][0]["url"]
        except Exception as exc:
            print(f"生成结局图片失败: {exc}")
            return DEFAULT_ENDING_IMAGE

    def get_bgm(self, city_name: str, time_phase: str = "noon"):
        bgm_library = {
            "Bangkok": {
                "day": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
            },
            "Chiang Mai": {
                "day": "https://cdn.pixabay.com/download/audio/2022/11/22/audio_febc508520.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2021/06/07/audio_cdfb955189.mp3",
            },
            "Pattaya": {
                "day": "https://cdn.pixabay.com/download/audio/2022/03/15/audio_12a79df404.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2025/02/19/audio_99d82c4799.mp3",
            },
            "Hua Hin": {
                "day": "https://cdn.pixabay.com/download/audio/2021/06/07/audio_cdfb955189.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2021/10/23/audio_fa974e579a.mp3",
            },
            "Phuket": {
                "day": "https://cdn.pixabay.com/download/audio/2022/03/09/audio_822ca01d29.mp3",
                "sunset": "https://cdn.pixabay.com/download/audio/2024/10/23/audio_5621af6dd3.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2025/02/19/audio_99d82c4799.mp3",
            },
            "Krabi": {
                "day": "https://cdn.pixabay.com/download/audio/2022/03/09/audio_eb16546260.mp3",
                "sunset": "https://cdn.pixabay.com/download/audio/2021/10/23/audio_fa974e579a.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2021/06/07/audio_cdfb955189.mp3",
            },
            "Koh Samui": {
                "day": "https://cdn.pixabay.com/download/audio/2025/02/19/audio_99d82c4799.mp3",
                "sunset": "https://cdn.pixabay.com/download/audio/2024/10/23/audio_5621af6dd3.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
            },
            "Phi Phi Islands": {
                "day": "https://cdn.pixabay.com/download/audio/2024/10/23/audio_5621af6dd3.mp3",
                "sunset": "https://cdn.pixabay.com/download/audio/2021/10/23/audio_fa974e579a.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
            },
            "Koh Lanta": {
                "day": "https://cdn.pixabay.com/download/audio/2021/10/23/audio_fa974e579a.mp3",
                "sunset": "https://cdn.pixabay.com/download/audio/2024/10/23/audio_5621af6dd3.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2021/06/07/audio_cdfb955189.mp3",
            },
            "Koh Lipe": {
                "day": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
                "sunset": "https://cdn.pixabay.com/download/audio/2024/10/23/audio_5621af6dd3.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2025/02/19/audio_99d82c4799.mp3",
            },
            "default": {
                "day": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3",
                "night": "https://cdn.pixabay.com/download/audio/2021/06/07/audio_cdfb955189.mp3",
            },
        }
        city_tracks = bgm_library.get(city_name, bgm_library["default"])
        if time_phase in city_tracks:
            return city_tracks[time_phase]
        if time_phase in {"morning", "noon"} and "day" in city_tracks:
            return city_tracks["day"]
        if time_phase == "sunset" and "sunset" in city_tracks:
            return city_tracks["sunset"]
        if time_phase == "night" and "night" in city_tracks:
            return city_tracks["night"]
        return city_tracks.get("day") or city_tracks.get("night") or bgm_library["default"]["day"]


ai_bot = AIManager()
