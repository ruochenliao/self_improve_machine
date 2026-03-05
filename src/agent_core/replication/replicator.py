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
        """Deploy agent code to remote instance via SSH.

        Strategy:
        1. Install system dependencies
        2. Pack local source into a tarball
        3. Transfer via base64-encoded stdin (avoids SCP dependency)
        4. Install Python dependencies
        """
        try:
            # Step 1: Install system deps
            setup_commands = [
                "apt-get update -qq && apt-get install -y -qq python3 python3-pip python3-venv git",
                "mkdir -p /opt/agent",
            ]
            for cmd in setup_commands:
                result = await provider.ssh_execute(instance, cmd)
                if hasattr(result, "exit_code") and result.exit_code != 0:
                    log.warning("replication.setup_cmd_warning", cmd=cmd)

            # Step 2: Create tarball of source code (excluding data/, __pycache__, .git)
            import tarfile
            import io
            import base64

            tar_buffer = io.BytesIO()
            with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
                for item in self.project_root.rglob("*"):
                    rel = item.relative_to(self.project_root)
                    skip_dirs = {"data", "__pycache__", ".git", ".venv", "node_modules"}
                    if any(part in skip_dirs for part in rel.parts):
                        continue
                    if item.is_file():
                        tar.add(str(item), arcname=str(rel))

            tar_bytes = tar_buffer.getvalue()
            b64_data = base64.b64encode(tar_bytes).decode("ascii")

            # Step 3: Transfer via echo + base64 decode (chunked for large payloads)
            chunk_size = 60000  # ~60KB per command
            chunks = [b64_data[i:i+chunk_size] for i in range(0, len(b64_data), chunk_size)]

            # Clear any previous tarball
            await provider.ssh_execute(instance, "rm -f /tmp/agent_code.tar.gz")

            for chunk in chunks:
                await provider.ssh_execute(
                    instance,
                    f"echo -n '{chunk}' >> /tmp/agent_code_b64.txt",
                )

            await provider.ssh_execute(
                instance,
                "base64 -d /tmp/agent_code_b64.txt > /tmp/agent_code.tar.gz && rm /tmp/agent_code_b64.txt",
            )

            # Step 4: Extract and install
            await provider.ssh_execute(
                instance,
                "cd /opt/agent && tar xzf /tmp/agent_code.tar.gz && rm /tmp/agent_code.tar.gz",
            )
            await provider.ssh_execute(
                instance,
                "cd /opt/agent && pip3 install -e . 2>&1 | tail -5",
            )

            log.info("replication.code_deployed", host=replica.host)
            return True
        except Exception as e:
            log.error("replication.deploy_failed", error=str(e))
            return False

    async def check_replica_health(self) -> dict[str, str]:
        """Check health of all replicas via their API status endpoint."""
        import aiohttp

        health: dict[str, str] = {}
        for rid, replica in self.replicas.items():
            if replica.status != "running":
                health[rid] = replica.status
                continue

            try:
                # Try to reach the agent's status endpoint
                url = f"http://{replica.host}:8402/api/v1/status"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            health[rid] = "healthy" if data.get("alive") else "unhealthy"
                        else:
                            health[rid] = "unreachable"
            except asyncio.TimeoutError:
                health[rid] = "timeout"
                log.warning("replication.health_timeout", instance=rid, host=replica.host)
            except Exception:
                health[rid] = "unreachable"

        return health

    async def terminate_replica(self, instance_id: str) -> bool:
        """Terminate a replica instance."""
        replica = self.replicas.get(instance_id)
        if not replica:
            return False

        try:
            if self.cloud and replica.host:
                # Try graceful shutdown first via API
                try:
                    import aiohttp
                    url = f"http://{replica.host}:8402/api/v1/shutdown"
                    async with aiohttp.ClientSession() as session:
                        async with session.post(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                            pass
                except Exception:
                    pass

                # Destroy the cloud instance
                providers = self.cloud.list_providers()
                for pname in providers:
                    try:
                        provider = self.cloud.get(pname)
                        await provider.destroy_instance(instance_id)
                        break
                    except Exception:
                        continue

            replica.status = "stopped"

            if self.audit:
                await self.audit.log_action(
                    AuditAction.REPLICATE,
                    f"Terminated replica {instance_id} at {replica.host}",
                    details={"instance_id": instance_id},
                )

            log.info("replication.terminated", instance_id=instance_id)
            return True
        except Exception as e:
            log.error("replication.terminate_failed", instance_id=instance_id, error=str(e))
            return False
