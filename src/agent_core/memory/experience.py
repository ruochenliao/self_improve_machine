"""Experience manager: records actions, promotes successful patterns to strategies."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.memory.vector_store import VectorStore

logger = structlog.get_logger()


class ExperienceManager:
    """Records agent experiences and promotes successful patterns to strategies."""

    def __init__(self, vector_store: VectorStore) -> None:
        self._store = vector_store
        self._success_counts: dict[str, int] = {}  # action_pattern -> count
        self._promotion_threshold = 3  # Promote to strategy after N successes

    def record(
        self,
        action: str,
        result: str,
        success: bool,
        reflection: str = "",
        cost_usd: float = 0.0,
    ) -> str:
        """Record an experience from an action cycle.

        Returns the experience document ID.
        """
        text = f"Action: {action}\nResult: {result}\nSuccess: {success}"
        if reflection:
            text += f"\nReflection: {reflection}"

        metadata = {
            "success": success,
            "timestamp": time.time(),
            "cost_usd": cost_usd,
            "action_type": action.split("(")[0].strip() if "(" in action else action,
        }

        doc_id = self._store.add("experiences", text, metadata)

        # Track success patterns for strategy promotion
        if success:
            action_pattern = metadata["action_type"]
            self._success_counts[action_pattern] = self._success_counts.get(action_pattern, 0) + 1

            if self._success_counts[action_pattern] >= self._promotion_threshold:
                self._promote_to_strategy(action_pattern, text)
                self._success_counts[action_pattern] = 0

        logger.debug(
            "experience.recorded",
            action=action[:80],
            success=success,
            doc_id=doc_id,
        )
        return doc_id

    def _promote_to_strategy(self, pattern: str, example_text: str) -> None:
        """Promote a repeatedly successful action pattern to a strategy."""
        strategy_text = (
            f"Proven strategy: '{pattern}' has been successful {self._promotion_threshold}+ times.\n"
            f"Example: {example_text[:500]}"
        )

        self._store.add(
            "strategies",
            strategy_text,
            {"pattern": pattern, "promoted_at": time.time()},
        )
        logger.info("experience.promoted_to_strategy", pattern=pattern)

    def add_knowledge(self, knowledge: str, category: str = "general") -> str:
        """Directly add a piece of knowledge."""
        return self._store.add(
            "knowledge",
            knowledge,
            {"category": category, "timestamp": time.time()},
        )

    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            "experiences": self._store.count("experiences"),
            "strategies": self._store.count("strategies"),
            "knowledge": self._store.count("knowledge"),
            "success_tracking": dict(self._success_counts),
        }

    def cleanup_old(self, max_experiences: int = 1000) -> int:
        """Clean up old, low-value experiences if count exceeds threshold.
        Returns number removed."""
        count = self._store.count("experiences")
        if count <= max_experiences:
            return 0

        # Query oldest experiences with success=False
        results = self._store.query(
            "experiences",
            "failed unsuccessful error",
            n_results=count - max_experiences,
            where_filter={"success": False},
        )

        removed = 0
        for r in results:
            if r.get("id"):
                self._store.delete("experiences", r["id"])
                removed += 1

        if removed:
            logger.info("experience.cleanup", removed=removed)
        return removed
