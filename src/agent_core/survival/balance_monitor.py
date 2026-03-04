"""Balance monitor: tracks balance, burn rate, and time-to-live prediction."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.economy.ledger import Ledger
    from agent_core.survival.state_machine import SurvivalStateMachine

logger = structlog.get_logger()


class BalanceMonitor:
    """Monitors agent balance, computes burn rate, and predicts survival time."""

    def __init__(self, ledger: Ledger, state_machine: SurvivalStateMachine) -> None:
        self._ledger = ledger
        self._state_machine = state_machine
        self._last_balance: float = 0.0
        self._burn_rate_per_hour: float = 0.0
        self._time_to_live_hours: float = float("inf")

    async def check(self) -> dict:
        """Perform a full balance check: query balance, compute metrics, update state."""
        balance = await self._ledger.get_balance()
        burn_rate = await self._ledger.get_burn_rate(hours=1)

        self._last_balance = balance
        self._burn_rate_per_hour = burn_rate

        if burn_rate > 0:
            self._time_to_live_hours = balance / burn_rate
        else:
            self._time_to_live_hours = float("inf")

        tier = self._state_machine.update_balance(balance)

        status = {
            "balance_usd": balance,
            "burn_rate_per_hour": burn_rate,
            "time_to_live_hours": self._time_to_live_hours,
            "tier": tier.value,
        }

        logger.info("balance.check", **status)
        return status

    @property
    def balance(self) -> float:
        return self._last_balance

    @property
    def burn_rate(self) -> float:
        return self._burn_rate_per_hour

    @property
    def time_to_live_hours(self) -> float:
        return self._time_to_live_hours
