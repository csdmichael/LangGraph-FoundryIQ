"""
Foundry Agent client.

Routes all traffic through the APIM AI Gateway (private VNET + private endpoints
to Foundry). Falls back to the direct Foundry project endpoint with Entra ID
(DefaultAzureCredential) when APIM is not configured — useful for local dev.

Foundry Agent REST surface (v1) used:
  POST {base}/threads                                  -> create thread
  POST {base}/threads/{thread_id}/messages             -> add user message
  POST {base}/threads/{thread_id}/runs                 -> start run (agent_id)
  GET  {base}/threads/{thread_id}/runs/{run_id}        -> poll run
  GET  {base}/threads/{thread_id}/messages             -> read messages

When traffic goes through APIM the gateway terminates Entra auth (managed
identity / client cert) and applies AI-Gateway policies (token-limit, semantic
cache, content safety, logging). The client only needs to send the APIM
subscription key.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import Settings, get_settings
from app.models.schemas import Citation

logger = logging.getLogger(__name__)

# Foundry Agents REST API version (Azure AI Foundry — agents/v1)
FOUNDRY_API_VERSION = "2025-05-15-preview"
DEFAULT_TIMEOUT = httpx.Timeout(60.0, connect=10.0)
POLL_INTERVAL_SEC = 1.0
MAX_POLL_SEC = 90


class FoundryAgentClient:
    """Async client that invokes the Foundry agent (`sp-search`) via APIM."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self._base_url = self.settings.foundry_gateway_url
        self._agent_id = self.settings.foundry_agent_id
        self._use_apim = bool(self.settings.apim_base_url)
        self._client: Optional[httpx.AsyncClient] = None
        self._entra_token: Optional[Tuple[str, float]] = None  # (token, exp)

    # ----------------------------- lifecycle --------------------------------

    async def __aenter__(self) -> "FoundryAgentClient":
        self._client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ------------------------------ auth ------------------------------------

    async def _auth_headers(self) -> Dict[str, str]:
        """Build the per-request auth headers."""
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self._use_apim:
            # APIM terminates Entra; we just present the subscription key.
            if self.settings.apim_subscription_key:
                headers["Ocp-Apim-Subscription-Key"] = self.settings.apim_subscription_key
            return headers

        # Direct Foundry path — Entra token via DefaultAzureCredential.
        token = await self._get_entra_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    async def _get_entra_token(self) -> Optional[str]:
        """Acquire a Foundry-scoped Entra token (cached for ~50 min)."""
        now = time.time()
        if self._entra_token and self._entra_token[1] - 60 > now:
            return self._entra_token[0]
        try:
            # Lazy import — only needed in non-APIM mode.
            from azure.identity.aio import DefaultAzureCredential

            cred = DefaultAzureCredential()
            try:
                token = await cred.get_token("https://ai.azure.com/.default")
            finally:
                await cred.close()
            self._entra_token = (token.token, float(token.expires_on))
            return token.token
        except Exception as exc:  # noqa: BLE001
            logger.warning("Entra token acquisition failed: %s", exc)
            return None

    # ---------------------------- low-level ---------------------------------

    def _url(self, path: str) -> str:
        sep = "&" if "?" in path else "?"
        return f"{self._base_url.rstrip('/')}{path}{sep}api-version={FOUNDRY_API_VERSION}"

    async def _request(
        self, method: str, path: str, *, json_body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        assert self._client is not None, "FoundryAgentClient not entered"
        headers = await self._auth_headers()
        url = self._url(path)
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
            retry=retry_if_exception_type((httpx.TransportError, httpx.HTTPStatusError)),
            reraise=True,
        ):
            with attempt:
                resp = await self._client.request(method, url, headers=headers, json=json_body)
                if resp.status_code >= 500:
                    resp.raise_for_status()
                if resp.status_code >= 400:
                    logger.error("Foundry %s %s -> %s: %s", method, url, resp.status_code, resp.text)
                    resp.raise_for_status()
                return resp.json() if resp.content else {}
        return {}  # pragma: no cover

    # ------------------------------ API -------------------------------------

    async def create_thread(self) -> str:
        data = await self._request("POST", "/threads", json_body={})
        return data["id"]

    async def add_message(self, thread_id: str, content: str) -> None:
        await self._request(
            "POST",
            f"/threads/{thread_id}/messages",
            json_body={"role": "user", "content": content},
        )

    async def start_run(self, thread_id: str) -> str:
        data = await self._request(
            "POST",
            f"/threads/{thread_id}/runs",
            json_body={"assistant_id": self._agent_id},
        )
        return data["id"]

    async def wait_for_run(self, thread_id: str, run_id: str) -> Dict[str, Any]:
        elapsed = 0.0
        terminal = {"completed", "failed", "cancelled", "expired"}
        while elapsed < MAX_POLL_SEC:
            data = await self._request("GET", f"/threads/{thread_id}/runs/{run_id}")
            if data.get("status") in terminal:
                return data
            await asyncio.sleep(POLL_INTERVAL_SEC)
            elapsed += POLL_INTERVAL_SEC
        raise TimeoutError(f"Foundry run {run_id} did not complete within {MAX_POLL_SEC}s")

    async def latest_assistant_message(self, thread_id: str) -> Tuple[str, List[Citation]]:
        data = await self._request("GET", f"/threads/{thread_id}/messages")
        messages = data.get("data", []) or []
        for msg in messages:  # API returns newest first
            if msg.get("role") != "assistant":
                continue
            text_parts: List[str] = []
            citations: List[Citation] = []
            for part in msg.get("content", []) or []:
                if part.get("type") == "text":
                    text_value = (part.get("text") or {}).get("value", "")
                    text_parts.append(text_value)
                    for ann in (part.get("text") or {}).get("annotations", []) or []:
                        citations.append(
                            Citation(
                                title=ann.get("file_citation", {}).get("file_name")
                                or ann.get("text"),
                                url=ann.get("file_citation", {}).get("uri")
                                or ann.get("url_citation", {}).get("url"),
                                snippet=ann.get("text"),
                                index=ann.get("file_citation", {}).get("index"),
                            )
                        )
            return "\n".join(text_parts).strip(), citations
        return "", []

    # ------------------------------ orchestration ---------------------------

    async def ask(
        self, prompt: str, thread_id: Optional[str] = None
    ) -> Tuple[str, str, str, List[Citation]]:
        """Send a prompt to the Foundry agent and return (answer, thread, run, citations)."""
        thread = thread_id or await self.create_thread()
        await self.add_message(thread, prompt)
        run_id = await self.start_run(thread)
        run = await self.wait_for_run(thread, run_id)
        if run.get("status") != "completed":
            err = (run.get("last_error") or {}).get("message", run.get("status"))
            raise RuntimeError(f"Foundry run did not complete: {err}")
        answer, citations = await self.latest_assistant_message(thread)
        return answer, thread, run_id, citations
