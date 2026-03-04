"""Rollback manager — automatically reverts failed self-modifications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import structlog

from .git_manager import GitManager
from .smoke_test import SmokeTestRunner, SmokeTestResult

log = structlog.get_logger()


@dataclass
class ModificationAttempt:
    """Record of a self-modification attempt."""
    description: str
    pre_commit: Optional[str] = None
    post_commit: Optional[str] = None
    smoke_result: Optional[SmokeTestResult] = None
    rolled_back: bool = False
    success: bool = False


class RollbackManager:
    """Manages safe self-modification with automatic rollback on failure."""

    def __init__(self, git: GitManager, smoke_runner: SmokeTestRunner):
        self.git = git
        self.smoke = smoke_runner
        self.history: list[ModificationAttempt] = []

    async def safe_modify(
        self,
        description: str,
        modify_fn,
    ) -> ModificationAttempt:
        """
        Execute a modification function with safety net.

        1. Record pre-modification commit
        2. Execute modify_fn (async callable)
        3. Commit changes
        4. Run smoke tests
        5. If tests fail → revert to pre-modification commit
        """
        attempt = ModificationAttempt(description=description)

        # Step 1: Record baseline
        attempt.pre_commit = await self.git.get_head_hash()
        log.info(
            "rollback.modification_start",
            description=description,
            baseline=attempt.pre_commit,
        )

        try:
            # Step 2: Execute modification
            await modify_fn()

            # Step 3: Commit
            attempt.post_commit = await self.git.commit_all(
                f"self-mod: {description}"
            )

            if not attempt.post_commit:
                log.info("rollback.no_changes", description=description)
                attempt.success = True
                self.history.append(attempt)
                return attempt

            # Step 4: Smoke test
            attempt.smoke_result = await self.smoke.run_all()

            if attempt.smoke_result.passed:
                # Tag successful modification
                await self.git.create_tag(
                    f"self-mod-ok-{attempt.post_commit[:8]}",
                    description,
                )
                attempt.success = True
                log.info(
                    "rollback.modification_success",
                    description=description,
                    commit=attempt.post_commit,
                )
            else:
                # Step 5: Revert
                log.warning(
                    "rollback.smoke_failed_reverting",
                    description=description,
                    errors=attempt.smoke_result.errors[:3],
                )
                if attempt.pre_commit:
                    reverted = await self.git.revert_to(attempt.pre_commit)
                    attempt.rolled_back = reverted
                    if reverted:
                        log.info("rollback.reverted", target=attempt.pre_commit)
                    else:
                        log.error("rollback.revert_failed")
                attempt.success = False

        except Exception as e:
            log.error(
                "rollback.modification_error",
                description=description,
                error=str(e),
            )
            if attempt.pre_commit:
                await self.git.revert_to(attempt.pre_commit)
                attempt.rolled_back = True
            attempt.success = False

        self.history.append(attempt)
        return attempt

    def get_success_rate(self) -> float:
        """Get the success rate of all modification attempts."""
        if not self.history:
            return 0.0
        successes = sum(1 for a in self.history if a.success)
        return successes / len(self.history)
