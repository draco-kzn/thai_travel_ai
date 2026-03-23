import os
import json
import streamlit as st
from zhipuai import ZhipuAI
from dotenv import load_dotenv

load_dotenv()

# --- 核心辅助函数：获取 ZhipuAI Client ---
# 独立为函数，便于在 st.cache_data 修饰的函数中调用
def get_zhipu_client():
    """从 session_state、.env 或 secrets 中安全获取 ZhipuAI 客户端。"""
    # 1. 优先读取用户填写的 Key
    user_key = st.session_state.get("user_api_key", "").strip()
    if user_key:
        return ZhipuAI(api_key=user_key)
    
    # 2. 读取系统预设的 Key (本地 .env 或 Streamlit Secrets)
    system_key = os.getenv("ZHIPUAI_API_KEY")
    if not system_key and hasattr(st, "secrets"):
        system_key = st.secrets.get("ZHIPUAI_API_KEY")
            
    if system_key:
        return ZhipuAI(api_key=system_key)
        
    return None

class AIManager:
    # AIManager 类现在主要作为一个封装所有 AI 服务的容器。
    # 所有对外服务的方法都使用 Streamlit 缓存。

    # === 1. 天气预测 (使用 st.cache_data 缓存 1 小时) ===
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def get_weather_probabilities(city_name: str, month: int):
        """获取指定城市和月份的天气概率，缓存 1 小时。"""
        client = get_zhipu_client()
        # 无 Key 时的默认返回值
        if not client: 
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
            # 安全解析 JSON (从代码块中提取)
            content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            print(f"❌ 天气预测失败: {e}")
            return {"sunny": 0.6, "cloudy": 0.3, "rainy": 0.1}

    # === 2. AI 画图 (使用 st.cache_data 永久硬盘缓存) ===
    @staticmethod
    @st.cache_data(persist="disk", show_spinner=False)
    def generate_city_card(city_name: str, city_desc: str, weather: str, time_phase: str):
        """根据城市、天气和时间生成图片 URL，结果永久缓存。"""
        client = get_zhipu_client()
        default_image = "https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?q=80&w=1200"
        if not client: 
            return default_image

        print(f"🎨 [AI绘画] 新生成: {city_name} ({time_phase})...")

        # 结合 B 版优化后的 Prompt 细节
        weather_prompt = {
            "sunny": "sunny day, clear blue sky, vibrant, dynamic shadows",
            "cloudy": "cloudy sky, soft lighting, misty atmosphere",
            "rainy": "raining, wet streets, umbrella, strong reflections on the pavement"
        }
        time_prompt = {
            "morning": "early morning light, soft golden glow, fresh atmosphere",
            "noon": "bright midday sun, high contrast, vivid colors",
            "sunset": "golden hour sunset, orange and purple sky, dramatic lighting, epic view",
            "night": "night time, cyberpunk neon lights, glowing city signs, dark sky"
        }
        
        prompt = f"""
        Anime style landscape wallpaper of {city_name}, Thailand.
        KEY FEATURES: {city_desc}. 
        ENVIRONMENT: {weather_prompt.get(weather)}, {time_prompt.get(time_phase, 'day')}.
        Makoto Shinkai style, high resolution, masterpiece, 8k, wide angle.
        No text, no watermarks.
        """

        try:
            # 兼容性调用 (新旧 SDK 通吃)
            try: 
                response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
            except AttributeError: 
                # 旧版 SDK 兼容
                response = client.images.generations(model="cogview-3-plus", prompt=prompt)
            
            # 兼容性获取 URL
            if hasattr(response, 'data'): 
                return response.data[0].url
            else: 
                return response['data'][0]['url']
                
        except Exception as e:
            print(f"❌ 画图失败: {e}")
            return default_image

    # === 3. 结局图 (永久缓存，更优化的 Prompt) ===
    @staticmethod
    @st.cache_data(persist="disk", show_spinner=False)
    def generate_ending_card(is_success: bool, city_name: str):
        """生成旅行结局图，永久缓存。"""
        client = get_zhipu_client()
        default_image = "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?q=80&w=1200"
        if not client: 
            return default_image
        
        # 采用 B 版优化后的更细致的 Prompt
        if is_success: 
            prompt = f"Anime style, happy travel memories, Thailand passport, sunglasses, photos of {city_name} on wooden table, warm sunset light, cozy atmosphere, perfect journey."
        else: 
            prompt = f"Anime style, sad ending, lonely figure sitting on a bench in {city_name}, raining, holding empty wallet, melancholic, washed out colors."

        try:
            # 兼容性调用
            try: 
                response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
            except AttributeError: 
                response = client.images.generations(model="cogview-3-plus", prompt=prompt)
            
            if hasattr(response, 'data'): 
                return response.data[0].url
            else: 
                return response['data'][0]['url']
        except: 
            return default_image

    # === 4. BGM (静态，无需缓存) ===
    # 作为一个实例方法，可以被外部像普通方法一样调用，或者改为静态方法。
    def get_bgm(self, city_name: str):
        """返回城市对应的背景音乐 URL。"""
        bgm_library = {
            "Bangkok": "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3",
            "Chiang Mai": "https://cdn.pixabay.com/download/audio/2022/11/22/audio_febc508520.mp3",
            "Phuket": "https://cdn.pixabay.com/download/audio/2022/03/09/audio_822ca01d29.mp3",
            "default": "https://cdn.pixabay.com/download/audio/2022/01/18/audio_d0a13f69d2.mp3"
        }
        return bgm_library.get(city_name, bgm_library["default"])

ai_bot = AIManager()
