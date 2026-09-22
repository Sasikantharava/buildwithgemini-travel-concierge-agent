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

"""Script to set up a serverless Vertex AI RAG corpus and import Gutenberg book pg49513.txt."""

import json
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
import vertexai

PROJECT_ID = "qwiklabs-gcp-01-f6cb912fc91a"
LOCATION = "us-central1"
GCS_PATH = "gs://travel-concierge-media-f6cb912f/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract useful historical, travel, and cultural facts from this text. "
    "Ignore boilerplate, publication details, and formatting markers. "
    "Output clean, self-contained prose."
)


def main():
    print(f"Initializing Vertex AI for project '{PROJECT_ID}' in '{LOCATION}'...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Switch region's RAG managed DB to serverless mode
    cfg_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    print("Updating RAG Engine configuration to serverless mode...")
    try:
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg_name,
                rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
            )
        )
        print("Serverless RAG Engine configuration applied.")
    except Exception as e:
        print(f"Notice during update_rag_engine_config: {e}")

    # 2. Create serverless RAG corpus
    print("Creating RAG Corpus 'travel-guide-corpus'...")
    corpus = rag.create_corpus(
        display_name="travel-guide-corpus",
        description="Grounding corpus created from Gutenberg ebook pg49513.txt",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    corpus_name = corpus.name
    print(f"SUCCESS: Created RAG Corpus -> {corpus_name}")

    # 3. Import and index file from GCS
    print(f"Importing {GCS_PATH} into corpus...")
    response = rag.import_files(
        corpus_name=corpus_name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"Import complete! Imported RAG files count: {response.imported_rag_files_count}")

    # Save corpus name to app/rag_config.json for tool reference
    config = {"corpus_name": corpus_name, "gcs_path": GCS_PATH}
    with open("app/rag_config.json", "w") as f:
        json.dump(config, f, indent=2)
    print(f"Saved RAG configuration to app/rag_config.json")


if __name__ == "__main__":
    main()
