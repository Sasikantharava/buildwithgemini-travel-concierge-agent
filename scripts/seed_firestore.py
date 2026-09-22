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

"""Seed script to populate Firestore 'destinations' collection.

Hardcodes project ID string: "qwiklabs-gcp-01-f6cb912fc91a"
"""

import sys
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-f6cb912fc91a"

SEED_DESTINATIONS = [
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


def seed_database():
    print(f"Connecting to Firestore with hardcoded project ID: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("destinations")

    count = 0
    for item in SEED_DESTINATIONS:
        doc_id = item["id"]
        data = {k: v for k, v in item.items() if k != "id"}
        collection_ref.document(doc_id).set(data)
        print(f"Seeded destination: {item['name']} ({doc_id})")
        count += 1

    print(f"Successfully seeded {count} items into 'destinations' collection in Firestore.")


if __name__ == "__main__":
    seed_database()
