"""OpenAI LLM provider adapter."""

from __future__ import annotations

import json

import structlog
from openai import AsyncOpenAI

from .base import LLMProvider, LLMResponse, TokenUsage, ToolCall

logger = structlog.get_logger()

# Pricing per 1M tokens (input/output) as of 2024
_PRICING = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-3.5-turbo": (0.50, 1.50),
}


class OpenAIProvider(LLMProvider):
    """OpenAI API adapter supporting gpt-4o, gpt-4o-mini, gpt-3.5-turbo."""

    provider_name = "openai"

    def __init__(self, api_key: str, model_name: str = "gpt-4o", base_url: str = "") -> None:
        self.model_name = model_name
        kwargs: dict = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        self._client = AsyncOpenAI(**kwargs)

    async def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        kwargs: dict = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = [
                {"type": "function", "function": t} for t in tools
            ]
            kwargs["tool_choice"] = "auto"

        response = await self._client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        # Parse tool calls
        tool_calls: list[ToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {"raw": tc.function.arguments}
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=args,
                ))

        usage = TokenUsage(
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            total_cost_usd=self.estimate_cost(
                response.usage.prompt_tokens if response.usage else 0,
                response.usage.completion_tokens if response.usage else 0,
            ),
        )

        logger.info(
            "llm.openai.chat",
            model=self.model_name,
            tokens=usage.total_tokens,
            cost_usd=f"{usage.total_cost_usd:.6f}",
        )

        return LLMResponse(
            content=choice.message.content or "",
            tool_calls=tool_calls,
            usage=usage,
            model=self.model_name,
            finish_reason=choice.finish_reason or "",
        )

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = _PRICING.get(self.model_name, (2.50, 10.00))
        return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000

    async def ping(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False
