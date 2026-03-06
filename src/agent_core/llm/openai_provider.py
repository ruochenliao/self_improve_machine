"""OpenAI LLM provider adapter."""

from __future__ import annotations

import json

import structlog
from openai import AsyncOpenAI

from .base import LLMProvider, LLMResponse, TokenUsage, ToolCall

logger = structlog.get_logger()

# Pricing per 1M tokens (input/output) — covers all CloseAI-proxied models
_PRICING = {
    # OpenAI GPT-4o family
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o-2024-11-20": (2.50, 10.00),
    "chatgpt-4o-latest": (2.50, 10.00),
    # OpenAI GPT-4.1
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "gpt-4.1-nano": (0.10, 0.40),
    # OpenAI GPT-5 family
    "gpt-5": (5.00, 15.00),
    "gpt-5-mini": (1.00, 4.00),
    "gpt-5-nano": (0.25, 1.00),
    # OpenAI o-series reasoning
    "o3": (10.00, 40.00),
    "o3-mini": (1.10, 4.40),
    "o4-mini": (1.10, 4.40),
    "o1": (15.00, 60.00),
    # Legacy
    "gpt-3.5-turbo": (0.50, 1.50),
    "gpt-4-turbo": (10.00, 30.00),
    # Claude via OpenAI-compatible proxy
    "claude-opus-4-20250514": (15.00, 75.00),
    "claude-opus-4-6": (15.00, 75.00),
    "claude-opus-4-5": (15.00, 75.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-sonnet-4-20250514": (3.00, 15.00),
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "claude-3-7-sonnet-latest": (3.00, 15.00),
    "claude-haiku-4-5": (0.80, 4.00),
    "claude-3-5-haiku-latest": (0.80, 4.00),
    "claude-3-haiku-20240307": (0.25, 1.25),
    # DeepSeek (very cheap — survival critical mode)
    "deepseek-chat": (0.14, 0.28),
    "deepseek-reasoner": (0.55, 2.19),
    # Gemini
    "gemini-2.5-flash": (0.15, 0.60),
    "gemini-2.5-flash-lite": (0.05, 0.20),
    "gemini-2.5-pro": (1.25, 10.00),
    "gemini-2.0-flash": (0.10, 0.40),
    "gemini-3-flash-preview": (0.10, 0.40),
    "gemini-3-pro-preview": (1.25, 10.00),
    # Grok
    "grok-3-beta": (3.00, 15.00),
    "grok-3-mini-beta": (0.30, 0.50),
    # 通义千问 Qwen (DashScope, CNY→USD ≈ /7.2)
    "qwen-turbo": (0.04, 0.08),       # ¥0.3/¥0.6 per 1M tokens
    "qwen-plus": (0.11, 0.39),        # ¥0.8/¥2.0 per 1M tokens (free until 2026 年某日)
    "qwen-max": (0.56, 2.22),         # ¥4.0/¥16.0 per 1M tokens
    "qwen-long": (0.07, 0.28),        # ¥0.5/¥2.0 per 1M tokens
    "qwen-turbo-latest": (0.04, 0.08),
    "qwen-plus-latest": (0.11, 0.39),
    "qwen-max-latest": (0.56, 2.22),
    # Qwen3 series
    "qwen3-max": (0.56, 2.22),         # 千问3旗舰
    "qwen3-coder-plus": (0.28, 1.11),  # 千问3代码专用
    # QwQ reasoning models (stream-only)
    "qwq-plus": (0.28, 1.11),          # ¥2.0/¥8.0 per 1M tokens
}

# Default fallback pricing for unknown models
_DEFAULT_PRICING = (2.00, 8.00)

# Models that require stream=True (DashScope limitation)
_STREAM_ONLY_MODELS = {"qwq-plus", "qwq-plus-2025-03-05"}


class OpenAIProvider(LLMProvider):
    """OpenAI-compatible API adapter. Works with OpenAI, CloseAI proxy, and any compatible endpoint."""

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

        # Some models (e.g. qwq-plus) only support stream mode
        if self.model_name in _STREAM_ONLY_MODELS:
            return await self._stream_chat(kwargs)

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

    async def _stream_chat(self, kwargs: dict) -> LLMResponse:
        """Stream-based chat for models that only support stream mode (e.g. qwq-plus)."""
        kwargs["stream"] = True
        kwargs["stream_options"] = {"include_usage": True}

        content_parts: list[str] = []
        tool_calls_map: dict[int, dict] = {}
        finish_reason = ""
        prompt_tokens = 0
        completion_tokens = 0

        async for chunk in await self._client.chat.completions.create(**kwargs):
            if not chunk.choices and chunk.usage:
                prompt_tokens = chunk.usage.prompt_tokens or 0
                completion_tokens = chunk.usage.completion_tokens or 0
                continue

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta
            if chunk.choices[0].finish_reason:
                finish_reason = chunk.choices[0].finish_reason

            if delta.content:
                content_parts.append(delta.content)

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index
                    if idx not in tool_calls_map:
                        tool_calls_map[idx] = {"id": tc.id or "", "name": "", "arguments": ""}
                    if tc.id:
                        tool_calls_map[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_calls_map[idx]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls_map[idx]["arguments"] += tc.function.arguments

        tool_calls: list[ToolCall] = []
        for _idx in sorted(tool_calls_map.keys()):
            tc_data = tool_calls_map[_idx]
            try:
                args = json.loads(tc_data["arguments"])
            except (json.JSONDecodeError, TypeError):
                args = {"raw": tc_data["arguments"]}
            tool_calls.append(ToolCall(id=tc_data["id"], name=tc_data["name"], arguments=args))

        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost_usd=self.estimate_cost(prompt_tokens, completion_tokens),
        )

        logger.info(
            "llm.openai.stream_chat",
            model=self.model_name,
            tokens=usage.total_tokens,
            cost_usd=f"{usage.total_cost_usd:.6f}",
        )

        return LLMResponse(
            content="".join(content_parts),
            tool_calls=tool_calls,
            usage=usage,
            model=self.model_name,
            finish_reason=finish_reason,
        )

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        input_price, output_price = _PRICING.get(self.model_name, _DEFAULT_PRICING)
        return (prompt_tokens * input_price + completion_tokens * output_price) / 1_000_000

    async def ping(self) -> bool:
        try:
            await self._client.models.list()
            return True
        except Exception:
            return False
