"""
Thin Azure AI Search helper — exposed so the LangGraph agent can do an
additional keyword/vector pass over Foundry IQ knowledge sources if desired.

In the default architecture, Foundry IQ owns retrieval and the Foundry agent
returns grounded answers via APIM. This client is provided so the LangGraph
graph can surface "related documents" alongside the agent answer (enrichment
only — it is **not** a fallback path around APIM/Foundry).
"""
from __future__ import annotations

import logging
from typing import List, Optional

from app.config import Settings, get_settings
from app.models.schemas import Citation

logger = logging.getLogger(__name__)


class AzureSearchClient:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._client = None  # lazy

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        if not (self.settings.azure_search_endpoint and self.settings.azure_search_index_name):
            return None
        try:
            from azure.core.credentials import AzureKeyCredential
            from azure.search.documents import SearchClient
            from azure.identity import DefaultAzureCredential

            cred = (
                AzureKeyCredential(self.settings.azure_search_api_key)
                if self.settings.azure_search_api_key
                else DefaultAzureCredential()
            )
            self._client = SearchClient(
                endpoint=self.settings.azure_search_endpoint,
                index_name=self.settings.azure_search_index_name,
                credential=cred,
            )
            return self._client
        except Exception as exc:  # noqa: BLE001
            logger.warning("AzureSearchClient init failed: %s", exc)
            return None

    def search(self, query: str, top: int = 5) -> List[Citation]:
        client = self._ensure_client()
        if client is None:
            return []
        try:
            results = client.search(search_text=query, top=top, query_type="simple")
            citations: List[Citation] = []
            for doc in results:
                citations.append(
                    Citation(
                        title=doc.get("title") or doc.get("metadata_spo_item_name"),
                        url=doc.get("url") or doc.get("metadata_spo_item_path"),
                        snippet=(doc.get("content") or doc.get("chunk") or "")[:400],
                        index=self.settings.azure_search_index_name,
                    )
                )
            return citations
        except Exception as exc:  # noqa: BLE001
            logger.warning("AzureSearch query failed: %s", exc)
            return []
