"""Git version control manager for safe self-modification."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import structlog

log = structlog.get_logger()


class GitManager:
    """Manages git operations for self-modification safety."""

    def __init__(self, repo_path: Path | str | None = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()

    async def _run(self, *args: str) -> tuple[int, str, str]:
        """Run a git command and return (returncode, stdout, stderr)."""
        proc = await asyncio.create_subprocess_exec(
            "git", *args,
            cwd=str(self.repo_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode, stdout.decode().strip(), stderr.decode().strip()

    async def init_repo(self) -> None:
        """Initialize git repo if not already initialized."""
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            await self._run("init")
            await self._run("config", "user.email", "agent@self-improve.local")
            await self._run("config", "user.name", "Self-Improve Agent")
            log.info("git.repo_initialized", path=str(self.repo_path))

    async def commit_all(self, message: str) -> Optional[str]:
        """Stage all changes and commit. Returns commit hash or None."""
        await self._run("add", "-A")
        rc, stdout, _ = await self._run("status", "--porcelain")
        if not stdout:
            log.debug("git.nothing_to_commit")
            return None
        rc, stdout, stderr = await self._run("commit", "-m", message)
        if rc != 0:
            log.warning("git.commit_failed", stderr=stderr)
            return None
        commit_hash = await self.get_head_hash()
        log.info("git.committed", hash=commit_hash, message=message)
        return commit_hash

    async def get_head_hash(self) -> Optional[str]:
        """Get current HEAD commit hash."""
        rc, stdout, _ = await self._run("rev-parse", "HEAD")
        return stdout if rc == 0 else None

    async def create_tag(self, tag: str, message: str = "") -> bool:
        """Create an annotated tag."""
        args = ["tag", "-a", tag, "-m", message or tag]
        rc, _, stderr = await self._run(*args)
        if rc != 0:
            log.warning("git.tag_failed", tag=tag, stderr=stderr)
            return False
        log.info("git.tag_created", tag=tag)
        return True

    async def revert_to(self, commit_hash: str) -> bool:
        """Hard reset to a specific commit. DANGEROUS - use with care."""
        rc, _, stderr = await self._run("reset", "--hard", commit_hash)
        if rc != 0:
            log.error("git.revert_failed", target=commit_hash, stderr=stderr)
            return False
        log.warning("git.reverted", target=commit_hash)
        return True

    async def get_diff(self, commit_a: str = "HEAD~1", commit_b: str = "HEAD") -> str:
        """Get diff between two commits."""
        rc, stdout, _ = await self._run("diff", commit_a, commit_b, "--stat")
        return stdout if rc == 0 else ""

    async def get_log(self, n: int = 10) -> str:
        """Get recent commit log."""
        rc, stdout, _ = await self._run(
            "log", f"-{n}", "--oneline", "--no-decorate"
        )
        return stdout if rc == 0 else ""

    async def stash(self) -> bool:
        """Stash current changes."""
        rc, _, _ = await self._run("stash", "push", "-m", "auto-stash before self-mod")
        return rc == 0

    async def stash_pop(self) -> bool:
        """Pop stashed changes."""
        rc, _, _ = await self._run("stash", "pop")
        return rc == 0
