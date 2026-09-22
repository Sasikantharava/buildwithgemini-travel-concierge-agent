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

from unittest.mock import MagicMock, patch
from app.rag_tool import search_travel_corpus


def test_search_travel_corpus_unconfigured():
    with patch("app.rag_tool._get_corpus_name", return_value=""):
        res = search_travel_corpus("history")
        assert "RAG travel corpus is not initialized or configured yet" in res


@patch("vertexai.preview.rag.retrieval_query")
def test_search_travel_corpus_success(mock_query):
    mock_context = MagicMock()
    mock_context.text = "Historical travel notes from Gutenberg book."

    mock_resp = MagicMock()
    mock_resp.contexts.contexts = [mock_context]
    mock_query.return_value = mock_resp

    with patch("app.rag_tool._get_corpus_name", return_value="projects/test/locations/us-central1/ragCorpora/123"):
        res = search_travel_corpus("history")
        assert "Historical travel notes" in res
