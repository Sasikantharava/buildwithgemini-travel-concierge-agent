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
from app.location_tool import fetch_location_coordinates


def test_fetch_location_coordinates_success():
    result_str = fetch_location_coordinates(query="San Francisco")
    data = json.loads(result_str)

    assert isinstance(data, list)
    assert len(data) > 0
    assert "display_name" in data[0]
    assert "latitude" in data[0]
    assert "longitude" in data[0]
