"""Snapshot manager for state persistence across restarts."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

import structlog

log = structlog.get_logger()

SNAPSHOT_DIR = Path("data/snapshots")


@dataclass
class AgentSnapshot:
    """Complete agent state snapshot for restart recovery."""
    timestamp: float = 0.0
    version: str = ""
    survival_state: str = "NORMAL"
    balance: float = 0.0
    current_task: Optional[str] = None
    pending_actions: list[dict[str, Any]] = field(default_factory=list)
    config_overrides: dict[str, Any] = field(default_factory=dict)
    cycle_count: int = 0
    uptime_seconds: float = 0.0
    last_income_source: Optional[str] = None
    active_services: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentSnapshot":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class SnapshotManager:
    """Manages agent state snapshots for graceful restart/recovery."""

    def __init__(self, snapshot_dir: Path | str | None = None):
        self.snapshot_dir = Path(snapshot_dir) if snapshot_dir else SNAPSHOT_DIR
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _snapshot_path(self, name: str = "latest") -> Path:
        return self.snapshot_dir / f"{name}.json"

    async def save(self, snapshot: AgentSnapshot, name: str = "latest") -> Path:
        """Save a snapshot to disk."""
        snapshot.timestamp = time.time()
        path = self._snapshot_path(name)
        data = json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False)
        path.write_text(data, encoding="utf-8")

        # Also save timestamped backup
        ts_name = f"snapshot_{int(snapshot.timestamp)}"
        backup_path = self._snapshot_path(ts_name)
        backup_path.write_text(data, encoding="utf-8")

        log.info("snapshot.saved", path=str(path), state=snapshot.survival_state)
        return path

    async def load(self, name: str = "latest") -> Optional[AgentSnapshot]:
        """Load a snapshot from disk."""
        path = self._snapshot_path(name)
        if not path.exists():
            log.debug("snapshot.not_found", path=str(path))
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            snapshot = AgentSnapshot.from_dict(data)
            age = time.time() - snapshot.timestamp
            log.info(
                "snapshot.loaded",
                path=str(path),
                age_seconds=f"{age:.0f}",
                state=snapshot.survival_state,
            )
            return snapshot
        except Exception as e:
            log.error("snapshot.load_failed", error=str(e))
            return None

    async def list_snapshots(self) -> list[dict[str, Any]]:
        """List all available snapshots with metadata."""
        snapshots = []
        for f in sorted(self.snapshot_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                snapshots.append({
                    "name": f.stem,
                    "timestamp": data.get("timestamp", 0),
                    "state": data.get("survival_state", "unknown"),
                    "balance": data.get("balance", 0),
                })
            except Exception:
                continue
        return snapshots

    async def cleanup(self, keep_latest: int = 10) -> int:
        """Remove old snapshots, keeping the N most recent + 'latest'."""
        files = sorted(
            self.snapshot_dir.glob("snapshot_*.json"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
        removed = 0
        for f in files[keep_latest:]:
            f.unlink()
            removed += 1
        if removed:
            log.info("snapshot.cleanup", removed=removed)
        return removed
