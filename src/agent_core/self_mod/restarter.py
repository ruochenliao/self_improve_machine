"""Self-restart mechanism using os.execv process replacement."""

from __future__ import annotations

import os
import sys
import asyncio
from typing import Optional

import structlog

from .snapshot import SnapshotManager, AgentSnapshot

log = structlog.get_logger()


class Restarter:
    """Handles graceful self-restart via process replacement."""

    def __init__(self, snapshot_manager: SnapshotManager):
        self.snapshot_mgr = snapshot_manager
        self._restart_requested = False
        self._shutdown_callbacks: list = []

    def request_restart(self, reason: str = "self-improvement") -> None:
        """Request a graceful restart."""
        log.info("restarter.restart_requested", reason=reason)
        self._restart_requested = True

    @property
    def restart_pending(self) -> bool:
        return self._restart_requested

    def on_shutdown(self, callback) -> None:
        """Register a callback to run before restart."""
        self._shutdown_callbacks.append(callback)

    async def graceful_restart(self, snapshot: AgentSnapshot) -> None:
        """
        Perform graceful restart:
        1. Save state snapshot
        2. Run shutdown callbacks
        3. Replace process with os.execv
        """
        log.warning("restarter.initiating_restart")

        # Step 1: Save state
        await self.snapshot_mgr.save(snapshot)
        log.info("restarter.state_saved")

        # Step 2: Run shutdown callbacks
        for cb in self._shutdown_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb()
                else:
                    cb()
            except Exception as e:
                log.error("restarter.shutdown_callback_error", error=str(e))

        # Step 3: Process replacement
        log.warning("restarter.execv", executable=sys.executable, args=sys.argv)
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            log.critical("restarter.execv_failed", error=str(e))
            # Fallback: exit and let watchdog handle it
            sys.exit(42)  # Special exit code for watchdog

    async def recover_from_snapshot(self) -> Optional[AgentSnapshot]:
        """Load the latest snapshot for recovery after restart."""
        snapshot = await self.snapshot_mgr.load("latest")
        if snapshot:
            log.info(
                "restarter.recovered",
                state=snapshot.survival_state,
                cycle=snapshot.cycle_count,
            )
        return snapshot
