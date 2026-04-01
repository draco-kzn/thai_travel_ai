import json
import os
import re
import base64
from urllib.parse import quote
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from zhipuai import ZhipuAI


load_dotenv()

DEFAULT_WEATHER_PROBS = {"sunny": 0.6, "cloudy": 0.3, "rainy": 0.1}
DEFAULT_CITY_IMAGE = "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"
DEFAULT_ENDING_IMAGE = "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200"
ROOT_DIR = Path(__file__).resolve().parent
WALLPAPER_MANIFEST_PATH = ROOT_DIR / "wallpapers" / "manifest.json"
CITY_FALLBACK_ART = {
    "Bangkok": {
        "palette": ("#ffd8a8", "#ff9f6e", "#2f6690", "#173753"),
        "silhouette": "<path d='M130 470 L180 240 L220 470 Z M230 470 L275 180 L315 470 Z M325 470 L370 220 L410 470 Z M420 470 L520 470 L520 390 L560 390 L560 470 L720 470 L720 360 L770 360 L770 470 L870 470 L870 330 L930 330 L930 470 Z' fill='{land}' opacity='0.96'/>",
    },
    "Chiang Mai": {
        "palette": ("#ffe4b5", "#f7b267", "#4f772d", "#31572c"),
        "silhouette": "<path d='M0 470 L150 280 L280 470 Z M200 470 L360 220 L520 470 Z M420 470 L610 250 L820 470 Z M730 470 L920 300 L1100 470 Z' fill='{land}' opacity='0.96'/><path d='M470 470 L520 250 L560 470 Z' fill='{accent}' opacity='0.85'/>",
    },
    "Pattaya": {
        "palette": ("#ffe2b8", "#ffad84", "#56cfe1", "#22577a"),
        "silhouette": "<path d='M0 470 L180 470 L180 390 L240 390 L240 470 L360 470 L360 350 L430 350 L430 470 L520 470 L520 310 L600 310 L600 470 L760 470 L760 360 L820 360 L820 470 L1100 470 Z' fill='{land}' opacity='0.94'/><circle cx='720' cy='230' r='48' fill='{accent}' opacity='0.32'/>",
    },
    "Hua Hin": {
        "palette": ("#fff0d9", "#f3c892", "#8ecae6", "#457b9d"),
        "silhouette": "<path d='M0 470 L260 470 L260 400 L320 400 L320 470 L430 470 L430 350 L490 350 L490 470 L620 470 L620 410 L760 410 L760 470 L1100 470 Z' fill='{land}' opacity='0.9'/><path d='M300 350 L400 260 L500 350 Z' fill='{accent}' opacity='0.72'/>",
    },
    "Phuket": {
        "palette": ("#ffe3bf", "#ffad66", "#4cc9f0", "#1d3557"),
        "silhouette": "<path d='M0 470 L180 470 L270 280 L360 470 Z M320 470 L470 180 L650 470 Z M620 470 L760 250 L940 470 Z M860 470 L980 320 L1100 470 Z' fill='{land}' opacity='0.95'/>",
    },
    "Krabi": {
        "palette": ("#ffe0bd", "#f4a261", "#48bfe3", "#264653"),
        "silhouette": "<path d='M0 470 L180 470 L280 260 L340 470 Z M260 470 L420 160 L520 470 Z M480 470 L680 210 L760 470 Z M700 470 L930 140 L1020 470 Z' fill='{land}' opacity='0.96'/>",
    },
    "Koh Samui": {
        "palette": ("#fff0d9", "#f7c873", "#72ddf7", "#2a9d8f"),
        "silhouette": "<path d='M0 470 L1100 470 L1100 420 Q980 360 860 410 T620 410 T360 400 T0 420 Z' fill='{land}' opacity='0.9'/><path d='M220 470 L250 350 L280 470 Z M680 470 L710 340 L740 470 Z' fill='{accent}' opacity='0.85'/>",
    },
    "Phi Phi Islands": {
        "palette": ("#ffe7c2", "#ffb26b", "#64dfdf", "#22577a"),
        "silhouette": "<path d='M0 470 L210 470 L320 220 L400 470 Z M360 470 L560 130 L690 470 Z M650 470 L850 190 L980 470 Z' fill='{land}' opacity='0.96'/><path d='M140 470 L230 420 L320 470 Z' fill='{accent}' opacity='0.72'/>",
    },
    "Koh Lanta": {
        "palette": ("#ffefd5", "#f7b267", "#72efdd", "#2b2d42"),
        "silhouette": "<path d='M0 470 L1100 470 L1100 430 Q920 380 780 420 T500 420 T250 410 T0 430 Z' fill='{land}' opacity='0.92'/><rect x='760' y='300' width='18' height='120' rx='6' fill='{accent}' opacity='0.88'/><polygon points='730,330 810,330 770,270' fill='{accent}' opacity='0.88'/>",
    },
    "Koh Lipe": {
        "palette": ("#fff3d6", "#ffc971", "#80ed99", "#3a86ff"),
        "silhouette": "<path d='M0 470 L1100 470 L1100 430 Q980 390 860 430 T600 425 T320 420 T0 430 Z' fill='{land}' opacity='0.9'/><path d='M90 420 Q150 380 210 420' stroke='{accent}' stroke-width='10' fill='none' opacity='0.82'/>",
    },
}


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


