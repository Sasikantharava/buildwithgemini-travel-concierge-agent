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

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.image_tool import generate_destination_image


@pytest.mark.asyncio
@patch("app.image_tool.storage.Client")
@patch("app.image_tool.genai.Client")
async def test_generate_destination_image(mock_genai_client_cls, mock_storage_client_cls):
    # Mock genai client response
    mock_part = MagicMock()
    mock_part.inline_data.data = b"fake-jpeg-bytes"
    mock_part.inline_data.mime_type = "image/jpeg"

    mock_resp = MagicMock()
    mock_resp.candidates = [MagicMock(content=MagicMock(parts=[mock_part]))]

    mock_genai_instance = MagicMock()
    mock_genai_instance.models.generate_content.return_value = mock_resp
    mock_genai_client_cls.return_value = mock_genai_instance

    # Mock storage client
    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_storage_instance = MagicMock()
    mock_storage_instance.bucket.return_value = mock_bucket
    mock_storage_client_cls.return_value = mock_storage_instance

    # Mock tool context
    mock_tool_context = AsyncMock()

    url = await generate_destination_image("Santorini sunset", mock_tool_context)

    assert url.startswith("https://storage.googleapis.com/travel-concierge-media-f6cb912f/destination_")
    assert url.endswith(".jpg")
    mock_tool_context.save_artifact.assert_called_once()
    mock_blob.upload_from_string.assert_called_once_with(b"fake-jpeg-bytes", content_type="image/jpeg")
