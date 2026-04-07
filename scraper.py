import re
import requests
from urllib.parse import unquote

# ── PASTE YOUR KEYS HERE ──────────────────────────────────────────────────────
PLACES_API_KEY = "Api_key"
# ─────────────────────────────────────────────────────────────────────────────


def extract_business_name(url: str) -> str:
    decoded = unquote(url)
    match = re.search(r"/maps/place/([^/@?&]+)", decoded)
    if match:
        name = match.group(1).replace("+", " ").replace("_", " ").strip()
        return re.sub(r"\s+", " ", name).strip()
    return ""


def extract_coords(url: str):
    match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
    if match:
        return match.group(1), match.group(2)
    return None, None


def search_business(name: str, lat=None, lng=None) -> dict | None:
    params = {"query": name, "key": PLACES_API_KEY, "language": "en"}
    if lat and lng:
        params["location"] = f"{lat},{lng}"
        params["radius"] = "2000"

    resp = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params=params, timeout=10
    )
    data = resp.json()

    if data.get("status") == "REQUEST_DENIED":
        raise ValueError(
            "API key denied. Go to console.cloud.google.com and make sure:\n"
            "1. Places API is enabled\n"
            "2. Billing is activated (free $200 credit applies)"
        )

    if data.get("status") != "OK" or not data.get("results"):
        return None

    return data["results"][0]


def get_details(place_id: str) -> dict:
    params = {
        "place_id": place_id,
        "fields": (
            "name,rating,user_ratings_total,formatted_address,"
            "formatted_phone_number,website,types,reviews,"
            "opening_hours,price_level,editorial_summary"
        ),
        "key": PLACES_API_KEY,
        "reviews_sort": "most_relevant",
        "language": "en",
    }

    resp = requests.get(
        "https://maps.googleapis.com/maps/api/place/details/json",
        params=params, timeout=10
    )
    data = resp.json()

    if data.get("status") != "OK":
        return {"error": f"Places API error: {data.get('status')} — check your API key."}

    result = data.get("result", {})

    reviews = []
    for r in result.get("reviews", []):
        text = r.get("text", "").strip()
        if text:
            reviews.append({
                "author": r.get("author_name", "Anonymous"),
                "rating": r.get("rating", 0),
                "text": text,
                "date": r.get("relative_time_description", ""),
            })

    types = result.get("types", [])
    skip = {"point_of_interest", "establishment", "food", "store"}
    category = next((t.replace("_", " ").title() for t in types if t not in skip), "")

    price_map = {1: "₹", 2: "₹₹", 3: "₹₹₹", 4: "₹₹₹₹"}

    return {
        "business_info": {
            "name": result.get("name", ""),
            "address": result.get("formatted_address", ""),
            "phone": result.get("formatted_phone_number", ""),
            "website": result.get("website", ""),
            "rating": result.get("rating"),
            "total_reviews": result.get("user_ratings_total", 0),
            "category": category,
            "price_level": price_map.get(result.get("price_level"), ""),
            "summary": result.get("editorial_summary", {}).get("overview", ""),
            "is_open": result.get("opening_hours", {}).get("open_now"),
        },
        "reviews": reviews,
        "total_fetched": len(reviews),
    }


def fetch_reviews(google_maps_url: str) -> dict:
    if not PLACES_API_KEY or "YOUR_" in PLACES_API_KEY:
        return {"error": "Google Places API key is missing in scraper.py", "business_info": {}, "reviews": []}

    name = extract_business_name(google_maps_url)
    lat, lng = extract_coords(google_maps_url)

    if not name:
        return {"error": "Could not read business name from URL. Copy the full URL from your browser.", "business_info": {}, "reviews": []}

    try:
        result = search_business(name, lat, lng)
        if not result:
            result = search_business(name)
        if not result:
            result = search_business(" ".join(name.split()[:3]), lat, lng)
    except ValueError as e:
        return {"error": str(e), "business_info": {}, "reviews": []}

    if not result:
        return {"error": f"Could not find '{name}' on Google Maps. Try a different URL.", "business_info": {}, "reviews": []}

    return get_details(result["place_id"])