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

"""Firestore backend tools for travel-concierge-agent.

Hardcoded GCP project ID string: "qwiklabs-gcp-01-f6cb912fc91a"
Collection: "destinations"
"""

import json
import logging
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from google.api_core import exceptions

logger = logging.getLogger(__name__)

# Hardcoded project ID string required for Agent Platform compatibility
PROJECT_ID = "qwiklabs-gcp-01-f6cb912fc91a"
COLLECTION_NAME = "destinations"

# Fallback seed data in case Firestore database is unprovisioned in environment
SEED_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "sf-ferry-building",
        "name": "Ferry Building Marketplace",
        "city": "San Francisco",
        "category": "Food & Market",
        "description": "Historic landmark on the waterfront featuring artisan food vendors, quiet coffee spots, and scenic bay views.",
        "tags": ["food", "views", "coffee", "historic", "scenic"],
        "rating": 4.8,
    },
    {
        "id": "sf-golden-gate-park",
        "name": "Japanese Tea Garden in Golden Gate Park",
        "city": "San Francisco",
        "category": "Nature & Garden",
        "description": "The oldest public Japanese garden in the US, featuring peaceful koi ponds, cherry blossoms, and classic tea house treats.",
        "tags": ["nature", "quiet", "garden", "tea", "scenic"],
        "rating": 4.7,
    },
    {
        "id": "tokyo-teamlab-planets",
        "name": "teamLab Planets TOKYO",
        "city": "Tokyo",
        "category": "Art & Digital Museum",
        "description": "Immersive digital art museum where visitors walk through water and body-immersive floral art spaces.",
        "tags": ["art", "digital", "modern", "indoor"],
        "rating": 4.9,
    },
    {
        "id": "paris-louvre-museum",
        "name": "Louvre Museum",
        "city": "Paris",
        "category": "Art & History",
        "description": "World-famous art museum housing thousands of historic masterpieces including the Mona Lisa.",
        "tags": ["art", "history", "museum", "culture"],
        "rating": 4.8,
    },
    {
        "id": "kyoto-bamboo-grove",
        "name": "Arashiyama Bamboo Grove",
        "city": "Kyoto",
        "category": "Nature & Sightseeing",
        "description": "Towering bamboo stalks creating a serene, whispering green forest path in western Kyoto.",
        "tags": ["nature", "scenic", "quiet", "walking"],
        "rating": 4.9,
    },
]

# In-memory store used if Firestore database is unprovisioned
_in_memory_store: List[Dict[str, Any]] = list(SEED_ITEMS)


def _get_firestore_client() -> Optional[firestore.Client]:
    """Returns Firestore client configured with hardcoded project ID string."""
    try:
        return firestore.Client(project=PROJECT_ID)
    except Exception as e:
        logger.warning(f"Could not initialize Firestore client: {e}")
        return None


def search_destinations(query: str = "", city: str = "", category: str = "") -> str:
    """Search for travel spots and destinations in the Firestore database.

    Args:
        query: General search keywords to match against destination names, descriptions, or tags (e.g. 'coffee', 'museum', 'nature').
        city: Filter destinations by city name (e.g. 'San Francisco', 'Tokyo', 'Paris').
        category: Filter destinations by category (e.g. 'Food & Market', 'Art & History', 'Nature & Garden').

    Returns:
        A JSON string containing matching destination records with details.
    """
    client = _get_firestore_client()
    matching_spots: List[Dict[str, Any]] = []

    if client:
        try:
            col_ref = client.collection(COLLECTION_NAME)
            docs = col_ref.stream()

            for doc in docs:
                spot = doc.to_dict()
                spot["id"] = doc.id
                matching_spots.append(spot)
        except exceptions.NotFound:
            logger.info("Firestore database unprovisioned, using seed fallback store.")
            matching_spots = list(_in_memory_store)
        except Exception as e:
            logger.warning(f"Error querying Firestore: {e}")
            matching_spots = list(_in_memory_store)
    else:
        matching_spots = list(_in_memory_store)

    # Filter results by city, category, and query
    filtered = []
    query_lower = query.lower().strip()
    city_lower = city.lower().strip()
    category_lower = category.lower().strip()

    for spot in matching_spots:
        spot_city = spot.get("city", "").lower()
        spot_cat = spot.get("category", "").lower()
        spot_name = spot.get("name", "").lower()
        spot_desc = spot.get("description", "").lower()
        spot_tags = [t.lower() for t in spot.get("tags", [])]

        if city_lower and city_lower not in spot_city:
            continue
        if category_lower and category_lower not in spot_cat:
            continue
        if query_lower:
            matches_query = (
                query_lower in spot_name
                or query_lower in spot_desc
                or any(query_lower in tag for tag in spot_tags)
                or query_lower in spot_cat
            )
            if not matches_query:
                continue
        filtered.append(spot)

    if not filtered:
        return f"No destinations found matching city='{city}', category='{category}', query='{query}'."

    return json.dumps(filtered, indent=2)


def add_destination(
    name: str,
    city: str,
    category: str,
    description: str,
    tags: str = "",
    rating: float = 4.5,
) -> str:
    """Add a new travel spot or destination to the Firestore database.

    Args:
        name: Name of the venue or spot (e.g. 'Golden Gate Bridge').
        city: City where the spot is located (e.g. 'San Francisco').
        category: Category of the spot (e.g. 'Sightseeing', 'Food & Market').
        description: Detailed description of the spot.
        tags: Comma-separated tags (e.g. 'scenic, views, landmark').
        rating: Rating out of 5.0 (default 4.5).

    Returns:
        A success message string confirming the spot was added to Firestore.
    """
    doc_id = f"{city.lower().replace(' ', '-')}-{name.lower().replace(' ', '-')}"
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if isinstance(tags, str) else tags

    new_spot = {
        "name": name,
        "city": city,
        "category": category,
        "description": description,
        "tags": tag_list,
        "rating": rating,
    }

    client = _get_firestore_client()
    if client:
        try:
            col_ref = client.collection(COLLECTION_NAME)
            col_ref.document(doc_id).set(new_spot)
            return f"Successfully added '{name}' in {city} to Firestore collection '{COLLECTION_NAME}' (ID: {doc_id})."
        except exceptions.NotFound:
            logger.info("Firestore database unprovisioned, saving to fallback store.")
        except Exception as e:
            logger.warning(f"Error writing to Firestore: {e}")

    new_spot["id"] = doc_id
    _in_memory_store.append(new_spot)
    return f"Successfully added '{name}' in {city} (ID: {doc_id})."
