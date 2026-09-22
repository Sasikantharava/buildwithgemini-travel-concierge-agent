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

import json
from app.firestore_tools import add_destination, search_destinations


def test_search_destinations_all():
    results_str = search_destinations()
    data = json.loads(results_str)
    assert isinstance(data, list)
    assert len(data) >= 3


def test_search_destinations_filtered():
    results_str = search_destinations(city="San Francisco")
    data = json.loads(results_str)
    assert isinstance(data, list)
    assert all("San Francisco" in spot["city"] for spot in data)


def test_add_destination():
    res = add_destination(
        name="Coit Tower",
        city="San Francisco",
        category="Sightseeing",
        description="Art deco tower with murals and panoramic views.",
        tags="views, historic, landmark",
        rating=4.6,
    )
    assert "Coit Tower" in res
    assert "San Francisco" in res

    # Verify search finds the new destination
    search_res = search_destinations(query="Coit Tower")
    assert "Coit Tower" in search_res
