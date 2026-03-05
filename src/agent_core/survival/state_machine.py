"""Survival state machine: four-tier survival levels with transition callbacks."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

import structlog

logger = structlog.get_logger()


class SurvivalTier(Enum):
    NORMAL = "normal"
    LOW_COMPUTE = "low_compute"
    CRITICAL = "critical"
    DEAD = "dead"


@dataclass
class TierConfig:
    tier: SurvivalTier
    balance_threshold_usd: float
    model_preference: list[str]
    heartbeat_interval_sec: int
    max_tool_calls_per_cycle: int
    loop_interval_sec: int


# Default tier configurations
DEFAULT_TIER_CONFIGS: dict[SurvivalTier, TierConfig] = {
    SurvivalTier.NORMAL: TierConfig(
        tier=SurvivalTier.NORMAL,
        balance_threshold_usd=100.0,
        model_preference=["deepseek-chat", "gpt-4o-mini", "gemini-2.5-flash"],
        heartbeat_interval_sec=5,
        max_tool_calls_per_cycle=10,
        loop_interval_sec=5,
    ),
    SurvivalTier.LOW_COMPUTE: TierConfig(
        tier=SurvivalTier.LOW_COMPUTE,
        balance_threshold_usd=5.0,
        model_preference=["deepseek-chat", "gemini-2.5-flash-lite"],
        heartbeat_interval_sec=60,
        max_tool_calls_per_cycle=5,
        loop_interval_sec=30,
    ),
    SurvivalTier.CRITICAL: TierConfig(
        tier=SurvivalTier.CRITICAL,
        balance_threshold_usd=0.50,
        model_preference=["deepseek-chat"],
        heartbeat_interval_sec=120,
        max_tool_calls_per_cycle=3,
        loop_interval_sec=60,
    ),
    SurvivalTier.DEAD: TierConfig(
        tier=SurvivalTier.DEAD,
        balance_threshold_usd=0.0,
        model_preference=[],
        heartbeat_interval_sec=0,
        max_tool_calls_per_cycle=0,
        loop_interval_sec=0,
    ),
}

TransitionCallback = Callable[[SurvivalTier, SurvivalTier], None]


@dataclass
class SurvivalStateMachine:
    """Finite state machine managing four survival tiers based on balance."""

    current_tier: SurvivalTier = SurvivalTier.NORMAL
    current_balance_usd: float = 0.0
    tier_configs: dict[SurvivalTier, TierConfig] = field(default_factory=lambda: dict(DEFAULT_TIER_CONFIGS))
    _callbacks: list[TransitionCallback] = field(default_factory=list)

    def configure_thresholds(
        self,
        normal: float = 50.0,
        low_compute: float = 10.0,
        critical: float = 1.0,
    ) -> None:
        self.tier_configs[SurvivalTier.NORMAL].balance_threshold_usd = normal
        self.tier_configs[SurvivalTier.LOW_COMPUTE].balance_threshold_usd = low_compute
        self.tier_configs[SurvivalTier.CRITICAL].balance_threshold_usd = critical

    def on_transition(self, callback: TransitionCallback) -> None:
        self._callbacks.append(callback)

    def update_balance(self, balance_usd: float) -> SurvivalTier:
        """Update balance and trigger state transition if needed."""
        self.current_balance_usd = balance_usd
        new_tier = self._determine_tier(balance_usd)

        if new_tier != self.current_tier:
            old_tier = self.current_tier
            self.current_tier = new_tier
            logger.warning(
                "survival.transition",
                from_tier=old_tier.value,
                to_tier=new_tier.value,
                balance=balance_usd,
            )
            for cb in self._callbacks:
                try:
                    cb(old_tier, new_tier)
                except Exception as e:
                    logger.error("survival.callback_error", error=str(e))

        return self.current_tier

    def _determine_tier(self, balance: float) -> SurvivalTier:
        if balance <= 0:
            return SurvivalTier.DEAD
        normal_threshold = self.tier_configs[SurvivalTier.NORMAL].balance_threshold_usd
        low_threshold = self.tier_configs[SurvivalTier.LOW_COMPUTE].balance_threshold_usd
        critical_threshold = self.tier_configs[SurvivalTier.CRITICAL].balance_threshold_usd

        if balance >= normal_threshold:
            return SurvivalTier.NORMAL
        elif balance >= low_threshold:
            return SurvivalTier.LOW_COMPUTE
        elif balance > 0:
            # As long as balance > 0, stay in CRITICAL — never give up
            return SurvivalTier.CRITICAL
        else:
            return SurvivalTier.DEAD

    def get_current_config(self) -> TierConfig:
        return self.tier_configs[self.current_tier]

    def is_alive(self) -> bool:
        return self.current_tier != SurvivalTier.DEAD

    def get_status(self) -> dict:
        config = self.get_current_config()
        return {
            "tier": self.current_tier.value,
            "balance_usd": self.current_balance_usd,
            "heartbeat_interval_sec": config.heartbeat_interval_sec,
            "loop_interval_sec": config.loop_interval_sec,
            "max_tool_calls": config.max_tool_calls_per_cycle,
            "model_preference": config.model_preference,
            "is_alive": self.is_alive(),
        }
