# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Maps Geocoding & Places (New) API tools for travel-concierge-agent."""

import json
import logging
import os
from typing import Any, Dict, List
import httpx

logger = logging.getLogger(__name__)


def geocode_address(address: str) -> str:
    """Geocodes a street address or location name into geographic coordinates using Google Maps Geocoding API.

    Args:
        address: The address or location query to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Eiffel Tower, Paris').

    Returns:
        A JSON string with key fields: name, address, and location (latitude, longitude).
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": api_key}

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK" or not data.get("results"):
            return f"No geocoding results found for address: '{address}'. Status: {data.get('status')}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address", address)
        loc = result.get("geometry", {}).get("location", {})

        output = {
            "name": formatted_address,
            "address": formatted_address,
            "location": {
                "latitude": loc.get("lat"),
                "longitude": loc.get("lng"),
            },
        }
        return json.dumps(output, indent=2)
    except Exception as e:
        logger.error(f"Geocoding API error: {e}")
        return f"Error calling Geocoding API for '{address}': {e}"


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1000.0,
) -> str:
    """Finds nearby places of a given type near coordinates using Google Places API (New).

    Args:
        latitude: Latitude coordinate of center search point (e.g. 37.7749).
        longitude: Longitude coordinate of center search point (e.g. -122.4194).
        place_type: Type of place to search for (e.g. 'restaurant', 'cafe', 'tourist_attraction', 'museum', 'hotel').
        radius_meters: Search radius in meters (default 1000.0 meters).

    Returns:
        A JSON string list of nearby places containing key fields: name, address, and location (latitude, longitude).
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }
    body = {
        "includedTypes": [place_type],
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": radius_meters,
            }
        },
    }

    try:
        response = httpx.post(url, json=body, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        raw_places = data.get("places", [])
        if not raw_places:
            return f"No nearby places of type '{place_type}' found within {radius_meters}m of ({latitude}, {longitude})."

        results: List[Dict[str, Any]] = []
        for place in raw_places:
            name_text = place.get("displayName", {}).get("text", "")
            formatted_addr = place.get("formattedAddress", "")
            loc = place.get("location", {})

            results.append(
                {
                    "name": name_text,
                    "address": formatted_addr,
                    "location": {
                        "latitude": loc.get("latitude"),
                        "longitude": loc.get("longitude"),
                    },
                }
            )

        return json.dumps(results, indent=2)
    except Exception as e:
        logger.error(f"Places API (New) error: {e}")
        return f"Error calling Places API (New) for coordinates ({latitude}, {longitude}): {e}"
