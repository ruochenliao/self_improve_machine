"""Scaling manager: auto-scaling decisions based on balance and load."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.infrastructure.cloud_provider import CloudProviderRegistry
    from agent_core.survival.state_machine import SurvivalStateMachine, SurvivalTier

logger = structlog.get_logger()


class ScalingManager:
    """Manages auto-scaling decisions for cloud infrastructure."""

    def __init__(
        self,
        cloud_registry: CloudProviderRegistry,
        state_machine: SurvivalStateMachine,
        scale_up_balance_threshold: float = 100.0,
        scale_down_balance_threshold: float = 20.0,
        max_instances: int = 5,
    ) -> None:
        self._cloud_registry = cloud_registry
        self._state_machine = state_machine
        self._scale_up_threshold = scale_up_balance_threshold
        self._scale_down_threshold = scale_down_balance_threshold
        self._max_instances = max_instances

    async def evaluate(self) -> dict:
        """Evaluate current state and recommend scaling action."""
        from agent_core.survival.state_machine import SurvivalTier

        balance = self._state_machine.current_balance_usd
        tier = self._state_machine.current_tier

        recommendation = {
            "action": "none",
            "reason": "",
            "balance": balance,
            "tier": tier.value,
        }

        # In critical or dead state, consider scaling down
        if tier in (SurvivalTier.CRITICAL, SurvivalTier.DEAD):
            recommendation["action"] = "scale_down"
            recommendation["reason"] = "Balance critical, destroy non-essential instances"
            return recommendation

        # Check current instance count
        try:
            provider = self._cloud_registry.get_default()
            instances = await provider.list_instances()
            running = [i for i in instances if i.status == "running"]
            instance_count = len(running)
        except Exception:
            instance_count = 0

        # Scale up: high balance + room for more instances
        if balance >= self._scale_up_threshold and instance_count < self._max_instances:
            recommendation["action"] = "scale_up"
            recommendation["reason"] = f"Balance ${balance:.2f} above threshold, {instance_count}/{self._max_instances} instances"

        # Scale down: low balance
        elif balance < self._scale_down_threshold and instance_count > 0:
            recommendation["action"] = "scale_down"
            recommendation["reason"] = f"Balance ${balance:.2f} below threshold, {instance_count} instances running"

        return recommendation

    async def execute_recommendation(self, recommendation: dict) -> bool:
        """Execute a scaling recommendation."""
        action = recommendation.get("action", "none")

        if action == "none":
            return True

        try:
            provider = self._cloud_registry.get_default()

            if action == "scale_up":
                info = await provider.create_instance({})
                logger.info("scaling.up", instance_id=info.instance_id)
                return True

            elif action == "scale_down":
                instances = await provider.list_instances()
                running = [i for i in instances if i.status == "running"]
                if running:
                    # Destroy the most recently created (last in list)
                    target = running[-1]
                    await provider.destroy_instance(target.instance_id)
                    logger.info("scaling.down", instance_id=target.instance_id)
                return True

        except Exception as e:
            logger.error("scaling.failed", action=action, error=str(e))
            return False

        return True
