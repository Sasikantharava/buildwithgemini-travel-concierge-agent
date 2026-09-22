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
from app.budget_tool import calculate_itinerary_budget


def test_calculate_itinerary_budget_defaults():
    result_str = calculate_itinerary_budget(city="San Francisco")
    data = json.loads(result_str)

    assert data["city"] == "San Francisco"
    assert data["days"] == 3
    assert data["travelers"] == 1
    assert data["travel_style"] == "moderate"
    assert data["estimated_grand_total_usd"] > 0


def test_calculate_itinerary_budget_luxury():
    result_str = calculate_itinerary_budget(
        city="Tokyo", days=5, travel_style="luxury", travelers=2
    )
    data = json.loads(result_str)

    assert data["city"] == "Tokyo"
    assert data["days"] == 5
    assert data["travelers"] == 2
    assert data["travel_style"] == "luxury"
    assert data["itemized_totals_usd"]["lodging"] == 450 * 5
