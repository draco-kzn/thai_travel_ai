import json
import os
import re
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st

from data_store import GAME_DATA, TRAVEL_ROUTES


AMADEUS_TEST_BASE_URL = "https://test.api.amadeus.com"
DEFAULT_TIMEOUT_SECONDS = 20

CITY_REALTIME_META = {
    "Bangkok": {
        "airport_code": "BKK",
        "airport_label": "Bangkok Suvarnabhumi",
        "hotel_label": "Bangkok",
        "lat": 13.7563,
        "lng": 100.5018,
        "flight_note": "使用曼谷素万那普机场作为实时航班参考。",
        "has_airport": True,
        "gateway_airports": ["BKK"],
    },
    "Chiang Mai": {
        "airport_code": "CNX",
        "airport_label": "Chiang Mai International",
        "hotel_label": "Chiang Mai",
        "lat": 18.7883,
        "lng": 98.9853,
        "flight_note": "使用清迈国际机场作为实时航班参考。",
        "has_airport": True,
        "gateway_airports": ["CNX"],
    },
    "Pattaya": {
        "airport_code": "UTP",
        "airport_label": "U-Tapao / Pattaya",
        "hotel_label": "Pattaya",
        "lat": 12.9236,
        "lng": 100.8825,
        "flight_note": "使用乌塔堡机场近似 Pattaya 的实时机票。",
        "has_airport": True,
        "gateway_airports": ["UTP"],
    },
    "Hua Hin": {
        "airport_code": "BKK",
        "airport_label": "Bangkok gateway",
        "hotel_label": "Hua Hin",
        "lat": 12.5684,
        "lng": 99.9577,
        "flight_note": "华欣在玩法里按曼谷网关处理，更接近真实旅行里“先回曼谷再飞”的逻辑。",
        "has_airport": False,
        "gateway_airports": ["BKK"],
    },
    "Phuket": {
        "airport_code": "HKT",
        "airport_label": "Phuket International",
        "hotel_label": "Phuket",
        "lat": 7.8804,
        "lng": 98.3923,
        "flight_note": "使用普吉国际机场作为实时航班参考。",
        "has_airport": True,
        "gateway_airports": ["HKT"],
    },
    "Krabi": {
        "airport_code": "KBV",
        "airport_label": "Krabi International",
        "hotel_label": "Krabi",
        "lat": 8.0863,
        "lng": 98.9063,
        "flight_note": "使用甲米国际机场作为实时航班参考。",
        "has_airport": True,
        "gateway_airports": ["KBV"],
    },
    "Koh Samui": {
        "airport_code": "USM",
        "airport_label": "Samui International",
        "hotel_label": "Koh Samui",
        "lat": 9.5120,
        "lng": 100.0136,
        "flight_note": "使用苏梅国际机场作为实时航班参考。",
        "has_airport": True,
        "gateway_airports": ["USM"],
    },
    "Phi Phi Islands": {
        "airport_code": "HKT",
        "airport_label": "Phuket gateway",
        "hotel_label": "Phi Phi Islands",
        "lat": 7.7407,
        "lng": 98.7784,
        "flight_note": "机票只查询到进出网关，岛上最终仍需船运。",
        "has_airport": False,
        "gateway_airports": ["HKT", "KBV"],
    },
    "Koh Lanta": {
        "airport_code": "KBV",
        "airport_label": "Krabi gateway",
        "hotel_label": "Koh Lanta",
        "lat": 7.6142,
        "lng": 99.0367,
        "flight_note": "机票只查询到进出网关，落地后通常还要地面接驳或船。",
        "has_airport": False,
        "gateway_airports": ["KBV"],
    },
    "Koh Lipe": {
        "airport_code": "HDY",
        "airport_label": "Hat Yai gateway",
        "hotel_label": "Koh Lipe",
        "lat": 6.4880,
        "lng": 99.3042,
        "flight_note": "机票只查询到合艾网关，最终上岛仍需车船联运。",
        "has_airport": False,
        "gateway_airports": ["HDY"],
    },
}


def has_amadeus_credentials():
    return bool(os.getenv("AMADEUS_API_KEY") and os.getenv("AMADEUS_API_SECRET"))


def get_city_realtime_meta(city_name):
    return CITY_REALTIME_META.get(city_name)


