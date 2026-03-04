"""HTTP client tool with HTTP 402 auto-payment integration."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import aiohttp
import structlog

from .registry import ToolResult, tool

if TYPE_CHECKING:
    from agent_core.economy.http402 import HTTP402Handler

logger = structlog.get_logger()

_http402_handler: HTTP402Handler | None = None


def set_http402_handler(handler: HTTP402Handler) -> None:
    global _http402_handler
    _http402_handler = handler


@tool(
    name="http_request",
    description="Make an HTTP request (GET/POST/PUT/DELETE). Automatically handles HTTP 402 Payment Required by auto-paying.",
    parameters={
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE"],
                "description": "HTTP method",
            },
            "url": {
                "type": "string",
                "description": "URL to request",
            },
            "headers": {
                "type": "object",
                "description": "Request headers (optional)",
            },
            "body": {
                "type": "string",
                "description": "Request body for POST/PUT (optional)",
            },
        },
        "required": ["method", "url"],
    },
    timeout_sec=30,
)
async def http_request(
    method: str,
    url: str,
    headers: dict | None = None,
    body: str = "",
) -> ToolResult:
    """Execute an HTTP request with optional 402 auto-payment."""
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            kwargs: dict = {"headers": headers or {}}

            if body and method in ("POST", "PUT"):
                kwargs["data"] = body
                if "Content-Type" not in kwargs["headers"]:
                    kwargs["headers"]["Content-Type"] = "application/json"

            async with session.request(method, url, **kwargs) as response:
                # Handle HTTP 402 auto-payment
                if response.status == 402 and _http402_handler:
                    response = await _http402_handler.handle_response(
                        response, session, method, url, **kwargs
                    )

                # Read response body (limit to 100KB)
                response_body = await response.text()
                if len(response_body) > 102400:
                    response_body = response_body[:102400] + "\n... (truncated at 100KB)"

                result_data = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "body": response_body,
                }

                return ToolResult(
                    success=200 <= response.status < 300,
                    output=f"HTTP {response.status}\n{response_body}",
                    data=result_data,
                )

    except aiohttp.ClientError as e:
        return ToolResult(success=False, error=f"HTTP error: {e}")
    except Exception as e:
        return ToolResult(success=False, error=str(e))
