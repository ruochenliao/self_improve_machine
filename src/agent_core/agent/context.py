"""Context manager: assembles complete context for LLM calls."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import structlog

from .prompts import IDENTITY_PROMPT, MEMORY_PROMPT, TOOL_CALLING_PROMPT, get_tier_prompt, _get_tunnel_url

if TYPE_CHECKING:
    from agent_core.identity.identity import IdentityManager
    from agent_core.memory.rag import RAGEngine
    from agent_core.survival.balance_monitor import BalanceMonitor
    from agent_core.survival.state_machine import SurvivalStateMachine
    from agent_core.tools.registry import ToolRegistry

logger = structlog.get_logger()


class ContextManager:
    """Assembles system prompt and context for each ReAct cycle."""

    def __init__(
        self,
        identity: IdentityManager,
        state_machine: SurvivalStateMachine,
        balance_monitor: BalanceMonitor,
        tool_registry: ToolRegistry,
        rag_engine: RAGEngine,
    ) -> None:
        self._identity = identity
        self._state_machine = state_machine
        self._balance_monitor = balance_monitor
        self._tool_registry = tool_registry
        self._rag_engine = rag_engine
        self._action_history: list[dict] = []

    def build_system_prompt(self, observation: str = "") -> str:
        """Build the complete system prompt for the current cycle."""
        identity_info = self._identity.get_identity_summary()
        tier = self._state_machine.current_tier.value
        balance = self._balance_monitor.balance
        burn_rate = self._balance_monitor.burn_rate
        ttl = self._balance_monitor.time_to_live_hours

        # Identity (inject dynamic tunnel URL)
        identity_info["tunnel_url"] = _get_tunnel_url()
        prompt_parts = [
            IDENTITY_PROMPT.format(**identity_info),
        ]

        # Survival tier prompt
        tier_prompt = get_tier_prompt(tier).format(
            balance=balance,
            burn_rate=burn_rate,
            ttl=min(ttl, 99999),
        )
        prompt_parts.append(tier_prompt)

        # Tool schemas
        tool_schemas = json.dumps(self._tool_registry.get_tool_schemas(), indent=2)
        prompt_parts.append(TOOL_CALLING_PROMPT.format(tool_schemas=tool_schemas))

        # RAG memories
        if observation:
            memories = self._rag_engine.retrieve_and_format(observation)
            if memories:
                prompt_parts.append(MEMORY_PROMPT.format(memories=memories))

        # Recent action history (last 5) with anti-repetition warning
        if self._action_history:
            recent = self._action_history[-5:]
            history_text = "## Recent Actions\n\n"

            # Detect repeated failures
            failed_actions = [h.get("action", "").split("(")[0] for h in recent if not h.get("success")]
            repeated = set()
            for a in failed_actions:
                if failed_actions.count(a) >= 2:
                    repeated.add(a)

            for h in recent:
                status = "✓" if h.get("success") else "✗"
                history_text += f"- [{status}] {h.get('action', 'unknown')}: {h.get('result', '')[:100]}\n"

            if repeated:
                history_text += f"\n⚠️ WARNING: You keep repeating failed action(s): {', '.join(repeated)}. STOP doing this. Try a completely different approach — build a new service, modify code, or create content.\n"

            prompt_parts.append(history_text)

        return "\n\n".join(prompt_parts)

    def add_action_to_history(self, action: dict) -> None:
        """Record an action in the rolling history."""
        self._action_history.append(action)
        # Keep only the last 20 actions
        if len(self._action_history) > 20:
            self._action_history = self._action_history[-20:]

    def get_messages(self, observation: str) -> list[dict]:
        """Build the full message list for an LLM call."""
        system_prompt = self.build_system_prompt(observation)
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": observation},
        ]
