"""Pluggable cloud provider abstract interface and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class InstanceInfo:
    instance_id: str
    provider_name: str
    public_ip: str | None = None
    private_ip: str | None = None
    status: str = "pending"  # running | stopped | pending | terminated
    specs: dict = field(default_factory=dict)  # cpu, memory, disk, region
    hourly_cost_usd: float = 0.0


@dataclass
class SSHResult:
    stdout: str = ""
    stderr: str = ""
    exit_code: int = -1


class CloudProvider(ABC):
    """Abstract base class for cloud infrastructure providers."""

    provider_name: str

    @abstractmethod
    async def create_instance(self, specs: dict) -> InstanceInfo:
        """Create a new cloud instance."""
        ...

    @abstractmethod
    async def destroy_instance(self, instance_id: str) -> bool:
        """Destroy/terminate a cloud instance."""
        ...

    @abstractmethod
    async def list_instances(self) -> list[InstanceInfo]:
        """List all managed instances."""
        ...

    @abstractmethod
    async def ssh_execute(self, instance_id: str, command: str) -> SSHResult:
        """Execute a command on an instance via SSH."""
        ...

    @abstractmethod
    async def get_instance_status(self, instance_id: str) -> str:
        """Get current status of an instance."""
        ...

    def __repr__(self) -> str:
        return f"CloudProvider({self.provider_name})"


class CloudProviderRegistry:
    """Registry managing all cloud provider instances."""

    def __init__(self) -> None:
        self._providers: dict[str, CloudProvider] = {}
        self._default: str | None = None

    def register(self, provider: CloudProvider, default: bool = False) -> None:
        self._providers[provider.provider_name] = provider
        if default or self._default is None:
            self._default = provider.provider_name

    def get(self, provider_name: str) -> CloudProvider:
        if provider_name not in self._providers:
            raise KeyError(f"Cloud provider '{provider_name}' not registered")
        return self._providers[provider_name]

    def get_default(self) -> CloudProvider:
        if self._default is None:
            raise RuntimeError("No cloud providers registered")
        return self._providers[self._default]

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def has_provider(self, name: str) -> bool:
        return name in self._providers
