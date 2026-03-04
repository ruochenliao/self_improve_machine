"""Stripe payment provider - skeleton for future self-registration.

This provider will be fully implemented by the agent itself once it has
earned enough money to register a Stripe account.
"""

from __future__ import annotations

from decimal import Decimal

import structlog

from .payment_provider import PaymentProvider, PaymentResult, WebhookEvent

logger = structlog.get_logger()


class StripeProvider(PaymentProvider):
    """Stripe payment provider - placeholder for agent self-registration.

    TODO: Agent will implement this when it has sufficient funds to:
    1. Register a Stripe account
    2. Complete identity verification
    3. Set up API keys
    """

    provider_name = "stripe"

    def __init__(self, api_key: str = "", webhook_secret: str = "") -> None:
        self._api_key = api_key
        self._webhook_secret = webhook_secret
        if api_key:
            logger.info("stripe.initialized", key_suffix=api_key[-4:])
        else:
            logger.info("stripe.skeleton_loaded")

    async def create_payment(self, amount: Decimal, description: str, **kwargs) -> PaymentResult:
        # TODO: Implement with stripe.PaymentIntent.create()
        raise NotImplementedError("Stripe provider not yet implemented. Agent needs to register first.")

    async def query_payment(self, payment_id: str) -> PaymentResult:
        # TODO: Implement with stripe.PaymentIntent.retrieve()
        raise NotImplementedError("Stripe provider not yet implemented.")

    async def query_balance(self) -> Decimal:
        # TODO: Implement with stripe.Balance.retrieve()
        raise NotImplementedError("Stripe provider not yet implemented.")

    async def refund(self, payment_id: str, amount: Decimal | None = None) -> bool:
        # TODO: Implement with stripe.Refund.create()
        raise NotImplementedError("Stripe provider not yet implemented.")

    async def verify_webhook(self, headers: dict, body: bytes) -> WebhookEvent | None:
        # TODO: Implement with stripe.Webhook.construct_event()
        raise NotImplementedError("Stripe provider not yet implemented.")
