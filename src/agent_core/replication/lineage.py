"""Lineage tracking for self-replicating agents."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

import structlog

log = structlog.get_logger()


@dataclass
class LineageRecord:
    """Records the genealogy of an agent instance."""
    instance_id: str = ""
    parent_id: Optional[str] = None
    generation: int = 0
    created_at: float = 0.0
    creator: str = "human"  # "human" for gen-0, "agent" for replicas
    birth_reason: str = ""
    source_commit: str = ""
    host: str = "localhost"
    children: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.instance_id:
            self.instance_id = str(uuid.uuid4())[:12]
        if not self.created_at:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class LineageTracker:
    """Tracks agent lineage across replications."""

    def __init__(self, db=None):
        self.db = db
        self._current: Optional[LineageRecord] = None

    @property
    def current(self) -> Optional[LineageRecord]:
        return self._current

    async def initialize(
        self,
        parent_id: Optional[str] = None,
        generation: int = 0,
        source_commit: str = "",
        host: str = "localhost",
    ) -> LineageRecord:
        """Initialize lineage for this instance."""
        self._current = LineageRecord(
            parent_id=parent_id,
            generation=generation,
            creator="human" if generation == 0 else "agent",
            birth_reason="genesis" if generation == 0 else "replication",
            source_commit=source_commit,
            host=host,
        )
        log.info(
            "lineage.initialized",
            instance_id=self._current.instance_id,
            generation=generation,
            parent=parent_id,
        )

        # Persist to DB
        if self.db:
            try:
                await self.db.execute(
                    """INSERT INTO lineage (instance_id, parent_id, generation, created_at, creator, host)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        self._current.instance_id,
                        self._current.parent_id,
                        self._current.generation,
                        self._current.created_at,
                        self._current.creator,
                        self._current.host,
                    ),
                )
            except Exception as e:
                log.error("lineage.db_save_failed", error=str(e))

        return self._current

    async def record_child(self, child_id: str) -> None:
        """Record that this instance spawned a child."""
        if self._current:
            self._current.children.append(child_id)
            log.info(
                "lineage.child_spawned",
                parent=self._current.instance_id,
                child=child_id,
            )
