"""Aliyun (Alibaba Cloud) ECS provider with paramiko SSH."""

from __future__ import annotations

import asyncio
from functools import partial

import structlog

from .cloud_provider import CloudProvider, InstanceInfo, SSHResult

logger = structlog.get_logger()


class AliyunProvider(CloudProvider):
    """Cloud provider using Alibaba Cloud ECS + paramiko SSH."""

    provider_name = "aliyun"

    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        region_id: str = "cn-hangzhou",
        default_instance_type: str = "ecs.t6-c1m1.large",
        default_image_id: str = "ubuntu_22_04_x64_20G_alibase_20240130.vhd",
        security_group_id: str = "",
        vswitch_id: str = "",
    ) -> None:
        self._access_key_id = access_key_id
        self._access_key_secret = access_key_secret
        self._region_id = region_id
        self._default_instance_type = default_instance_type
        self._default_image_id = default_image_id
        self._security_group_id = security_group_id
        self._vswitch_id = vswitch_id
        self._ecs_client = None
        self._instances: dict[str, InstanceInfo] = {}
        self._ssh_keys: dict[str, dict] = {}  # instance_id -> {host, key_path, user}

        self._init_client()

    def _init_client(self) -> None:
        """Initialize Alibaba Cloud ECS client."""
        if not self._access_key_id or not self._access_key_secret:
            logger.warning("aliyun.no_credentials")
            return

        try:
            from alibabacloud_ecs20140526.client import Client as EcsClient
            from alibabacloud_tea_openapi.models import Config

            config = Config(
                access_key_id=self._access_key_id,
                access_key_secret=self._access_key_secret,
                region_id=self._region_id,
            )
            config.endpoint = f"ecs.{self._region_id}.aliyuncs.com"
            self._ecs_client = EcsClient(config)
            logger.info("aliyun.initialized", region=self._region_id)
        except ImportError:
            logger.warning("aliyun.sdk_not_installed")
        except Exception as e:
            logger.error("aliyun.init_failed", error=str(e))

    async def create_instance(self, specs: dict) -> InstanceInfo:
        """Create an ECS instance."""
        if self._ecs_client is None:
            raise RuntimeError("Aliyun ECS client not initialized")

        try:
            from alibabacloud_ecs20140526.models import RunInstancesRequest

            request = RunInstancesRequest(
                region_id=self._region_id,
                instance_type=specs.get("instance_type", self._default_instance_type),
                image_id=specs.get("image_id", self._default_image_id),
                security_group_id=specs.get("security_group_id", self._security_group_id),
                v_switch_id=specs.get("vswitch_id", self._vswitch_id),
                instance_charge_type="PostPaid",
                internet_charge_type="PayByTraffic",
                internet_max_bandwidth_out=specs.get("bandwidth", 5),
                amount=1,
            )

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, partial(self._ecs_client.run_instances, request)
            )

            instance_ids = response.body.instance_id_sets.instance_id_set
            instance_id = instance_ids[0] if instance_ids else "unknown"

            info = InstanceInfo(
                instance_id=instance_id,
                provider_name=self.provider_name,
                status="pending",
                specs=specs,
                hourly_cost_usd=specs.get("hourly_cost_usd", 0.05),
            )
            self._instances[instance_id] = info

            logger.info("aliyun.instance_created", instance_id=instance_id)
            return info

        except Exception as e:
            logger.error("aliyun.create_failed", error=str(e))
            raise

    async def destroy_instance(self, instance_id: str) -> bool:
        """Terminate an ECS instance."""
        if self._ecs_client is None:
            return False

        try:
            from alibabacloud_ecs20140526.models import DeleteInstanceRequest

            request = DeleteInstanceRequest(instance_id=instance_id, force=True)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, partial(self._ecs_client.delete_instance, request)
            )

            self._instances.pop(instance_id, None)
            logger.info("aliyun.instance_destroyed", instance_id=instance_id)
            return True
        except Exception as e:
            logger.error("aliyun.destroy_failed", instance_id=instance_id, error=str(e))
            return False

    async def list_instances(self) -> list[InstanceInfo]:
        """List all managed ECS instances."""
        if self._ecs_client is None:
            return list(self._instances.values())

        try:
            from alibabacloud_ecs20140526.models import DescribeInstancesRequest

            request = DescribeInstancesRequest(region_id=self._region_id, page_size=100)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, partial(self._ecs_client.describe_instances, request)
            )

            instances = []
            for inst in response.body.instances.instance:
                public_ips = inst.public_ip_address.ip_address if inst.public_ip_address else []
                info = InstanceInfo(
                    instance_id=inst.instance_id,
                    provider_name=self.provider_name,
                    public_ip=public_ips[0] if public_ips else None,
                    status=inst.status.lower() if inst.status else "unknown",
                    specs={
                        "instance_type": inst.instance_type,
                        "cpu": inst.cpu,
                        "memory_mb": inst.memory,
                        "region": inst.region_id,
                    },
                )
                instances.append(info)
                self._instances[inst.instance_id] = info

            return instances
        except Exception as e:
            logger.error("aliyun.list_failed", error=str(e))
            return list(self._instances.values())

    async def ssh_execute(self, instance_id: str, command: str) -> SSHResult:
        """Execute command on instance via SSH using paramiko."""
        info = self._instances.get(instance_id)
        ssh_config = self._ssh_keys.get(instance_id, {})

        host = ssh_config.get("host") or (info.public_ip if info else None)
        if not host:
            return SSHResult(stderr="No host/IP for instance", exit_code=1)

        try:
            import paramiko

            key_path = ssh_config.get("key_path", "")
            user = ssh_config.get("user", "root")

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            connect_kwargs: dict = {"hostname": host, "username": user, "timeout": 10}
            if key_path:
                connect_kwargs["key_filename"] = key_path

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, partial(client.connect, **connect_kwargs))

            stdin, stdout, stderr = await loop.run_in_executor(
                None, partial(client.exec_command, command, timeout=60)
            )

            result = SSHResult(
                stdout=stdout.read().decode("utf-8", errors="replace"),
                stderr=stderr.read().decode("utf-8", errors="replace"),
                exit_code=stdout.channel.recv_exit_status(),
            )

            client.close()
            return result
        except Exception as e:
            logger.error("aliyun.ssh_failed", instance_id=instance_id, error=str(e))
            return SSHResult(stderr=str(e), exit_code=1)

    async def get_instance_status(self, instance_id: str) -> str:
        """Get instance current status."""
        instances = await self.list_instances()
        for inst in instances:
            if inst.instance_id == instance_id:
                return inst.status
        return "unknown"

    def set_ssh_config(self, instance_id: str, host: str, key_path: str, user: str = "root") -> None:
        """Configure SSH access for an instance."""
        self._ssh_keys[instance_id] = {"host": host, "key_path": key_path, "user": user}
