"""Heartbeat daemon: periodic health checks and balance monitoring."""

from __future__ import annotations

import asyncio
import shutil
import time
from pathlib import Path
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.survival.balance_monitor import BalanceMonitor
    from agent_core.survival.state_machine import SurvivalStateMachine

logger = structlog.get_logger()


class HeartbeatDaemon:
    """Background heartbeat daemon that performs health checks and triggers balance monitoring."""

    def __init__(
        self,
        state_machine: SurvivalStateMachine,
        balance_monitor: BalanceMonitor,
        data_dir: Path,
    ) -> None:
        self._state_machine = state_machine
        self._balance_monitor = balance_monitor
        self._heartbeat_file = data_dir / "watchdog.heartbeat"
        self._running = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the heartbeat loop as a background task."""
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("heartbeat.started")

    async def stop(self) -> None:
        """Stop the heartbeat loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("heartbeat.stopped")

    async def _loop(self) -> None:
        while self._running:
            try:
                await self._beat()
                interval = self._state_machine.get_current_config().heartbeat_interval_sec
                if interval <= 0:
                    logger.warning("heartbeat.dead_state")
                    break
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("heartbeat.error", error=str(e))
                await asyncio.sleep(5)

    async def _beat(self) -> None:
        """Perform a single heartbeat: health checks + balance update."""
        # Write heartbeat timestamp for watchdog
        self._heartbeat_file.parent.mkdir(parents=True, exist_ok=True)
        self._heartbeat_file.write_text(str(time.time()))

        # Run balance check
        await self._balance_monitor.check()

        # Disk space check
        disk = shutil.disk_usage("/")
        free_gb = disk.free / (1024**3)
        if free_gb < 1.0:
            logger.warning("heartbeat.low_disk", free_gb=f"{free_gb:.2f}")

        logger.debug(
            "heartbeat.beat",
            tier=self._state_machine.current_tier.value,
            balance=self._balance_monitor.balance,
        )
