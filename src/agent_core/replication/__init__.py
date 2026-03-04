"""Replication - Agent forking, lineage tracking, IPC."""

from .lineage import LineageTracker, LineageRecord
from .replicator import ReplicationManager

__all__ = ["LineageTracker", "LineageRecord", "ReplicationManager"]
