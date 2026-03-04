"""Audit logger — immutable record of all self-modifications."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import structlog

log = structlog.get_logger()


class AuditAction(str, Enum):
    """Types of auditable actions."""
    SELF_MODIFY = "self_modify"
    RESTART = "restart"
    ROLLBACK = "rollback"
    PAYMENT_SENT = "payment_sent"
    PAYMENT_RECEIVED = "payment_received"
    INFRASTRUCTURE_CREATE = "infra_create"
    INFRASTRUCTURE_DESTROY = "infra_destroy"
    REPLICATE = "replicate"
    CONSTITUTION_CHECK = "constitution_check"
    CREATOR_PAYOUT = "creator_payout"
    CONFIG_CHANGE = "config_change"
    TOOL_EXECUTION = "tool_execution"


@dataclass
class AuditEntry:
    """Single audit log entry."""
    timestamp: float
    action: str
    description: str
    details: dict[str, Any] = field(default_factory=dict)
    success: bool = True
    actor: str = "agent"  # "agent", "creator", "system"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


class AuditLogger:
    """
    Append-only audit logger.
    
    Writes to both:
    - SQLite database (via storage module) for querying
    - JSONL file for tamper-evident backup
    """

    def __init__(self, db=None, log_dir: Path | str | None = None):
        self.db = db
        self.log_dir = Path(log_dir) if log_dir else Path("data/audit")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self.log_dir / "audit.jsonl"

    async def log_action(
        self,
        action: AuditAction,
        description: str,
        details: dict[str, Any] | None = None,
        success: bool = True,
        actor: str = "agent",
    ) -> AuditEntry:
        """Record an auditable action."""
        entry = AuditEntry(
            timestamp=time.time(),
            action=action.value,
            description=description,
            details=details or {},
            success=success,
            actor=actor,
        )

        # Write to JSONL file (append-only)
        with open(self._log_file, "a", encoding="utf-8") as f:
            f.write(entry.to_json() + "\n")

        # Write to database if available
        if self.db:
            try:
                await self.db.execute(
                    """INSERT INTO audit_log (timestamp, action, description, details, success, actor)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        entry.timestamp,
                        entry.action,
                        entry.description,
                        json.dumps(entry.details, ensure_ascii=False),
                        entry.success,
                        entry.actor,
                    ),
                )
            except Exception as e:
                log.error("audit.db_write_failed", error=str(e))

        log.info(
            "audit.recorded",
            action=entry.action,
            description=entry.description[:80],
            success=entry.success,
        )
        return entry

    async def get_recent(self, n: int = 50, action: Optional[str] = None) -> list[dict[str, Any]]:
        """Get recent audit entries from JSONL file."""
        if not self._log_file.exists():
            return []

        entries = []
        with open(self._log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if action and entry.get("action") != action:
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        return entries[-n:]

    async def get_stats(self) -> dict[str, Any]:
        """Get audit statistics."""
        entries = await self.get_recent(n=10000)
        if not entries:
            return {"total": 0}

        action_counts: dict[str, int] = {}
        success_count = 0
        for e in entries:
            a = e.get("action", "unknown")
            action_counts[a] = action_counts.get(a, 0) + 1
            if e.get("success"):
                success_count += 1

        return {
            "total": len(entries),
            "success_rate": success_count / len(entries) if entries else 0,
            "by_action": action_counts,
            "earliest": entries[0].get("timestamp", 0),
            "latest": entries[-1].get("timestamp", 0),
        }
