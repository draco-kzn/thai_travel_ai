import json
import os
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import streamlit as st


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
    },
    "Chiang Mai": {
        "airport_code": "CNX",
        "airport_label": "Chiang Mai International",
        "hotel_label": "Chiang Mai",
        "lat": 18.7883,
        "lng": 98.9853,
        "flight_note": "使用清迈国际机场作为实时航班参考。",
    },
    "Pattaya": {
        "airport_code": "UTP",
        "airport_label": "U-Tapao / Pattaya",
        "hotel_label": "Pattaya",
        "lat": 12.9236,
        "lng": 100.8825,
        "flight_note": "使用乌塔堡机场近似 Pattaya 的实时机票。",
    },
    "Hua Hin": {
        "airport_code": "HHQ",
        "airport_label": "Hua Hin Airport",
        "hotel_label": "Hua Hin",
        "lat": 12.5684,
        "lng": 99.9577,
        "flight_note": "使用华欣机场近似实时机票。",
    },
    "Phuket": {
        "airport_code": "HKT",
        "airport_label": "Phuket International",
        "hotel_label": "Phuket",
        "lat": 7.8804,
        "lng": 98.3923,
        "flight_note": "使用普吉国际机场作为实时航班参考。",
    },
    "Krabi": {
        "airport_code": "KBV",
        "airport_label": "Krabi International",
        "hotel_label": "Krabi",
        "lat": 8.0863,
        "lng": 98.9063,
        "flight_note": "使用甲米国际机场作为实时航班参考。",
    },
    "Koh Samui": {
        "airport_code": "USM",
        "airport_label": "Samui International",
        "hotel_label": "Koh Samui",
        "lat": 9.5120,
        "lng": 100.0136,
        "flight_note": "使用苏梅国际机场作为实时航班参考。",
    },
    "Phi Phi Islands": {
        "airport_code": "HKT",
        "airport_label": "Phuket gateway",
        "hotel_label": "Phi Phi Islands",
        "lat": 7.7407,
        "lng": 98.7784,
        "flight_note": "机票用 Phuket 作为皮皮岛的进出网关；岛上实际接驳通常仍需船运。",
    },
    "Koh Lanta": {
        "airport_code": "KBV",
        "airport_label": "Krabi gateway",
        "hotel_label": "Koh Lanta",
        "lat": 7.6142,
        "lng": 99.0367,
        "flight_note": "机票用 Krabi 作为兰塔岛进出网关；落地后通常仍需地面接驳。",
    },
    "Koh Lipe": {
        "airport_code": "HDY",
        "airport_label": "Hat Yai gateway",
        "hotel_label": "Koh Lipe",
        "lat": 6.4880,
        "lng": 99.3042,
        "flight_note": "机票用 Hat Yai 作为丽贝岛进出网关；实际到岛仍需车船联运。",
    },
}


def has_amadeus_credentials():
    return bool(os.getenv("AMADEUS_API_KEY") and os.getenv("AMADEUS_API_SECRET"))


def get_city_realtime_meta(city_name):
    return CITY_REALTIME_META.get(city_name)


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
    data = _request_json(f"{_get_amadeus_base_url()}/v1/security/oauth2/token", method="POST", headers=headers, body=body)
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

    return {
        "price": raw_offer["price"]["total"],
        "currency": raw_offer["price"]["currency"],
        "carrier": ",".join(validating) if validating else first_segment.get("carrierCode", "-"),
        "departure": first_segment["departure"]["at"],
        "arrival": last_segment["arrival"]["at"],
        "stops": max(len(raw_offer["itineraries"][0]["segments"]) - 1, 0),
        "duration": raw_offer["itineraries"][0].get("duration", ""),
        "source": raw_offer.get("source", ""),
    }


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
