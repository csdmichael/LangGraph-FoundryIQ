"""Pydantic request/response schemas for the chat API."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="user | assistant | system")
    content: str


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    thread_id: Optional[str] = Field(
        default=None,
        description="Optional Foundry agent thread_id to continue a conversation.",
    )
    history: List[ChatMessage] = Field(default_factory=list)


class Citation(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    snippet: Optional[str] = None
    index: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    thread_id: Optional[str] = None
    run_id: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)
    latency_ms: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SamplePrompt(BaseModel):
    id: int
    title: str
    prompt: str
    category: str
    icon: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
