"""Chat + sample prompts routes."""
from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, HTTPException

from app.graph.langgraph_workflow import get_graph
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SamplePrompt,
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Sample prompts grounded in the SharePoint search (`sp-search`) Foundry agent.
# These map to typical content surfaced by the AI Search indexes pointed at the
# SharePoint data source in the project.
SAMPLE_PROMPTS: List[SamplePrompt] = [
    SamplePrompt(
        id=1,
        title="Remote work policy",
        prompt="What are our latest company policies on remote work and hybrid schedules?",
        category="HR & Policy",
        icon="briefcase-outline",
    ),
    SamplePrompt(
        id=2,
        title="Quarterly business review",
        prompt="Find the most recent quarterly business review documents and summarize the top three takeaways.",
        category="Business",
        icon="analytics-outline",
    ),
    SamplePrompt(
        id=3,
        title="Engineering onboarding",
        prompt="Show me the onboarding documentation for new engineers and list the day-one checklist.",
        category="Onboarding",
        icon="people-outline",
    ),
    SamplePrompt(
        id=4,
        title="Information security",
        prompt="What is our current information security policy and how does it apply to AI workloads?",
        category="Security",
        icon="shield-checkmark-outline",
    ),
    SamplePrompt(
        id=5,
        title="Foundry IQ architecture",
        prompt="Find architecture documents for the Foundry IQ platform and explain the retrieval pipeline.",
        category="Architecture",
        icon="git-network-outline",
    ),
    SamplePrompt(
        id=6,
        title="Employee handbook updates",
        prompt="Summarize the most recent updates to the employee handbook in the last 90 days.",
        category="HR & Policy",
        icon="book-outline",
    ),
    SamplePrompt(
        id=7,
        title="Azure deployment runbooks",
        prompt="Where can I find Azure deployment runbooks for App Service, AKS, and Container Apps?",
        category="Operations",
        icon="cloud-upload-outline",
    ),
    SamplePrompt(
        id=8,
        title="AI Solution Engineer training",
        prompt="List training resources and learning paths for AI Solution Engineers working on Microsoft Foundry.",
        category="Learning",
        icon="school-outline",
    ),
    SamplePrompt(
        id=9,
        title="Customer SLA agreements",
        prompt="Find documents related to customer SLA agreements and the support response-time commitments.",
        category="Customer",
        icon="document-text-outline",
    ),
    SamplePrompt(
        id=10,
        title="AI POC team updates",
        prompt="What are the latest project updates from the AI POC team and which workloads moved to production?",
        category="Project",
        icon="rocket-outline",
    ),
]


@router.get("/prompts", response_model=List[SamplePrompt])
async def list_sample_prompts() -> List[SamplePrompt]:
    return SAMPLE_PROMPTS


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    graph = get_graph()
    try:
        result = await graph.ainvoke(
            {
                "prompt": request.prompt,
                "history": [m.model_dump() for m in request.history],
                "thread_id": request.thread_id,
            }
        )
    except TimeoutError as exc:
        logger.error("Foundry timeout: %s", exc)
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Chat invocation failed")
        raise HTTPException(status_code=502, detail=f"Upstream Foundry error: {exc}") from exc

    return ChatResponse(
        answer=result.get("answer", ""),
        thread_id=result.get("thread_id"),
        run_id=result.get("run_id"),
        citations=result.get("citations", []),
        latency_ms=result.get("latency_ms"),
    )
