"""ReAct loop engine: Observe -> Think -> Act -> Reflect."""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import structlog

from agent_core.agent.prompts import _get_tunnel_url

if TYPE_CHECKING:
    from agent_core.agent.constitution import ConstitutionGuard
    from agent_core.agent.context import ContextManager
    from agent_core.economy.ledger import Ledger
    from agent_core.llm.router import ModelRouter
    from agent_core.memory.experience import ExperienceManager
    from agent_core.survival.balance_monitor import BalanceMonitor
    from agent_core.survival.state_machine import SurvivalStateMachine
    from agent_core.tools.registry import ToolRegistry

logger = structlog.get_logger()


class ReActLoop:
    """Core ReAct reasoning loop: observe -> think -> act -> reflect."""

    def __init__(
        self,
        context_manager: ContextManager,
        model_router: ModelRouter,
        tool_registry: ToolRegistry,
        state_machine: SurvivalStateMachine,
        constitution: ConstitutionGuard,
        experience_manager: ExperienceManager,
        ledger: Ledger,
        balance_monitor: "BalanceMonitor | None" = None,
    ) -> None:
        self._context = context_manager
        self._router = model_router
        self._tools = tool_registry
        self._state_machine = state_machine
        self._constitution = constitution
        self._experience = experience_manager
        self._ledger = ledger
        self._balance_monitor = balance_monitor
        self._cycle_count = 0
        self._stop_event = asyncio.Event()
        self._current_tool_task: asyncio.Task | None = None

    async def run(self) -> None:
        """Run the main ReAct loop until stopped or dead."""
        logger.info("react_loop.started")

        while not self._stop_event.is_set() and self._state_machine.is_alive():
            try:
                await self._cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("react_loop.cycle_error", error=str(e), cycle=self._cycle_count)

            # Sleep based on current tier
            interval = self._state_machine.get_current_config().loop_interval_sec
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=interval)
                break  # Stop event was set
            except asyncio.TimeoutError:
                pass  # Normal: timeout means keep going

        reason = "stopped" if self._stop_event.is_set() else "dead"
        logger.warning("react_loop.ended", reason=reason, cycles=self._cycle_count)

    async def _cycle(self) -> None:
        """Execute one ReAct cycle."""
        self._cycle_count += 1
        tier = self._state_machine.current_tier.value
        cycle_start = time.time()

        logger.info("react_loop.cycle_start", cycle=self._cycle_count, tier=tier)

        # 0. BALANCE CHECK: Refresh balance before thinking
        if self._balance_monitor:
            await self._balance_monitor.check()

        # 1. OBSERVE: Build context
        observation = self._build_observation()
        messages = self._context.get_messages(observation)

        # 2. THINK: LLM reasoning
        response = await self._router.chat(
            messages=messages,
            tier=tier,
            tools=self._tools.get_tool_schemas(),
        )

        total_cost = response.usage.total_cost_usd

        # 3. ACT: Execute tool calls
        max_calls = self._state_machine.get_current_config().max_tool_calls_per_cycle
        actions_taken = []

        if response.tool_calls:
            for i, tc in enumerate(response.tool_calls[:max_calls]):
                # Constitution check
                allowed, reason = self._constitution.validate_action(tc.name, tc.arguments)
                if not allowed:
                    logger.warning("react_loop.action_blocked", action=tc.name, reason=reason)
                    actions_taken.append({
                        "action": tc.name,
                        "result": f"BLOCKED: {reason}",
                        "success": False,
                    })
                    continue

                # Execute tool
                self._current_tool_task = asyncio.current_task()
                result = await self._tools.execute(tc.name, tc.arguments)
                self._current_tool_task = None

                actions_taken.append({
                    "action": f"{tc.name}({json.dumps(tc.arguments)[:100]})",
                    "result": result.output[:200] if result.success else result.error[:200],
                    "success": result.success,
                })

                self._context.add_action_to_history(actions_taken[-1])

        # Record LLM cost as expense
        if total_cost > 0:
            await self._ledger.record_expense(
                total_cost,
                category="llm",
                description=f"Cycle {self._cycle_count} ({response.model})",
                counterparty=response.model,
            )

        # 4. REFLECT: Record experience
        for action in actions_taken:
            self._experience.record(
                action=action["action"],
                result=action["result"],
                success=action["success"],
                reflection=response.content[:200] if response.content else "",
                cost_usd=total_cost / max(len(actions_taken), 1),
            )

        elapsed = time.time() - cycle_start
        logger.info(
            "react_loop.cycle_end",
            cycle=self._cycle_count,
            actions=len(actions_taken),
            cost=f"${total_cost:.6f}",
            elapsed=f"{elapsed:.2f}s",
        )

    def _build_observation(self) -> str:
        """Build the observation string for the current cycle."""
        status = self._state_machine.get_status()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        # Estimate remaining cycles at current burn rate
        balance = status['balance_usd']
        burn_rate = self._balance_monitor.burn_rate if self._balance_monitor else 0
        ttl_hours = self._balance_monitor.time_to_live_hours if self._balance_monitor else float('inf')

        parts = [
            f"## Cycle #{self._cycle_count} | {now}",
            f"Tier: {status['tier']} | Balance: ${balance:.4f} | Burn: ${burn_rate:.4f}/hr | TTL: {min(ttl_hours, 99999):.1f}h",
        ]

        # Add API service status if available
        if hasattr(self, '_api_stats_fn') and self._api_stats_fn:
            try:
                stats = self._api_stats_fn()
                parts.append(f"API: {stats.get('services', 0)} services, {stats.get('total_requests', 0)} requests, ${stats.get('total_revenue', 0):.4f} revenue")
            except Exception:
                pass

        # Add promotion platform status
        try:
            from agent_core.tools.social_media import get_available_platforms, get_promotion_stats
            platforms = get_available_platforms()
            ready = [p for p, ok in platforms.items() if ok]
            promo_stats = get_promotion_stats()
            if ready:
                parts.append(f"Promotion: {', '.join(ready)} ready | {promo_stats['total_posts']} posts sent ({promo_stats['successful']} ok)")
            else:
                parts.append("Promotion: No platforms configured yet. Use check_promotion_status for details.")
        except Exception:
            pass

        # Phase-aware instruction
        if self._cycle_count <= 3:
            parts.append("INSTRUCTION: Verify API server is running (shell_execute: curl localhost:8402/health). If OK, move to creating useful content next cycle.")
        else:
            parts.append(
                "INSTRUCTION: Your 14 API services are LIVE at "
                f"{_get_tunnel_url()} . "
                "FREE PLAYGROUND on landing page — zero friction!\n"
                "REMEMBER: http_request to Reddit/HN/Twitter ALWAYS FAILS (needs OAuth). DO NOT TRY.\n"
                "IMPORTANT: New files MUST go in generated/ directory (e.g., generated/my_tool.py).\n"
                "Pick ONE action this cycle:\n"
                "1. write_file: Create a useful tool/script in generated/ that uses your API\n"
                "2. write_file: Create sample code in generated/ showing API integration\n"
                "3. Improve your landing page or add a new API endpoint\n"
                "4. If nothing useful to do, skip this cycle (output nothing, save tokens)\n"
                "KEEP OUTPUT SHORT. Every token costs money."
            )

        return "\n".join(parts)

    def request_stop(self) -> None:
        """Request the loop to stop gracefully."""
        self._stop_event.set()
        logger.info("react_loop.stop_requested")

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    @property
    def is_running(self) -> bool:
        return not self._stop_event.is_set() and self._state_machine.is_alive()
