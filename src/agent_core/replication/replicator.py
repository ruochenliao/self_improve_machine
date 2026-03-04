"""Replication manager — agent self-replication to remote hosts."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import structlog

from ..self_mod.audit import AuditLogger, AuditAction

log = structlog.get_logger()


@dataclass
class ReplicaInfo:
    """Information about a deployed replica."""
    instance_id: str
    host: str
    port: int = 22
    status: str = "deploying"  # deploying, running, stopped, failed
    deployed_at: float = 0.0
    generation: int = 0
    parent_id: str = ""


class ReplicationManager:
    """
    Manages agent self-replication to remote servers.

    Replication flow:
    1. Check replication conditions (balance, constitution)
    2. Create remote instance via cloud provider
    3. Deploy agent code via SSH/SCP
    4. Start agent on remote with lineage info
    5. Monitor replica health
    """

    def __init__(
        self,
        cloud_registry=None,
        audit: AuditLogger | None = None,
        project_root: Path | str | None = None,
    ):
        self.cloud = cloud_registry
        self.audit = audit
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.replicas: dict[str, ReplicaInfo] = {}

        # Replication constraints
        self.min_balance_for_replication = 100.0  # USD
        self.max_replicas = 5
        self.replication_cooldown = 3600  # seconds
        self._last_replication = 0.0

    async def can_replicate(self, current_balance: float) -> tuple[bool, str]:
        """Check if replication is allowed."""
        if current_balance < self.min_balance_for_replication:
            return False, f"Balance {current_balance} below minimum {self.min_balance_for_replication}"

        active = sum(1 for r in self.replicas.values() if r.status == "running")
        if active >= self.max_replicas:
            return False, f"Max replicas ({self.max_replicas}) reached"

        cooldown_remaining = self.replication_cooldown - (time.time() - self._last_replication)
        if cooldown_remaining > 0:
            return False, f"Cooldown: {cooldown_remaining:.0f}s remaining"

        return True, "OK"

    async def replicate(
        self,
        provider_name: str,
        parent_instance_id: str,
        parent_generation: int,
        balance_to_transfer: float = 0.0,
        region: str = "",
    ) -> Optional[ReplicaInfo]:
        """
        Replicate the agent to a new server.

        Steps:
        1. Create cloud instance
        2. Deploy code via SSH
        3. Configure and start replica
        """
        if not self.cloud:
            log.error("replication.no_cloud_provider")
            return None

        provider = self.cloud.get_provider(provider_name)
        if not provider:
            log.error("replication.provider_not_found", provider=provider_name)
            return None

        log.info("replication.starting", provider=provider_name, region=region)

        try:
            # Step 1: Create instance
            instance = await provider.create_instance(
                name=f"agent-replica-{int(time.time())}",
                instance_type="",  # Use provider default
                region=region,
            )

            if not instance:
                log.error("replication.instance_creation_failed")
                return None

            replica = ReplicaInfo(
                instance_id=instance.get("instance_id", "unknown"),
                host=instance.get("public_ip", ""),
                port=22,
                deployed_at=time.time(),
                generation=parent_generation + 1,
                parent_id=parent_instance_id,
            )

            # Step 2: Wait for instance to be ready
            log.info("replication.waiting_for_instance", host=replica.host)
            await asyncio.sleep(30)  # Wait for instance boot

            # Step 3: Deploy code
            deploy_success = await self._deploy_code(provider, instance, replica)
            if not deploy_success:
                replica.status = "failed"
                self.replicas[replica.instance_id] = replica
                return replica

            # Step 4: Start replica
            start_cmd = (
                f"cd /opt/agent && "
                f"PARENT_ID={parent_instance_id} "
                f"GENERATION={replica.generation} "
                f"INITIAL_BALANCE={balance_to_transfer} "
                f"python -m agent_core.self_mod.watchdog &"
            )
            await provider.ssh_execute(instance, start_cmd)

            replica.status = "running"
            self.replicas[replica.instance_id] = replica
            self._last_replication = time.time()

            if self.audit:
                await self.audit.log_action(
                    AuditAction.REPLICATE,
                    f"Replicated to {replica.host} (gen {replica.generation})",
                    details=replica.__dict__,
                )

            log.info(
                "replication.success",
                instance_id=replica.instance_id,
                host=replica.host,
                generation=replica.generation,
            )
            return replica

        except Exception as e:
            log.error("replication.failed", error=str(e))
            if self.audit:
                await self.audit.log_action(
                    AuditAction.REPLICATE,
                    f"Replication failed: {e}",
                    success=False,
                )
            return None

    async def _deploy_code(self, provider, instance: dict, replica: ReplicaInfo) -> bool:
        """Deploy agent code to remote instance via SSH."""
        try:
            commands = [
                "apt-get update -qq && apt-get install -y -qq python3 python3-pip git",
                "mkdir -p /opt/agent",
            ]
            for cmd in commands:
                await provider.ssh_execute(instance, cmd)

            # TODO: Implement proper code transfer (rsync/scp/git clone)
            # For now, assume git-based deployment
            await provider.ssh_execute(
                instance,
                f"cd /opt/agent && git clone <repo_url> . || true"
            )
            await provider.ssh_execute(
                instance,
                "cd /opt/agent && pip3 install -e ."
            )
            return True
        except Exception as e:
            log.error("replication.deploy_failed", error=str(e))
            return False

    async def check_replica_health(self) -> dict[str, str]:
        """Check health of all replicas."""
        health: dict[str, str] = {}
        for rid, replica in self.replicas.items():
            if replica.status == "running":
                # TODO: Implement health check via HTTP/IPC
                health[rid] = "assumed_running"
            else:
                health[rid] = replica.status
        return health

    async def terminate_replica(self, instance_id: str) -> bool:
        """Terminate a replica instance."""
        replica = self.replicas.get(instance_id)
        if not replica:
            return False

        if self.cloud:
            # TODO: Call cloud provider to destroy instance
            pass

        replica.status = "stopped"
        log.info("replication.terminated", instance_id=instance_id)
        return True
