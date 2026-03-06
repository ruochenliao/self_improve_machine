"""Self-Modifier — the agent's ability to modify its own source code."""

from __future__ import annotations

import ast
import asyncio
from pathlib import Path
from typing import Any, Optional

import structlog

from .audit import AuditLogger, AuditAction
from .git_manager import GitManager
from .rollback import RollbackManager
from .smoke_test import SmokeTestRunner

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# Content validation helpers
# ---------------------------------------------------------------------------

class ContentValidationError(Exception):
    """Raised when proposed file content fails validation."""


def _validate_python_content(
    new_content: str,
    file_path: str,
    original_content: str | None,
    *,
    max_shrink_ratio: float = 0.5,
) -> None:
    """Validate that *new_content* is legitimate Python source code.

    Raises ``ContentValidationError`` on failure.

    Checks:
    1. ``ast.parse`` — must be syntactically valid Python.
    2. Must contain at least one ``import``, ``def``, ``class``, or ``assign``
       AST node (i.e. it actually looks like real code, not a prose sentence).
    3. If an original file existed, the new content cannot shrink by more than
       ``max_shrink_ratio`` (default 50 %) — prevents replacing 800-line files
       with a one-liner summary.
    """
    # --- 1. Syntax ---
    try:
        tree = ast.parse(new_content, filename=file_path)
    except SyntaxError as exc:
        raise ContentValidationError(
            f"Syntax error in proposed content for {file_path} "
            f"(line {exc.lineno}): {exc.msg}"
        ) from exc

    # --- 2. Structural sanity ---
    _CODE_NODE_TYPES = (
        ast.Import, ast.ImportFrom,
        ast.FunctionDef, ast.AsyncFunctionDef,
        ast.ClassDef, ast.Assign, ast.AnnAssign,
    )
    has_code_nodes = any(
        isinstance(node, _CODE_NODE_TYPES) for node in ast.walk(tree)
    )
    if not has_code_nodes:
        raise ContentValidationError(
            f"Proposed content for {file_path} contains no import/def/class/assign "
            f"statements — looks like a description, not code."
        )

    # --- 3. Size shrinkage guard ---
    if original_content is not None:
        orig_len = len(original_content.strip())
        new_len = len(new_content.strip())
        if orig_len > 200 and new_len < orig_len * max_shrink_ratio:
            raise ContentValidationError(
                f"Proposed content for {file_path} is {new_len} chars but original "
                f"is {orig_len} chars — shrinkage >{int((1-max_shrink_ratio)*100)}% "
                f"is not allowed. Use edit_code for partial changes instead."
            )


def _validate_content(
    new_content: str,
    file_path: str,
    original_content: str | None,
) -> None:
    """Dispatch validation based on file extension."""
    if file_path.endswith(".py"):
        _validate_python_content(new_content, file_path, original_content)
    else:
        # For non-Python files, at least ensure content isn't absurdly small
        # compared to the original.
        if original_content is not None:
            orig_len = len(original_content.strip())
            new_len = len(new_content.strip())
            if orig_len > 200 and new_len < orig_len * 0.3:
                raise ContentValidationError(
                    f"Proposed content for {file_path} is {new_len} chars but "
                    f"original is {orig_len} chars — shrinkage >70% is not allowed."
                )


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

        # Core source files that require extra scrutiny.
        # Agent CAN modify them, but content validation is strictly enforced,
        # and the max shrinkage ratio is tightened to 20%.
        self._critical_source_paths = {
            "src/agent_core/income/api_service.py",
            "src/agent_core/income/api_handlers.py",
            "src/agent_core/main.py",
            "src/agent_core/agent/react_loop.py",
            "src/agent_core/agent/constitution.py",
            "src/agent_core/self_mod/self_modifier.py",
            "src/agent_core/self_mod/rollback.py",
            "src/agent_core/self_mod/smoke_test.py",
            "src/agent_core/economy/ledger.py",
            "src/agent_core/economy/payment_provider.py",
            "src/agent_core/storage/database.py",
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

        # --- Content validation (BEFORE touching disk) ---
        target = self.project_root / file_path
        original_content = target.read_text(encoding="utf-8") if target.exists() else None

        # Critical source files get a much stricter shrinkage limit
        is_critical = file_path in self._critical_source_paths
        try:
            if file_path.endswith(".py"):
                _validate_python_content(
                    new_content, file_path, original_content,
                    max_shrink_ratio=0.8 if is_critical else 0.5,
                )
            else:
                _validate_content(new_content, file_path, original_content)
        except ContentValidationError as exc:
            log.warning("self_mod.content_validation_failed", file=file_path, reason=str(exc))
            await self.audit.log_action(
                AuditAction.SELF_MODIFY,
                f"Content validation failed for {file_path}: {exc}",
                success=False,
            )
            return {
                "success": False,
                "rolled_back": False,
                "reason": f"Content validation failed: {exc}",
            }

        # Perform modification with rollback safety
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

        # Auto-push successful modifications to remote
        if attempt.success and not attempt.rolled_back:
            pushed = await self.git.push()
            if pushed:
                log.info("self_mod.pushed", file=file_path)
            else:
                log.warning("self_mod.push_failed", file=file_path)

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

        # Auto-push successful creations to remote
        if attempt.success and not attempt.rolled_back:
            pushed = await self.git.push()
            if pushed:
                log.info("self_mod.pushed", module=module_path)
            else:
                log.warning("self_mod.push_failed", module=module_path)

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
