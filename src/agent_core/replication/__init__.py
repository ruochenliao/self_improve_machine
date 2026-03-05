"""Replication - Agent forking, lineage tracking, IPC."""

from .lineage import LineageTracker, LineageRecord
from .replicator import ReplicationManager
from .ipc import IPCBridge, IPCMessage

__all__ = ["LineageTracker", "LineageRecord", "ReplicationManager", "IPCBridge", "IPCMessage"]
