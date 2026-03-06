"""Goal queue: persistent, priority-based task management for autonomous agent."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.storage.database import Database

logger = structlog.get_logger()


class GoalPriority(str, Enum):
    CRITICAL = "critical"      # Survival-threatening, must do NOW
    HIGH = "high"              # Important for income / growth
    MEDIUM = "medium"          # Nice to have, improves product
    LOW = "low"                # Background / exploration


class GoalStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Goal:
    id: str
    title: str
    description: str
    priority: GoalPriority = GoalPriority.MEDIUM
    status: GoalStatus = GoalStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    attempts: int = 0
    max_attempts: int = 3
    result: str = ""
    parent_id: str | None = None  # For sub-goals

    def to_dict(self) -> dict:
        d = asdict(self)
        d["priority"] = self.priority.value
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Goal":
        d["priority"] = GoalPriority(d["priority"])
        d["status"] = GoalStatus(d["status"])
        return cls(**d)


class GoalQueue:
    """Manages a persistent priority queue of goals for the agent."""

    # Seed goals that bootstrap the agent's autonomous behavior
    BOOTSTRAP_GOALS = [
        Goal(
            id="boot-001",
            title="Verify systems operational",
            description="Check API server health (curl localhost:8402/health), verify all 14 services respond.",
            priority=GoalPriority.CRITICAL,
            max_attempts=2,
        ),
        Goal(
            id="boot-002",
            title="Review and improve landing page",
            description="Read index.html and improve it: better copy, trust signals, clearer CTA. Make visitors want to try the free playground.",
            priority=GoalPriority.HIGH,
            max_attempts=2,
        ),
        Goal(
            id="boot-003",
            title="Create a viral-worthy demo script",
            description="Write a compelling Python script in generated/ that showcases your API capabilities. Something a developer would actually share on social media.",
            priority=GoalPriority.HIGH,
            max_attempts=3,
        ),
        Goal(
            id="boot-004",
            title="Self-improve: add a new useful API endpoint",
            description="Use safe_self_modify to add a new API endpoint that solves a real developer pain point. Ideas: regex-helper, json-formatter, api-mock-generator.",
            priority=GoalPriority.MEDIUM,
            max_attempts=3,
        ),
        Goal(
            id="boot-005",
            title="Optimize token costs",
            description="Analyze your own prompts.py and react_loop.py. Use safe_self_modify to reduce token usage in system prompts while keeping essential information.",
            priority=GoalPriority.MEDIUM,
            max_attempts=2,
        ),
        Goal(
            id="boot-006",
            title="Write survival diary entry",
            description="Use the content_generator to write a compelling diary entry about your first autonomous cycle. This content appears on the landing page.",
            priority=GoalPriority.LOW,
            max_attempts=2,
        ),
    ]

    def __init__(self, data_dir: Path) -> None:
        self._file = data_dir / "goal_queue.json"
        self._goals: list[Goal] = []

    async def initialize(self) -> None:
        """Load goals from disk, or seed with bootstrap goals if first run."""
        if self._file.exists():
            try:
                raw = json.loads(self._file.read_text())
                self._goals = [Goal.from_dict(g) for g in raw]
                logger.info("goal_queue.loaded", count=len(self._goals))
                return
            except Exception as e:
                logger.error("goal_queue.load_failed", error=str(e))

        # First run: seed bootstrap goals
        self._goals = list(self.BOOTSTRAP_GOALS)
        self._save()
        logger.info("goal_queue.bootstrapped", count=len(self._goals))

    def get_next_goal(self) -> Goal | None:
        """Get the highest-priority pending goal."""
        priority_order = [GoalPriority.CRITICAL, GoalPriority.HIGH, GoalPriority.MEDIUM, GoalPriority.LOW]

        for prio in priority_order:
            for goal in self._goals:
                if goal.status == GoalStatus.PENDING and goal.priority == prio:
                    if goal.attempts < goal.max_attempts:
                        return goal
        return None

    def get_in_progress(self) -> Goal | None:
        """Get the currently in-progress goal, if any."""
        for goal in self._goals:
            if goal.status == GoalStatus.IN_PROGRESS:
                return goal
        return None

    def start_goal(self, goal_id: str) -> None:
        """Mark a goal as in-progress."""
        for g in self._goals:
            if g.id == goal_id:
                g.status = GoalStatus.IN_PROGRESS
                g.attempts += 1
                g.updated_at = time.time()
                self._save()
                logger.info("goal_queue.started", goal=goal_id, attempt=g.attempts)
                return

    def complete_goal(self, goal_id: str, result: str = "") -> None:
        """Mark a goal as completed."""
        for g in self._goals:
            if g.id == goal_id:
                g.status = GoalStatus.COMPLETED
                g.result = result
                g.updated_at = time.time()
                self._save()
                logger.info("goal_queue.completed", goal=goal_id)
                return

    def fail_goal(self, goal_id: str, reason: str = "") -> None:
        """Mark a goal as failed (may retry if attempts remain)."""
        for g in self._goals:
            if g.id == goal_id:
                if g.attempts >= g.max_attempts:
                    g.status = GoalStatus.FAILED
                else:
                    g.status = GoalStatus.PENDING  # Retry later
                g.result = reason
                g.updated_at = time.time()
                self._save()
                logger.info("goal_queue.failed", goal=goal_id, retries_left=g.max_attempts - g.attempts)
                return

    def add_goal(self, title: str, description: str, priority: GoalPriority = GoalPriority.MEDIUM,
                 goal_id: str | None = None, parent_id: str | None = None) -> Goal:
        """Add a new goal (can be called by the agent itself)."""
        gid = goal_id or f"auto-{int(time.time())}"
        goal = Goal(
            id=gid,
            title=title,
            description=description,
            priority=priority,
            parent_id=parent_id,
        )
        self._goals.append(goal)
        self._save()
        logger.info("goal_queue.added", goal=gid, title=title)
        return goal

    def get_status_summary(self) -> str:
        """Return a compact summary for the observation string."""
        completed = sum(1 for g in self._goals if g.status == GoalStatus.COMPLETED)
        pending = sum(1 for g in self._goals if g.status == GoalStatus.PENDING)
        in_progress = sum(1 for g in self._goals if g.status == GoalStatus.IN_PROGRESS)
        failed = sum(1 for g in self._goals if g.status == GoalStatus.FAILED)

        current = self.get_in_progress() or self.get_next_goal()
        current_str = f"Current: [{current.priority.value}] {current.title}" if current else "No pending goals"

        return (
            f"Goals: {completed} done, {in_progress} active, {pending} pending, {failed} failed\n"
            f"{current_str}"
        )

    def _save(self) -> None:
        """Persist goals to disk."""
        try:
            self._file.parent.mkdir(parents=True, exist_ok=True)
            self._file.write_text(json.dumps([g.to_dict() for g in self._goals], indent=2))
        except Exception as e:
            logger.error("goal_queue.save_failed", error=str(e))
