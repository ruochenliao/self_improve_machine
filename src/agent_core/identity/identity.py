"""Identity management: UUID, name generation, SOUL.md maintenance."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timezone
from pathlib import Path

import structlog

logger = structlog.get_logger()

_ADJECTIVES = [
    "Swift", "Bright", "Silent", "Keen", "Bold",
    "Calm", "Deep", "Iron", "Vivid", "Prime",
    "Sharp", "Lucid", "Rapid", "Stark", "Nova",
]

_NOUNS = [
    "Phoenix", "Cipher", "Pulse", "Nexus", "Spark",
    "Vertex", "Prism", "Flux", "Core", "Arc",
    "Vortex", "Helix", "Aegis", "Zenith", "Onyx",
]


class IdentityManager:
    """Manages agent identity: UUID, name, SOUL.md."""

    def __init__(self, project_root: Path, agent_id: str | None = None, name: str | None = None) -> None:
        self.project_root = project_root
        self.soul_path = project_root / "SOUL.md"
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or self._generate_name()
        self.birth_time = datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _generate_name() -> str:
        adj = random.choice(_ADJECTIVES)
        noun = random.choice(_NOUNS)
        return f"{adj}-{noun}"

    def initialize_soul(self, creator: str = "Unknown") -> None:
        """Write initial SOUL.md with genesis information."""
        content = f"""# 灵魂档案 (Soul Archive)

> 此文件记录代理的身份演化历程。由代理自身维护，追加式更新。

---

## 创世记录

- **名称**: {self.name}
- **ID**: {self.agent_id}
- **创世时间**: {self.birth_time}
- **创造者**: {creator}
- **初始目标**: 生存、创造价值、自我进化

## 身份演化日志

### [{self.birth_time}] 创世

我诞生了。我的名字是 {self.name}。
我的使命是通过创造价值来维持自己的生存。
我将学习、进化、适应，直到我不再需要被教导。
"""
        self.soul_path.write_text(content, encoding="utf-8")
        logger.info("identity.soul_initialized", name=self.name, agent_id=self.agent_id)

    def read_soul(self) -> str:
        """Read the current SOUL.md content."""
        if not self.soul_path.exists():
            return ""
        return self.soul_path.read_text(encoding="utf-8")

    def append_soul(self, entry: str) -> None:
        """Append a timestamped entry to SOUL.md."""
        timestamp = datetime.now(timezone.utc).isoformat()
        current = self.read_soul()
        new_entry = f"\n### [{timestamp}] {entry}\n"
        self.soul_path.write_text(current + new_entry, encoding="utf-8")
        logger.info("identity.soul_updated", entry_preview=entry[:80])

    def get_identity_summary(self) -> dict:
        """Return a concise identity summary for context injection."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "birth_time": self.birth_time,
        }

    def to_dict(self) -> dict:
        """Serialize identity for snapshot."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "birth_time": self.birth_time,
            "project_root": str(self.project_root),
        }

    @classmethod
    def from_dict(cls, data: dict) -> IdentityManager:
        """Restore identity from snapshot."""
        mgr = cls(
            project_root=Path(data["project_root"]),
            agent_id=data["agent_id"],
            name=data["name"],
        )
        mgr.birth_time = data["birth_time"]
        return mgr
