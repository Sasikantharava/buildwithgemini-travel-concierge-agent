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

import os
from unittest.mock import MagicMock, patch
from app.google_maps_tools import geocode_address, search_nearby_places


def test_google_maps_tools_missing_key():
    with patch.dict(os.environ, {}, clear=True):
        res1 = geocode_address("1600 Amphitheatre Pkwy, Mountain View, CA")
        assert "GOOGLE_MAPS_API_KEY environment variable is not set" in res1

        res2 = search_nearby_places(37.7749, -122.4194)
        assert "GOOGLE_MAPS_API_KEY environment variable is not set" in res2


@patch("httpx.get")
def test_geocode_address_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "OK",
        "results": [
            {
                "formatted_address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
                "geometry": {"location": {"lat": 37.422, "lng": -122.084}},
            }
        ],
    }
    mock_get.return_value = mock_response

    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}):
        result = geocode_address("1600 Amphitheatre Pkwy")
        assert "Mountain View" in result
        assert "37.422" in result


@patch("httpx.post")
def test_search_nearby_places_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "places": [
            {
                "displayName": {"text": "Blue Bottle Coffee"},
                "formattedAddress": "Mint Plaza, San Francisco, CA",
                "location": {"latitude": 37.782, "longitude": -122.408},
            }
        ]
    }
    mock_post.return_value = mock_response

    with patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test-key"}):
        result = search_nearby_places(37.7749, -122.4194, place_type="cafe")
        assert "Blue Bottle Coffee" in result
        assert "Mint Plaza" in result