def route_has_flight_component(origin_city, destination_city):
    mode = TRAVEL_ROUTES.get(origin_city, {}).get(destination_city, {}).get("mode", "")
    return any(keyword in mode for keyword in ("飞机", "航班", "直飞", "飞到", "转机"))


def build_realtime_flight_plan(origin_city, destination_city):
    origin_meta = get_city_realtime_meta(origin_city)
    destination_meta = get_city_realtime_meta(destination_city)
    if not origin_meta or not destination_meta:
        return {
            "kind": "unavailable",
            "queryable": False,
            "title": "当前路线缺少实时机场映射。",
            "notes": [],
        }

    route_mode = TRAVEL_ROUTES.get(origin_city, {}).get(destination_city, {}).get("mode", "")
    if not route_has_flight_component(origin_city, destination_city):
        return {
            "kind": "surface_only",
            "queryable": False,
            "title": "这条路线主要依赖陆路或船运，不适合查机票。",
            "notes": [
                f"当前模拟路线：{route_mode}",
                "这类路线更接近渡轮、快艇、巴士或联运接驳，而不是独立航班。",
            ],
        }

    origin_gateway = origin_meta["gateway_airports"][0]
    destination_gateway = destination_meta["gateway_airports"][0]
    notes = []

    if not origin_meta["has_airport"]:
        notes.append(
            f"{GAME_DATA[origin_city]['name_cn']} 本身没有机场，实际需要先接驳到 {origin_meta['airport_label']}。"
        )
    if not destination_meta["has_airport"]:
        notes.append(
            f"{GAME_DATA[destination_city]['name_cn']} 本身没有机场，机票只查到 {destination_meta['airport_label']}，落地后仍需船或地面接驳。"
        )
        extra_gateways = destination_meta["gateway_airports"][1:]
        if extra_gateways:
            notes.append(f"可替代网关还包括：{', '.join(extra_gateways)}。当前默认展示 {destination_gateway}。")

    if origin_gateway == destination_gateway and (not origin_meta["has_airport"] or not destination_meta["has_airport"]):
        notes.append(f"当前路段的共同网关是 {origin_gateway}。")
        notes.append("例如 Phi Phi ↔ Phuket、Phi Phi ↔ Krabi 这类路线，通常应该看船班或联运，而不是机票。")
        return {
            "kind": "same_gateway_surface",
            "queryable": False,
            "title": "这条路线没有独立的有效航班段，主要是船运或同网关接驳。",
            "notes": notes,
        }

    if origin_meta["has_airport"] and destination_meta["has_airport"]:
        title = f"实时机票将查询 {origin_meta['airport_label']} -> {destination_meta['airport_label']}"
        kind = "direct_flight"
    else:
        title = f"实时机票将查询网关航段 {origin_meta['airport_label']} -> {destination_meta['airport_label']}"
        kind = "gateway_flight"

    return {
        "kind": kind,
        "queryable": True,
        "title": title,
        "origin_code": origin_gateway,
        "destination_code": destination_gateway,
        "origin_label": origin_meta["airport_label"],
        "destination_label": destination_meta["airport_label"],
        "route_mode": route_mode,
        "notes": notes,
    }


def infer_trip_date(start_month, trip_day, today=None):
    today = today or date.today()
    year = today.year if start_month >= today.month else today.year + 1
    anchor = date(year, start_month, 1)
    return anchor + timedelta(days=max(trip_day - 1, 0))


def infer_hotel_dates(player):
    check_in = infer_trip_date(player["month"], player["day"])
    check_out = check_in + timedelta(days=1)
    return check_in, check_out


def format_date_for_api(value):
    return value.isoformat()


def _get_amadeus_base_url():
    return os.getenv("AMADEUS_BASE_URL", AMADEUS_TEST_BASE_URL).rstrip("/")


def _request_json(url, method="GET", headers=None, body=None):
    request = Request(url, method=method)
    for key, value in (headers or {}).items():
        request.add_header(key, value)

    payload = body.encode("utf-8") if isinstance(body, str) else body
    with urlopen(request, data=payload, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


@st.cache_data(ttl=1500, show_spinner=False)
def get_amadeus_access_token():
    api_key = os.getenv("AMADEUS_API_KEY")
    api_secret = os.getenv("AMADEUS_API_SECRET")
    if not api_key or not api_secret:
        return None

    body = urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": api_secret,
        }
    )
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = _request_json(
        f"{_get_amadeus_base_url()}/v1/security/oauth2/token",
        method="POST",
        headers=headers,
        body=body,
    )
    return data.get("access_token")


