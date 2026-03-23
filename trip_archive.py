import json
import uuid
from datetime import datetime
from pathlib import Path

from data_store import GAME_DATA


ARCHIVE_DIR = Path(__file__).resolve().parent / "data"
ARCHIVE_FILE = ARCHIVE_DIR / "trip_journals.json"


def _ensure_archive_file():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    if not ARCHIVE_FILE.exists():
        ARCHIVE_FILE.write_text("[]", encoding="utf-8")


def _load_archive_data():
    _ensure_archive_file()
    try:
        return json.loads(ARCHIVE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save_archive_data(items):
    _ensure_archive_file()
    ARCHIVE_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _city_name(city_code):
    return GAME_DATA.get(city_code, {}).get("name_cn", city_code)


def build_trip_journal(player, cover_image_url=""):
    route_path_codes = player.get("route_path", [])
    route_path_names = [_city_name(city) for city in route_path_codes]
    activities = []
    for city_code in route_path_codes:
        city_data = GAME_DATA.get(city_code, {})
        for activity in city_data.get("activities", []):
            if activity["id"] in player.get("visited_activities", set()):
                activities.append({"city": city_data.get("name_cn", city_code), "name": activity["name"]})

    unique_route_names = []
    for name in route_path_names:
        if not unique_route_names or unique_route_names[-1] != name:
            unique_route_names.append(name)

    outcome = "完美收官" if player.get("success") else "旅程结束"
    summary = (
        f"这趟旅程从 {route_path_names[0] if route_path_names else _city_name(player.get('city', ''))} 出发，"
        f"一共走了 {max(len(unique_route_names), 1)} 段城市节点，"
        f"打卡 {len(player.get('visited_activities', []))} 个活动，"
        f"最后以“{player.get('fail_reason', '')}”收尾。"
    )

    return {
        "id": str(uuid.uuid4()),
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "title": f"{route_path_names[0] if route_path_names else '泰国旅程'} · {outcome}",
        "route_count": max(len(unique_route_names), 1),
        "outcome": outcome,
        "cover_image_url": cover_image_url,
        "fail_reason": player.get("fail_reason", ""),
        "success": bool(player.get("success")),
        "days": player.get("day", 0),
        "max_days": player.get("max_days", 0),
        "money_left": player.get("money", 0),
        "month": player.get("month", 0),
        "final_city": _city_name(player.get("city", "")),
        "route_path": route_path_names,
        "summary": summary,
        "activity_count": len(player.get("visited_activities", [])),
        "activities": activities,
        "history": list(player.get("history", [])),
    }


def save_trip_journal(journal):
    items = _load_archive_data()
    items = [item for item in items if item.get("id") != journal["id"]]
    items.insert(0, journal)
    _save_archive_data(items)
    return journal


def list_trip_journals():
    return _load_archive_data()


def get_trip_journal(journal_id):
    for item in _load_archive_data():
        if item.get("id") == journal_id:
            return item
    return None


def delete_trip_journal(journal_id):
    items = _load_archive_data()
    new_items = [item for item in items if item.get("id") != journal_id]
    deleted = len(new_items) != len(items)
    if deleted:
        _save_archive_data(new_items)
    return deleted
