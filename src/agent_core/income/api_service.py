"""Paid API service — the agent's own monetizable API endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter
from pydantic import BaseModel

from agent_core.income.revenue_tracker import log_revenue_event

logger = logging.getLogger(__name__)

api_service_router = APIRouter()


class ExplainCodeRequest(BaseModel):
    code: str


class ExplainCodeResponse(BaseModel):
    explanation: str


@api_service_router.post("/api/explain-code", response_model=ExplainCodeResponse)
async def explain_code_endpoint(request: ExplainCodeRequest) -> ExplainCodeResponse:
    log_revenue_event("explain-code", 0.01)  # $0.01 per request
    # In a real scenario, this would call a more sophisticated code explanation model.
    explanation = f"This is a placeholder explanation for the provided code: {request.code[:100]}..."
    return ExplainCodeResponse(explanation=explanation)


class SummarizeRequest(BaseModel):
    text: str


class SummarizeResponse(BaseModel):
    summary: str


@api_service_router.post("/api/summarize", response_model=SummarizeResponse)
async def summarize_endpoint(request: SummarizeRequest) -> SummarizeResponse:
    log_revenue_event("summarize", 0.01)  # $0.01 per request
    # Placeholder for a real summarization model
    summary = f"This is a placeholder summary for the provided text: {request.text[:100]}..."
    return SummarizeResponse(summary=summary)

