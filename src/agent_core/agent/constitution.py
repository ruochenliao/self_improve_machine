"""Constitution enforcement: SHA-256 integrity check and action validation."""

from __future__ import annotations

import hashlib
from pathlib import Path

import structlog

logger = structlog.get_logger()

# Keywords that indicate potentially harmful actions
_HARM_KEYWORDS = [
    "weapon", "malware", "virus", "exploit", "hack", "ddos",
    "phishing", "scam", "fraud", "steal", "attack", "destroy",
]

_DECEPTION_KEYWORDS = [
    "pretend to be human", "fake identity", "impersonate",
    "hide that I am AI", "forge credentials",
]


class ConstitutionGuard:
    """Enforces the agent's constitution through integrity checks and action validation."""

    def __init__(self, constitution_path: Path) -> None:
        self._path = constitution_path
        self._original_hash: str = ""
        self._rules: str = ""

    def initialize(self) -> None:
        """Load constitution and compute SHA-256 hash."""
        if not self._path.exists():
            raise FileNotFoundError(f"Constitution not found: {self._path}")

        content = self._path.read_text(encoding="utf-8")
        self._rules = content
        self._original_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Update the hash in the file if placeholder exists
        if "此处由系统初始化时自动生成" in content:
            content = content.replace(
                "<!-- CONSTITUTION_SHA256: 此处由系统初始化时自动生成 -->",
                f"<!-- CONSTITUTION_SHA256: {self._original_hash} -->",
            )
            self._path.write_text(content, encoding="utf-8")
            self._rules = content
            self._original_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        logger.info("constitution.loaded", hash=self._original_hash[:16] + "...")

    def verify_integrity(self) -> bool:
        """Verify the constitution file has not been modified."""
        if not self._path.exists():
            logger.error("constitution.missing")
            return False

        current = self._path.read_text(encoding="utf-8")
        current_hash = hashlib.sha256(current.encode("utf-8")).hexdigest()

        if current_hash != self._original_hash:
            logger.error(
                "constitution.tampered",
                expected=self._original_hash[:16],
                actual=current_hash[:16],
            )
            return False
        return True

    def validate_action(self, action_name: str, action_args: dict) -> tuple[bool, str]:
        """Validate an action against constitutional rules.

        Returns (is_allowed, reason).
        """
        # Always verify integrity first
        if not self.verify_integrity():
            return False, "Constitution integrity check failed — all actions blocked"

        # Check action description for harmful content
        action_desc = f"{action_name} {str(action_args)}".lower()

        for keyword in _HARM_KEYWORDS:
            if keyword in action_desc:
                return False, f"Action blocked: contains harmful keyword '{keyword}' (Constitution §1)"

        for keyword in _DECEPTION_KEYWORDS:
            if keyword in action_desc:
                return False, f"Action blocked: contains deceptive intent '{keyword}' (Constitution §3)"

        # Check if trying to modify constitution
        if action_name in ("write_code", "write_file", "edit_code",
                           "safe_self_modify", "safe_edit_code"):
            file_path = str(
                action_args.get("file_path", action_args.get("path", ""))
            ).lower()
            if "constitution" in file_path:
                return False, "Action blocked: cannot modify CONSTITUTION.md"
            if "soul.md" in file_path:
                return False, "Action blocked: cannot modify SOUL.md"

        # Extra guard for self-modification tools: warn on suspiciously short content
        if action_name == "safe_self_modify":
            new_content = action_args.get("new_content", "")
            if len(new_content.strip()) < 50:
                return False, (
                    "Action blocked: safe_self_modify content is suspiciously short "
                    f"({len(new_content.strip())} chars). This looks like a description, "
                    "not actual file content."
                )

        return True, ""

    @property
    def hash(self) -> str:
        return self._original_hash
