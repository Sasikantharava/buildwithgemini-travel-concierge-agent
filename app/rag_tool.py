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

"""Vertex AI RAG retrieval tool for travel-concierge-agent."""

import json
import logging
import os
import vertexai

logger = logging.getLogger(__name__)

PROJECT_ID = "qwiklabs-gcp-01-f6cb912fc91a"
LOCATION = "us-central1"

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "rag_config.json")
CORPUS_NAME = ""


def _get_corpus_name() -> str:
    global CORPUS_NAME
    if CORPUS_NAME:
        return CORPUS_NAME
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                CORPUS_NAME = cfg.get("corpus_name", "")
                return CORPUS_NAME
        except Exception as e:
            logger.warning(f"Could not load rag_config.json: {e}")
    return ""


def search_travel_corpus(query: str) -> str:
    """Searches the grounded travel knowledge corpus (Gutenberg pg49513) for relevant facts, history, or passages.

    Args:
        query: What to look up in the grounded travel corpus (e.g. historical notes, locations, culture).

    Returns:
        Relevant matched passages from the grounded corpus, or a message if none found.
    """
    corpus_name = _get_corpus_name()
    if not corpus_name:
        return "RAG travel corpus is not initialized or configured yet."

    try:
        from vertexai.preview import rag

        vertexai.init(project=PROJECT_ID, location=LOCATION)
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=corpus_name)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        if not passages:
            return f"No relevant passages found in the travel corpus for query: '{query}'."
        return "\n\n---\n\n".join(passages)
    except Exception as e:
        logger.warning(f"RAG retrieval query failed: {e}")
        return f"RAG retrieval unavailable or returned error for query '{query}': {e}"
