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

"""Public API location tool for travel-concierge-agent using OpenStreetMap Nominatim."""

import json
import os
import httpx


def fetch_location_coordinates(query: str) -> str:
    """Fetches real geographical location data and coordinates for a city or landmark.

    Args:
        query: Name of the city, venue, or landmark to locate (e.g. 'San Francisco', 'Eiffel Tower', 'Tokyo').

    Returns:
        A JSON string containing display name, latitude, longitude, and place details.
    """
    api_key = os.environ.get("LOCATION_API_KEY")
    headers = {"User-Agent": "TravelConciergeAgent/1.0 (build-with-gemini)"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    params = {"q": query, "format": "json", "limit": 3}

    try:
        response = httpx.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers=headers,
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return f"No location coordinates found for query: '{query}'."

        results = []
        for item in data:
            results.append(
                {
                    "display_name": item.get("display_name"),
                    "latitude": item.get("lat"),
                    "longitude": item.get("lon"),
                    "category": item.get("class"),
                    "type": item.get("type"),
                }
            )

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error fetching location data for query '{query}': {e}"
