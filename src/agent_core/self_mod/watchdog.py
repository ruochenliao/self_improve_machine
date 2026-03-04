"""Watchdog process — monitors and restarts the agent if it crashes."""

from __future__ import annotations

import asyncio
import os
import signal
import sys
import time

import structlog

log = structlog.get_logger()

# Exit code that signals intentional restart (not crash)
RESTART_EXIT_CODE = 42
# Exit code for clean shutdown (no restart)
CLEAN_EXIT_CODE = 0


class Watchdog:
    """
    External watchdog that monitors the agent process.
    
    Run as: python -m agent_core.self_mod.watchdog
    
    Behavior:
    - Launches the agent as a subprocess
    - If agent exits with code 42 → restart immediately (self-restart)
    - If agent exits with code 0 → clean shutdown, stop watchdog
    - If agent crashes (other codes) → wait + restart with backoff
    - Max consecutive crashes before giving up: configurable
    """

    def __init__(
        self,
        agent_command: list[str] | None = None,
        max_crashes: int = 5,
        base_backoff: float = 5.0,
        max_backoff: float = 300.0,
    ):
        self.agent_command = agent_command or [
            sys.executable, "-m", "agent_core.main"
        ]
        self.max_crashes = max_crashes
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff
        self._consecutive_crashes = 0
        self._total_restarts = 0
        self._running = True
        self._process: asyncio.subprocess.Process | None = None

    async def start(self) -> None:
        """Start the watchdog loop."""
        log.info(
            "watchdog.started",
            command=" ".join(self.agent_command),
            max_crashes=self.max_crashes,
        )

        # Handle signals
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_signal)

        while self._running:
            exit_code = await self._run_agent()

            if exit_code == CLEAN_EXIT_CODE:
                log.info("watchdog.agent_clean_exit")
                break

            elif exit_code == RESTART_EXIT_CODE:
                log.info("watchdog.agent_requested_restart")
                self._consecutive_crashes = 0
                self._total_restarts += 1
                continue

            else:
                self._consecutive_crashes += 1
                self._total_restarts += 1
                log.warning(
                    "watchdog.agent_crashed",
                    exit_code=exit_code,
                    consecutive=self._consecutive_crashes,
                    total_restarts=self._total_restarts,
                )

                if self._consecutive_crashes >= self.max_crashes:
                    log.critical(
                        "watchdog.max_crashes_exceeded",
                        max=self.max_crashes,
                    )
                    break

                backoff = min(
                    self.base_backoff * (2 ** (self._consecutive_crashes - 1)),
                    self.max_backoff,
                )
                log.info("watchdog.backoff_wait", seconds=backoff)
                await asyncio.sleep(backoff)

        log.info("watchdog.stopped", total_restarts=self._total_restarts)

    async def _run_agent(self) -> int:
        """Run the agent process and return its exit code."""
        env = os.environ.copy()
        env["WATCHDOG_PID"] = str(os.getpid())

        self._process = await asyncio.create_subprocess_exec(
            *self.agent_command,
            env=env,
            cwd=os.getcwd(),
        )

        exit_code = await self._process.wait()
        self._process = None
        return exit_code

    def _handle_signal(self) -> None:
        """Handle termination signals."""
        log.info("watchdog.signal_received")
        self._running = False
        if self._process:
            self._process.terminate()


async def main():
    """Entry point for watchdog process."""
    watchdog = Watchdog()
    await watchdog.start()


if __name__ == "__main__":
    asyncio.run(main())