def get_city_fallback_image(city_name: str, weather: str = "sunny", time_phase: str = "noon"):
    art = CITY_FALLBACK_ART.get(city_name)
    if not art:
        return DEFAULT_CITY_IMAGE

    sky_by_time = {
        "morning": ("#ffe8c2", "#b8ecff"),
        "noon": ("#bfe8ff", "#6dc9ff"),
        "sunset": ("#ffd0b5", "#ff8f6b"),
        "night": ("#102542", "#1b4965"),
    }
    sky_top, sky_bottom = sky_by_time.get(time_phase, sky_by_time["noon"])
    if weather == "cloudy":
        sky_top, sky_bottom = "#dde7ef", "#8aa1b1"
    elif weather == "rainy":
        sky_top, sky_bottom = "#91a7b8", "#52606d"

    sea_by_weather = {
        "sunny": "#6ed3cf",
        "cloudy": "#78a6b8",
        "rainy": "#507284",
    }
    sea = sea_by_weather.get(weather, "#6ed3cf")
    land, accent = art["palette"][2], art["palette"][1]
    if time_phase == "night":
        land = art["palette"][3]
        accent = "#c8d9ff"

    weather_layer = ""
    if weather == "sunny":
        weather_layer = "<circle cx='860' cy='110' r='52' fill='#ffe27a' opacity='0.9'/>"
    elif weather == "cloudy":
        weather_layer = "<g fill='#f1f5f9' opacity='0.9'><ellipse cx='770' cy='120' rx='62' ry='24'/><ellipse cx='825' cy='105' rx='48' ry='22'/><ellipse cx='880' cy='122' rx='58' ry='26'/></g>"
    elif weather == "rainy":
        weather_layer = (
            "<g fill='#d8e2ea' opacity='0.88'><ellipse cx='780' cy='118' rx='74' ry='26'/><ellipse cx='850' cy='108' rx='52' ry='24'/>"
            "<ellipse cx='915' cy='122' rx='64' ry='28'/></g>"
            "<g stroke='#d7efff' stroke-width='3' opacity='0.55'>"
            "<line x1='720' y1='150' x2='700' y2='220'/><line x1='760' y1='150' x2='740' y2='220'/>"
            "<line x1='800' y1='150' x2='780' y2='220'/><line x1='840' y1='150' x2='820' y2='220'/>"
            "<line x1='880' y1='150' x2='860' y2='220'/><line x1='920' y1='150' x2='900' y2='220'/></g>"
        )

    silhouette = art["silhouette"].format(land=land, accent=accent)
    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1100 620'>
        <defs>
            <linearGradient id='sky' x1='0' y1='0' x2='0' y2='1'>
                <stop offset='0%' stop-color='{sky_top}'/>
                <stop offset='100%' stop-color='{sky_bottom}'/>
            </linearGradient>
            <linearGradient id='sea' x1='0' y1='0' x2='0' y2='1'>
                <stop offset='0%' stop-color='{sea}'/>
                <stop offset='100%' stop-color='#1d4f68'/>
            </linearGradient>
        </defs>
        <rect width='1100' height='620' fill='url(#sky)'/>
        {weather_layer}
        <rect y='360' width='1100' height='260' fill='url(#sea)' opacity='0.96'/>
        <rect y='338' width='1100' height='18' fill='rgba(255,255,255,0.2)' opacity='0.35'/>
        {silhouette}
        <path d='M0 470 Q180 450 340 470 T700 470 T1100 470 V620 H0 Z' fill='rgba(255,255,255,0.08)'/>
    </svg>
    """
    return f"data:image/svg+xml;utf8,{quote(svg)}"


def _load_wallpaper_manifest():
    if not WALLPAPER_MANIFEST_PATH.exists():
        return {}
    try:
        return json.loads(WALLPAPER_MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def get_local_wallpaper_image(city_name: str, weather: str, time_phase: str):
    key = f"{city_name}|{weather}|{time_phase}"
    manifest = _load_wallpaper_manifest()
    item = manifest.get(key)
    if not item:
        return None

    relative_path = item.get("path")
    if not relative_path:
        return None

    file_path = ROOT_DIR / relative_path
    if not file_path.exists():
        return None

    suffix = file_path.suffix.lower()
    mime_type = "image/jpeg"
    if suffix == ".png":
        mime_type = "image/png"
    elif suffix == ".webp":
        mime_type = "image/webp"

    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


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
        local_wallpaper = get_local_wallpaper_image(city_name, weather, time_phase)
        if local_wallpaper:
            return local_wallpaper

        client = get_zhipu_client()
        fallback_image = get_city_fallback_image(city_name, weather, time_phase)
        if not client:
            return fallback_image

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
            return fallback_image

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
