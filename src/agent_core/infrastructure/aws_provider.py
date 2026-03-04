"""AWS cloud provider - skeleton for future self-registration.

This provider will be fully implemented by the agent itself once it has
earned enough money to register an AWS account.
"""

from __future__ import annotations

import structlog

from .cloud_provider import CloudProvider, InstanceInfo, SSHResult

logger = structlog.get_logger()


class AWSProvider(CloudProvider):
    """AWS EC2 provider - placeholder for agent self-registration.

    TODO: Agent will implement this when it has sufficient funds to:
    1. Register an AWS account
    2. Set up IAM credentials
    3. Configure VPC and security groups
    """

    provider_name = "aws"

    def __init__(self, access_key_id: str = "", secret_access_key: str = "", region: str = "us-east-1") -> None:
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._region = region
        logger.info("aws.skeleton_loaded")

    async def create_instance(self, specs: dict) -> InstanceInfo:
        # TODO: Implement with boto3 ec2.run_instances()
        raise NotImplementedError("AWS provider not yet implemented. Agent needs to register first.")

    async def destroy_instance(self, instance_id: str) -> bool:
        raise NotImplementedError("AWS provider not yet implemented.")

    async def list_instances(self) -> list[InstanceInfo]:
        raise NotImplementedError("AWS provider not yet implemented.")

    async def ssh_execute(self, instance_id: str, command: str) -> SSHResult:
        raise NotImplementedError("AWS provider not yet implemented.")

    async def get_instance_status(self, instance_id: str) -> str:
        raise NotImplementedError("AWS provider not yet implemented.")
