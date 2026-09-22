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

"""Trip budget calculation tool for travel-concierge-agent."""

import json

RATES = {
    "budget": {"lodging": 60, "food": 35, "transport": 15, "attractions": 20},
    "moderate": {"lodging": 160, "food": 75, "transport": 35, "attractions": 40},
    "luxury": {"lodging": 450, "food": 200, "transport": 90, "attractions": 100},
}


def calculate_itinerary_budget(
    city: str,
    days: int = 3,
    travel_style: str = "moderate",
    travelers: int = 1,
) -> str:
    """Calculates estimated travel budget and itemized expenses for a trip.

    Args:
        city: Destination city name (e.g. 'San Francisco', 'Tokyo', 'Paris').
        days: Duration of the trip in days (default 3).
        travel_style: Budget tier - 'budget', 'moderate', or 'luxury' (default 'moderate').
        travelers: Number of people traveling (default 1).

    Returns:
        A JSON string with itemized daily/total expense breakdown and grand total USD cost.
    """
    days = max(1, days)
    travelers = max(1, travelers)
    style = travel_style.lower().strip() if travel_style else "moderate"
    rate = RATES.get(style, RATES["moderate"])

    lodging_total = rate["lodging"] * days
    food_total = rate["food"] * days * travelers
    transport_total = rate["transport"] * days * travelers
    attractions_total = rate["attractions"] * days * travelers
    grand_total = lodging_total + food_total + transport_total + attractions_total

    breakdown = {
        "city": city,
        "days": days,
        "travelers": travelers,
        "travel_style": style,
        "daily_rates_per_person_usd": {
            "lodging_per_room": rate["lodging"],
            "food": rate["food"],
            "local_transport": rate["transport"],
            "attractions": rate["attractions"],
        },
        "itemized_totals_usd": {
            "lodging": lodging_total,
            "food": food_total,
            "transportation": transport_total,
            "attractions_and_activities": attractions_total,
        },
        "estimated_grand_total_usd": grand_total,
    }

    return json.dumps(breakdown, indent=2)
