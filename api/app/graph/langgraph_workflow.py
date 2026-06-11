"""
LangGraph workflow that orchestrates the Foundry agent call.

The graph is intentionally small — Foundry IQ owns retrieval/grounding inside
the agent, so the LangGraph layer is responsible for:

  1. prepare    — normalize the prompt, attach conversational history
  2. invoke     — call the Foundry agent (`sp-search`) through APIM
  3. enrich     — (optional) add complementary AI Search citations
  4. finalize   — package the response for the API layer

This makes it trivial to extend with extra tools, guardrails, or human-in-
the-loop later without touching the API surface.
"""
from __future__ import annotations

import logging
import time
from typing import Annotated, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from app.models.schemas import Citation
from app.services.foundry_client import FoundryAgentClient
from app.services.search_client import AzureSearchClient

logger = logging.getLogger(__name__)


def _merge_citations(
    a: List[Citation], b: List[Citation]
) -> List[Citation]:
    seen = set()
    merged: List[Citation] = []
    for c in list(a) + list(b):
        key = (c.url or "") + "|" + (c.title or "")
        if key in seen:
            continue
        seen.add(key)
        merged.append(c)
    return merged


class GraphState(TypedDict, total=False):
    prompt: str
    history: List[dict]
    thread_id: Optional[str]

    answer: str
    run_id: Optional[str]
    citations: Annotated[List[Citation], _merge_citations]
    latency_ms: int


async def _node_prepare(state: GraphState) -> GraphState:
    prompt = (state.get("prompt") or "").strip()
    if not prompt:
        raise ValueError("Empty prompt")
    # Prepend a short history block so the Foundry agent has conversational context.
    history = state.get("history") or []
    if history:
        hist_lines = [f"{m['role'].upper()}: {m['content']}" for m in history[-6:]]
        prompt = "Previous conversation:\n" + "\n".join(hist_lines) + "\n\nUser: " + prompt
    return {"prompt": prompt}


async def _node_invoke_foundry(state: GraphState) -> GraphState:
    start = time.perf_counter()
    async with FoundryAgentClient() as client:
        answer, thread_id, run_id, citations = await client.ask(
            prompt=state["prompt"],
            thread_id=state.get("thread_id"),
        )
    latency = int((time.perf_counter() - start) * 1000)
    return {
        "answer": answer,
        "thread_id": thread_id,
        "run_id": run_id,
        "citations": citations,
        "latency_ms": latency,
    }


async def _node_enrich(state: GraphState) -> GraphState:
    # Only run if we have an answer (don't waste tokens on failures)
    if not state.get("answer"):
        return {}
    client = AzureSearchClient()
    extra = client.search(state["prompt"], top=3)
    if not extra:
        return {}
    return {"citations": extra}


async def _node_finalize(state: GraphState) -> GraphState:
    return {}  # all assembly already in state


def build_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(GraphState)
    workflow.add_node("prepare", _node_prepare)
    workflow.add_node("invoke_foundry", _node_invoke_foundry)
    workflow.add_node("enrich", _node_enrich)
    workflow.add_node("finalize", _node_finalize)

    workflow.set_entry_point("prepare")
    workflow.add_edge("prepare", "invoke_foundry")
    workflow.add_edge("invoke_foundry", "enrich")
    workflow.add_edge("enrich", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
