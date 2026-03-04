"""Pluggable payment provider abstract interface and registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class PaymentResult:
    payment_id: str
    status: str  # "pending" | "success" | "failed"
    amount: Decimal
    provider_name: str
    qr_code_url: str = ""
    raw_response: dict | None = None


@dataclass
class WebhookEvent:
    event_type: str  # "payment.success" | "payment.failed" | "refund.success"
    payment_id: str
    amount: Decimal
    provider_name: str
    raw_data: dict = field(default_factory=dict)


class PaymentProvider(ABC):
    """Abstract base class for payment providers."""

    provider_name: str

    @abstractmethod
    async def create_payment(self, amount: Decimal, description: str, **kwargs) -> PaymentResult:
        """Create a payment request (e.g., generate QR code, payment link)."""
        ...

    @abstractmethod
    async def query_payment(self, payment_id: str) -> PaymentResult:
        """Query the status of a payment."""
        ...

    @abstractmethod
    async def query_balance(self) -> Decimal:
        """Query current account balance."""
        ...

    @abstractmethod
    async def refund(self, payment_id: str, amount: Decimal | None = None) -> bool:
        """Refund a payment (full or partial)."""
        ...

    @abstractmethod
    async def verify_webhook(self, headers: dict, body: bytes) -> WebhookEvent | None:
        """Verify and parse a webhook notification."""
        ...

    def __repr__(self) -> str:
        return f"PaymentProvider({self.provider_name})"


class PaymentProviderRegistry:
    """Registry managing all payment provider instances."""

    def __init__(self) -> None:
        self._providers: dict[str, PaymentProvider] = {}
        self._default: str | None = None

    def register(self, provider: PaymentProvider, default: bool = False) -> None:
        self._providers[provider.provider_name] = provider
        if default or self._default is None:
            self._default = provider.provider_name

    def get(self, provider_name: str) -> PaymentProvider:
        if provider_name not in self._providers:
            raise KeyError(f"Payment provider '{provider_name}' not registered")
        return self._providers[provider_name]

    def get_default(self) -> PaymentProvider:
        if self._default is None:
            raise RuntimeError("No payment providers registered")
        return self._providers[self._default]

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    def has_provider(self, name: str) -> bool:
        return name in self._providers
