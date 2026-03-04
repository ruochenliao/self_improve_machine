"""Self-Modification - Code editing, smoke test, rollback, restart, watchdog."""

from .self_modifier import SelfModifier
from .git_manager import GitManager
from .smoke_test import SmokeTestRunner
from .rollback import RollbackManager
from .snapshot import SnapshotManager, AgentSnapshot
from .restarter import Restarter
from .audit import AuditLogger, AuditAction

__all__ = [
    "SelfModifier",
    "GitManager",
    "SmokeTestRunner",
    "RollbackManager",
    "SnapshotManager",
    "AgentSnapshot",
    "Restarter",
    "AuditLogger",
    "AuditAction",
]