def _authorized_get(path, query):
    token = get_amadeus_access_token()
    if not token:
        raise RuntimeError("Missing Amadeus credentials")

    url = f"{_get_amadeus_base_url()}{path}?{urlencode(query, doseq=True)}"
    return _request_json(url, headers={"Authorization": f"Bearer {token}"})


def _safe_api_call(func):
    try:
        return {"ok": True, "data": func(), "error": ""}
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        return {"ok": False, "data": [], "error": f"HTTP {exc.code}: {detail[:240]}"}
    except URLError as exc:
        return {"ok": False, "data": [], "error": f"Network error: {exc.reason}"}
    except Exception as exc:
        return {"ok": False, "data": [], "error": str(exc)}


def _format_flight_offer(raw_offer):
    first_segment = raw_offer["itineraries"][0]["segments"][0]
    last_segment = raw_offer["itineraries"][0]["segments"][-1]
    validating = raw_offer.get("validatingAirlineCodes") or []
    duration = raw_offer["itineraries"][0].get("duration", "")

    return {
        "price": raw_offer["price"]["total"],
        "currency": raw_offer["price"]["currency"],
        "carrier": ",".join(validating) if validating else first_segment.get("carrierCode", "-"),
        "departure": first_segment["departure"]["at"],
        "arrival": last_segment["arrival"]["at"],
        "stops": max(len(raw_offer["itineraries"][0]["segments"]) - 1, 0),
        "duration": duration,
        "duration_minutes": _parse_iso_duration_to_minutes(duration),
        "source": raw_offer.get("source", ""),
    }


def _parse_iso_duration_to_minutes(duration):
    if not duration:
        return 10**9

    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration)
    if not match:
        return 10**9

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    return hours * 60 + minutes


@st.cache_data(ttl=900, show_spinner=False)
def search_live_flights(origin_code, destination_code, departure_date, adults=1, max_results=3):
    def _call():
        payload = _authorized_get(
            "/v2/shopping/flight-offers",
            {
                "originLocationCode": origin_code,
                "destinationLocationCode": destination_code,
                "departureDate": departure_date,
                "adults": adults,
                "max": max_results,
                "currencyCode": "THB",
            },
        )
        return [_format_flight_offer(item) for item in payload.get("data", [])[:max_results]]

    return _safe_api_call(_call)


def _format_hotel_offer(hotel_item):
    hotel = hotel_item.get("hotel", {})
    offers = hotel_item.get("offers") or []
    offer = offers[0] if offers else {}
    price = offer.get("price", {})

    return {
        "hotel_name": hotel.get("name", "Unknown hotel"),
        "hotel_id": hotel.get("hotelId", ""),
        "room_type": offer.get("room", {}).get("typeEstimated", {}).get("category", "Room"),
        "board_type": offer.get("boardType", ""),
        "price": price.get("total") or price.get("sellingTotal") or "-",
        "currency": price.get("currency", "THB"),
        "check_in": offer.get("checkInDate", ""),
        "check_out": offer.get("checkOutDate", ""),
    }


@st.cache_data(ttl=1800, show_spinner=False)
def search_live_hotels(city_name, latitude, longitude, check_in_date, check_out_date, adults=1, max_hotels=6):
    def _call():
        hotel_list = _authorized_get(
            "/v1/reference-data/locations/hotels/by-geocode",
            {
                "latitude": latitude,
                "longitude": longitude,
                "radius": 12,
                "radiusUnit": "KM",
                "hotelSource": "ALL",
            },
        )
        hotel_ids = [item.get("hotelId") for item in hotel_list.get("data", []) if item.get("hotelId")]
        hotel_ids = hotel_ids[:max_hotels]
        if not hotel_ids:
            return []

        offers = _authorized_get(
            "/v3/shopping/hotel-offers",
            {
                "hotelIds": ",".join(hotel_ids),
                "adults": adults,
                "checkInDate": check_in_date,
                "checkOutDate": check_out_date,
                "roomQuantity": 1,
                "bestRateOnly": "true",
                "countryOfResidence": "TH",
            },
        )
        return [_format_hotel_offer(item) for item in offers.get("data", [])]

    return _safe_api_call(_call)
