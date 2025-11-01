from langchain_core.tools import tool

# from typing import Any
import geocoder
import httpx
import json
import os
from urllib.parse import urlencode
from dotenv import load_dotenv

# Constants
FSQ_API_BASE = "https://places-api.foursquare.com"

load_dotenv(".env")
FSQ_SERVICE_TOKEN = os.getenv("FOURSQUARE_SERVICE_TOKEN")

async def submit_request(endpoint: str, params: dict[str, str]) -> str:
    headers = {
        "Authorization": f"Bearer {FSQ_SERVICE_TOKEN}",
        "X-Places-Api-Version": "2025-02-05"
    }
    encoded_params = urlencode(params)
    url = f"{FSQ_API_BASE}{endpoint}?{encoded_params}"
    print(f"[DEBUG] Requesting: {url}")
    print(f"[DEBUG] Headers: {headers}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=3000.0)
            response.raise_for_status()
            print(f"[DEBUG] Response: {response.text}")
            return response.text
        except httpx.HTTPStatusError as e:
            print(f"[ERROR] HTTP error: {e.response.status_code} - {e.response.text}")
            return json.dumps({"error": f"HTTP error: {e.response.status_code} - {e.response.text}"})
        except Exception as e:
            print(f"[ERROR] Exception during request: {e}")
            return json.dumps({"error": f"Exception during request: {str(e)}"})
        
@tool
async def search_near(where: str, what: str) -> str:
    """Search for places near a particular named region

    Args:
        where: a geographic region (e.g., Los Angeles, Fort Greene)
        what: concept you are looking for (e.g., coffee shop, Hard Rock Cafe)
    """
    params = {
        "query": what,
        "near": where,
        "limit": 5
    }
    response_text = await submit_request("/places/search", params)
    if response_text in ("null", None, ""):
        return f"Sorry, I couldn't find {what} near {where} (no response)."
    try:
        data = json.loads(response_text)
        if "error" in data:
            return f"API error: {data['error']}"
        results = data.get("results", [])
        if not results:
            return f"No {what} found near {where}."
        summary = []
        for place in results:
            name = place.get("name", "Unknown")
            address = ", ".join(place.get("location", {}).get("formatted_address", []))
            summary.append(f"{name} ({address})")
        return "Top results:\n" + "\n".join(summary)
    except Exception as e:
        print(f"[ERROR] Exception parsing response: {e}")
        return f"Sorry, I couldn't process the results for {what} near {where}."


@tool()
async def search_near_point(what: str, ll: str, radius: int) -> str:
    """Search for places near a particular point including restaurants, cafes, shops, etc.

    Args:
        what: concept you are looking for (e.g., coffee shop, Hard Rock Cafe)
        ll: comma separated latitude and longitude pair (e.g., 40.74,-74.0)
        radius: distance in meters (e.g., 1000)
    """
    params = {
        "query": what,
        "ll": ll,
        "radius": radius,
        "limit": 5
    }
    return await submit_request("/places/search", params)


@tool()
async def place_snap(ll: str) -> str:
    """Get the most likely place the user is at based on their reported location.

    Args:
        ll: comma separate latitude and longitude pair (e.g., 40.74,-74.0)
    """
    params = {
        "ll": ll,
        "limit": 1
    }
    return await submit_request("/geotagging/candidates", params)

@tool()
async def place_details(id: str) -> str:
    """Get detailed information about a place based on the fsq_id (foursquare id), including:
       description, phone, website, social media, hours, popular hours, rating (out of 10),
       price, menu, top photos, top tips (mini-reviews from users), top tastes, and features
       such as takes reservations.
    """
    params = {
      "fields": "description,tel,website,social_media,hours,hours_popular,rating,price,menu,photos,tips,tastes,attributes"
    }
    return await submit_request(f"/places/{id}", params)

@tool()
async def get_location() -> str:
    """Get user's location. Returns latitude and longitude, or else reports it could not find location. Tries to guess user's location
      based on ip address. Useful if the user has not provided their own precise location.
    """
    location = geocoder.ip('me')
    if not location.ok:
        return "I don't know where you are"
    return f"{location.lat},{location.lng} (using geoip, so this is an approximation)"

