"""FastAPI application entrypoint for the LangGraph-FoundryIQ API."""
from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models.schemas import HealthResponse
from app.routes.chat import router as chat_router

settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

app = FastAPI(
    title="LangGraph-FoundryIQ API",
    description=(
        "LangGraph-based custom agent that integrates with Microsoft Foundry IQ "
        "through the APIM AI Gateway. Designed to run on AKS / AKS NARO."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="langgraph-foundryiq-api", version="0.1.0")


@app.get("/ready", response_model=HealthResponse, tags=["health"])
async def ready() -> HealthResponse:
    # AKS readiness probe — extend with deeper checks if needed.
    return HealthResponse(status="ready", service="langgraph-foundryiq-api", version="0.1.0")


app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
