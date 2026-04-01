import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlopen

from dotenv import load_dotenv
from zhipuai import ZhipuAI


load_dotenv()


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data_store import GAME_DATA

WALLPAPER_DIR = ROOT / "wallpapers"
MANIFEST_PATH = WALLPAPER_DIR / "manifest.json"
TIME_PHASES = ["morning", "noon", "sunset", "night"]
WEATHERS = ["sunny", "cloudy", "rainy"]

DEFAULT_PROMPTS = {
    "sunny": "sunny day, clear blue sky, vibrant, dynamic shadows",
    "cloudy": "cloudy sky, soft lighting, misty atmosphere",
    "rainy": "raining, wet streets, umbrellas, strong reflections on the ground",
}

TIME_PROMPTS = {
    "morning": "early morning light, soft golden glow, fresh atmosphere",
    "noon": "bright midday sun, vivid contrast, travel postcard feeling",
    "sunset": "golden hour sunset, warm orange and coral sky, cinematic travel mood",
    "night": "night scene with lively lights, moody reflections, atmospheric travel photography",
}


def slugify(value: str) -> str:
    value = value.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def load_manifest():
    if not MANIFEST_PATH.exists():
        return {}
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def get_client():
    api_key = os.getenv("ZHIPUAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ZHIPUAI_API_KEY")
    return ZhipuAI(api_key=api_key)


def build_prompt(city_name: str, city_desc: str, weather: str, time_phase: str) -> str:
    return f"""
    Anime style travel wallpaper of {city_name}, Thailand.
    KEY FEATURES: {city_desc}.
    ENVIRONMENT: {DEFAULT_PROMPTS[weather]}, {TIME_PROMPTS[time_phase]}.
    Clean composition, no text, no watermark, cinematic, highly detailed, 8k.
    """


def generate_image_url(client, prompt: str) -> str:
    try:
        response = client.images.generations.create(model="cogview-3-plus", prompt=prompt)
    except AttributeError:
        response = client.images.generations(model="cogview-3-plus", prompt=prompt)

    if hasattr(response, "data"):
        return response.data[0].url
    return response["data"][0]["url"]


def download_image(url: str, destination: Path):
    with urlopen(url, timeout=60) as response:
        destination.write_bytes(response.read())


def main():
    client = get_client()
    WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()

    total = len(GAME_DATA) * len(WEATHERS) * len(TIME_PHASES)
    done = 0

    for city_name, city_data in GAME_DATA.items():
        city_slug = slugify(city_name)
        city_dir = WALLPAPER_DIR / city_slug
        city_dir.mkdir(parents=True, exist_ok=True)

        for weather in WEATHERS:
            for time_phase in TIME_PHASES:
                key = f"{city_name}|{weather}|{time_phase}"
                filename = f"{weather}_{time_phase}.jpg"
                destination = city_dir / filename

                if destination.exists():
                    manifest[key] = {
                        "city": city_name,
                        "weather": weather,
                        "time_phase": time_phase,
                        "path": str(destination.relative_to(ROOT)).replace("\\", "/"),
                        "generated_at": manifest.get(key, {}).get("generated_at", ""),
                    }
                    done += 1
                    print(f"[skip] {done}/{total} {key}")
                    continue

                prompt = build_prompt(city_name, city_data["description"], weather, time_phase)
                print(f"[gen ] {done + 1}/{total} {key}")
                image_url = generate_image_url(client, prompt)
                download_image(image_url, destination)
                manifest[key] = {
                    "city": city_name,
                    "weather": weather,
                    "time_phase": time_phase,
                    "path": str(destination.relative_to(ROOT)).replace("\\", "/"),
                    "source_url": image_url,
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                }
                save_manifest(manifest)
                done += 1
                time.sleep(1.2)

    print(f"Done. Generated {done}/{total} wallpapers.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Wallpaper generation failed: {exc}", file=sys.stderr)
        raise
