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

"""Image generation tool using gemini-3.1-flash-lite-image model and GCS upload."""

import logging
import uuid
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

logger = logging.getLogger(__name__)

PROJECT_ID = "qwiklabs-gcp-01-f6cb912fc91a"
BUCKET_NAME = "travel-concierge-media-f6cb912f"
MODEL_NAME = "gemini-3.1-flash-lite-image"


async def generate_destination_image(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generates a travel landscape or destination photo based on a description, saves it as an artifact, and uploads it to public Cloud Storage.

    Args:
        prompt: Detailed description of the travel scene, venue, landmark, or destination to generate an image for.
        tool_context: Context for saving session artifacts in Agent Engine.

    Returns:
        The public HTTPS URL (https://storage.googleapis.com/<bucket>/<object>) of the generated image.
    """
    try:
        # 1. Generate image with gemini-3.1-flash-lite-image in global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        part = response.candidates[0].content.parts[0]
        image_bytes = part.inline_data.data
        mime_type = part.inline_data.mime_type or "image/jpeg"

        # Unique filename/object name
        img_id = uuid.uuid4().hex[:8]
        filename = f"destination_{img_id}.jpg"

        # 2. Save image as session artifact using tool_context
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 3. Upload image bytes directly to GCS bucket (without writing to local disk)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return public_url
    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        return f"Failed to generate destination image: {e}"
