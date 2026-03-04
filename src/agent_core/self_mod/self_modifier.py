"""Self-Modifier — the agent's ability to modify its own source code."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Optional

import structlog

from .audit import AuditLogger, AuditAction
from .git_manager import GitManager
from .rollback import RollbackManager
from .smoke_test import SmokeTestRunner

log = structlog.get_logger()


class SelfModifier:
    """
    Orchestrates safe self-modification of agent source code.

    Flow:
    1. Agent proposes a code change
    2. Constitutional check (is this modification allowed?)
    3. Git commit baseline
    4. Apply modification
    5. Smoke test
    6. If tests pass → keep; if fail → rollback
    7. Audit log everything
    """

    def __init__(
        self,
        project_root: Path | str | None = None,
        git: GitManager | None = None,
        audit: AuditLogger | None = None,
    ):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.git = git or GitManager(self.project_root)
        self.smoke = SmokeTestRunner(self.project_root)
        self.rollback = RollbackManager(self.git, self.smoke)
        self.audit = audit or AuditLogger()

        # Forbidden paths — agent cannot modify these
        self._protected_paths = {
            "CONSTITUTION.md",
            "SOUL.md",
        }

        # Modification budget per cycle
        self.max_modifications_per_cycle = 3
        self._modifications_this_cycle = 0

    async def initialize(self) -> None:
        """Initialize git repo if needed."""
        await self.git.init_repo()

    def _is_protected(self, file_path: str) -> bool:
        """Check if a file is protected from modification."""
        rel = Path(file_path).name
        return rel in self._protected_paths

    async def modify_file(
        self,
        file_path: str,
        new_content: str,
        description: str,
        constitutional_check: bool = True,
    ) -> dict[str, Any]:
        """
        Safely modify a single file.

        Returns dict with keys: success, rolled_back, reason
        """
        # Budget check
        if self._modifications_this_cycle >= self.max_modifications_per_cycle:
            return {
                "success": False,
                "rolled_back": False,
                "reason": "Modification budget exhausted for this cycle",
            }

        # Protected path check
        if self._is_protected(file_path):
            await self.audit.log_action(
                AuditAction.CONSTITUTION_CHECK,
                f"Blocked modification to protected file: {file_path}",
                success=False,
            )
            return {
                "success": False,
                "rolled_back": False,
                "reason": f"File {file_path} is constitutionally protected",
            }

        # Perform modification with rollback safety
        target = self.project_root / file_path

        async def do_modify():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(new_content, encoding="utf-8")

        attempt = await self.rollback.safe_modify(description, do_modify)
        self._modifications_this_cycle += 1

        # Audit
        await self.audit.log_action(
            AuditAction.SELF_MODIFY,
            description,
            details={
                "file": file_path,
                "rolled_back": attempt.rolled_back,
                "smoke_passed": attempt.smoke_result.passed if attempt.smoke_result else None,
            },
            success=attempt.success,
        )

        return {
            "success": attempt.success,
            "rolled_back": attempt.rolled_back,
            "reason": (
                "Smoke tests failed, changes reverted"
                if attempt.rolled_back
                else "OK" if attempt.success else "Unknown error"
            ),
        }

    async def create_new_module(
        self,
        module_path: str,
        files: dict[str, str],
        description: str,
    ) -> dict[str, Any]:
        """Create a new module with multiple files."""
        if self._modifications_this_cycle >= self.max_modifications_per_cycle:
            return {"success": False, "reason": "Modification budget exhausted"}

        async def do_create():
            base = self.project_root / module_path
            for fname, content in files.items():
                fpath = base / fname
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(content, encoding="utf-8")

        attempt = await self.rollback.safe_modify(description, do_create)
        self._modifications_this_cycle += 1

        await self.audit.log_action(
            AuditAction.SELF_MODIFY,
            description,
            details={"module": module_path, "files": list(files.keys())},
            success=attempt.success,
        )

        return {
            "success": attempt.success,
            "rolled_back": attempt.rolled_back,
            "reason": "OK" if attempt.success else "Smoke tests failed",
        }

    def reset_cycle_budget(self) -> None:
        """Reset the per-cycle modification budget."""
        self._modifications_this_cycle = 0

    def get_stats(self) -> dict[str, Any]:
        """Get self-modification statistics."""
        return {
            "modifications_this_cycle": self._modifications_this_cycle,
            "budget_remaining": self.max_modifications_per_cycle - self._modifications_this_cycle,
            "total_attempts": len(self.rollback.history),
            "success_rate": self.rollback.get_success_rate(),
        }
