"""Anthropic LLM provider adapter."""

from __future__ import annotations

import structlog
from anthropic import AsyncAnthropic

from .base import LLMProvider, LLMResponse, TokenUsage, ToolCall

logger = structlog.get_logger()

# Pricing per 1M tokens (input/output)
_PRICING = {
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "claude-3-haiku-20240307": (0.25, 1.25),
}


class AnthropicProvider(LLMProvider):
    """Anthropic API adapter supporting Claude models."""

    provider_name = "anthropic"

    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022") -> None:
        self.model_name = model_name
        self._client = AsyncAnthropic(api_key=api_key)

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        # Extract system message
        system_content = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_content += msg["content"] + "\n"
            else:
                chat_messages.append(msg)

        kwargs: dict = {
            "model": self.model_name,
            "messages": chat_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if system_content:
            kwargs["system"] = system_content.strip()

        if tools:
            kwargs["tools"] = [
                {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "input_schema": t.get("parameters", {}),
                }
                for t in tools
            ]

        response = await self._client.messages.create(**kwargs)

        # Parse response content and tool calls
        content_parts: list[str] = []
        tool_calls: list[ToolCall] = []

        for block in response.content:
            if block.type == "text":
                content_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(
                    id=block.id,
                    name=block.name,
                    arguments=block.input if isinstance(block.input, dict) else {},
                ))

        usage = TokenUsage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            total_cost_usd=self.estimate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens,
            ),
        )

        logger.info(
            "llm.anthropic.chat",
            model=self.model_name,
            tokens=usage.total_tokens,
            cost_usd=f"{usage.total_cost_usd:.6f}",
        )

        return LLMResponse(
            content="\n".join(content_parts),
            tool_calls=tool_calls,
            usage=usage,
            model=self.model_name,
            finish_reason=response.stop_reason or "",
        )

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = _PRICING.get(self.model_name, (3.00, 15.00))
        return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000

    async def ping(self) -> bool:
        try:
            await self._client.messages.create(
                model=self.model_name,
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}],
            )
            return True
        except Exception:
            return False
