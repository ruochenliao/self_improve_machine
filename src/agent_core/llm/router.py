"""Model Router: selects LLM provider based on survival tier with fallback chain."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import structlog

from .base import LLMProvider, LLMResponse

if TYPE_CHECKING:
    from agent_core.config import AgentConfig

logger = structlog.get_logger()


class ModelRouter:
    """Routes LLM calls to the best available provider based on survival tier."""

    def __init__(self) -> None:
        self._providers: dict[str, LLMProvider] = {}
        self._tier_preferences: dict[str, list[str]] = {}
        self._cumulative_cost_usd: float = 0.0
        self._call_count: int = 0

    def register_provider(self, provider: LLMProvider) -> None:
        key = f"{provider.provider_name}:{provider.model_name}"
        self._providers[key] = provider
        logger.info("router.provider_registered", provider=key)

    def set_tier_preferences(self, tier: str, model_keys: list[str]) -> None:
        """Set model preference order for a survival tier.

        Args:
            tier: Survival tier name (normal, low_compute, critical)
            model_keys: Ordered list of 'provider:model' keys
        """
        self._tier_preferences[tier] = model_keys

    def configure_from_config(self, config: AgentConfig) -> None:
        """Build tier preferences from config model lists.

        All models registered through OpenAI-compatible providers (including
        CloseAI proxy for Claude/DeepSeek/Gemini) use 'openai' as provider name.
        """
        # Build a map of model_name -> provider_name from registered providers
        registered: dict[str, str] = {}
        for key in self._providers:
            provider_name, model_name = key.split(":", 1)
            registered[model_name] = provider_name

        for tier_name, model_list in [
            ("normal", config.survival.models.normal),
            ("low_compute", config.survival.models.low_compute),
            ("critical", config.survival.models.critical),
        ]:
            keys = []
            for model in model_list:
                provider = registered.get(model)
                if provider:
                    keys.append(f"{provider}:{model}")
                else:
                    # Assume openai-compatible (CloseAI proxy)
                    keys.append(f"openai:{model}")
            self._tier_preferences[tier_name] = keys

    async def chat(
        self,
        messages: list[dict],
        tier: str = "normal",
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        """Route chat to best available provider for the given tier, with fallback."""
        preferences = self._tier_preferences.get(tier, list(self._providers.keys()))

        last_error: Exception | None = None
        for key in preferences:
            provider = self._providers.get(key)
            if provider is None:
                continue

            try:
                response = await asyncio.wait_for(
                    provider.chat(messages, tools, temperature, max_tokens),
                    timeout=30.0,
                )
                self._cumulative_cost_usd += response.usage.total_cost_usd
                self._call_count += 1
                return response
            except asyncio.TimeoutError:
                logger.warning("router.timeout", provider=key)
                last_error = TimeoutError(f"Provider {key} timed out")
            except Exception as e:
                logger.warning("router.provider_failed", provider=key, error=str(e))
                last_error = e

        # All providers failed - try any available provider as last resort
        for key, provider in self._providers.items():
            if key not in preferences:
                try:
                    response = await asyncio.wait_for(
                        provider.chat(messages, tools, temperature, max_tokens),
                        timeout=30.0,
                    )
                    self._cumulative_cost_usd += response.usage.total_cost_usd
                    self._call_count += 1
                    logger.warning("router.fallback_used", provider=key)
                    return response
                except Exception:
                    continue

        raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")

    @property
    def cumulative_cost_usd(self) -> float:
        return self._cumulative_cost_usd

    @property
    def call_count(self) -> int:
        return self._call_count

    def get_stats(self) -> dict:
        return {
            "total_cost_usd": self._cumulative_cost_usd,
            "total_calls": self._call_count,
            "providers": list(self._providers.keys()),
            "tier_preferences": self._tier_preferences,
        }
