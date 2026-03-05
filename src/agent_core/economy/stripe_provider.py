"""Stripe payment provider implementation."""

from __future__ import annotations

from decimal import Decimal

import structlog

from .payment_provider import PaymentProvider, PaymentResult, WebhookEvent

logger = structlog.get_logger()


class StripeProvider(PaymentProvider):
    """Stripe payment provider using stripe-python SDK.

    Supports:
    - Payment creation via PaymentIntent (card) or Checkout Session (hosted page)
    - Payment status query
    - Balance retrieval
    - Refunds
    - Webhook signature verification
    """

    provider_name = "stripe"

    def __init__(
        self,
        api_key: str = "",
        webhook_secret: str = "",
    ) -> None:
        self._api_key = api_key
        self._webhook_secret = webhook_secret
        self._stripe = None

        if api_key:
            try:
                import stripe
                stripe.api_key = api_key
                self._stripe = stripe
                logger.info("stripe.initialized", key_suffix=api_key[-4:])
            except ImportError:
                logger.warning("stripe.sdk_not_installed")
        else:
            logger.info("stripe.skeleton_loaded")

    def _ensure_stripe(self) -> None:
        """Ensure Stripe SDK is available and configured."""
        if self._stripe is None:
            raise RuntimeError(
                "Stripe not initialized. Provide a valid API key or install stripe package."
            )

    async def create_payment(
        self, amount: Decimal, description: str, **kwargs
    ) -> PaymentResult:
        """Create a Stripe PaymentIntent.

        Args:
            amount: Amount in USD (will be converted to cents).
            description: Payment description.
            **kwargs: Optional 'currency' (default 'usd'), 'customer', 'metadata'.
        """
        self._ensure_stripe()

        currency = kwargs.get("currency", "usd")
        amount_cents = int(amount * 100)

        try:
            intent = self._stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                description=description,
                metadata=kwargs.get("metadata", {}),
                customer=kwargs.get("customer"),
                automatic_payment_methods={"enabled": True},
            )

            logger.info(
                "stripe.payment_created",
                payment_id=intent.id,
                amount=str(amount),
                currency=currency,
            )

            status_map = {
                "requires_payment_method": "pending",
                "requires_confirmation": "pending",
                "requires_action": "pending",
                "processing": "pending",
                "succeeded": "success",
                "canceled": "failed",
            }

            return PaymentResult(
                payment_id=intent.id,
                status=status_map.get(intent.status, "pending"),
                amount=amount,
                provider_name=self.provider_name,
                qr_code_url=intent.get("client_secret", ""),
                raw_response=dict(intent),
            )
        except Exception as e:
            logger.error("stripe.create_payment_failed", error=str(e))
            return PaymentResult(
                payment_id="",
                status="failed",
                amount=amount,
                provider_name=self.provider_name,
                raw_response={"error": str(e)},
            )

    async def query_payment(self, payment_id: str) -> PaymentResult:
        """Retrieve a PaymentIntent by ID."""
        self._ensure_stripe()

        try:
            intent = self._stripe.PaymentIntent.retrieve(payment_id)

            status_map = {
                "requires_payment_method": "pending",
                "requires_confirmation": "pending",
                "requires_action": "pending",
                "processing": "pending",
                "succeeded": "success",
                "canceled": "failed",
            }

            return PaymentResult(
                payment_id=intent.id,
                status=status_map.get(intent.status, "pending"),
                amount=Decimal(str(intent.amount / 100)),
                provider_name=self.provider_name,
                raw_response=dict(intent),
            )
        except Exception as e:
            logger.error("stripe.query_failed", error=str(e), payment_id=payment_id)
            return PaymentResult(
                payment_id=payment_id,
                status="failed",
                amount=Decimal(0),
                provider_name=self.provider_name,
            )

    async def query_balance(self) -> Decimal:
        """Query Stripe account balance."""
        self._ensure_stripe()

        try:
            balance = self._stripe.Balance.retrieve()
            # Sum available balances across currencies (convert to USD equivalent)
            total_cents = 0
            for entry in balance.get("available", []):
                if entry["currency"] == "usd":
                    total_cents += entry["amount"]
                else:
                    # For non-USD, approximate (in production use exchange rates)
                    total_cents += entry["amount"]

            return Decimal(str(total_cents / 100))
        except Exception as e:
            logger.error("stripe.balance_query_failed", error=str(e))
            return Decimal(0)

    async def refund(self, payment_id: str, amount: Decimal | None = None) -> bool:
        """Create a refund for a PaymentIntent."""
        self._ensure_stripe()

        try:
            params: dict = {"payment_intent": payment_id}
            if amount is not None:
                params["amount"] = int(amount * 100)

            refund = self._stripe.Refund.create(**params)
            logger.info(
                "stripe.refunded",
                payment_id=payment_id,
                refund_id=refund.id,
                status=refund.status,
            )
            return refund.status in ("succeeded", "pending")
        except Exception as e:
            logger.error("stripe.refund_failed", error=str(e), payment_id=payment_id)
            return False

    async def verify_webhook(self, headers: dict, body: bytes) -> WebhookEvent | None:
        """Verify Stripe webhook signature and parse event."""
        self._ensure_stripe()

        if not self._webhook_secret:
            logger.warning("stripe.no_webhook_secret")
            return None

        try:
            sig_header = headers.get("stripe-signature", "")
            event = self._stripe.Webhook.construct_event(
                body, sig_header, self._webhook_secret
            )

            event_type = event.get("type", "")
            data_obj = event.get("data", {}).get("object", {})

            # Map Stripe event types to our internal types
            type_map = {
                "payment_intent.succeeded": "payment.success",
                "payment_intent.payment_failed": "payment.failed",
                "charge.refunded": "refund.success",
            }

            mapped_type = type_map.get(event_type)
            if not mapped_type:
                logger.debug("stripe.webhook_ignored", event_type=event_type)
                return None

            return WebhookEvent(
                event_type=mapped_type,
                payment_id=data_obj.get("id", ""),
                amount=Decimal(str(data_obj.get("amount", 0) / 100)),
                provider_name=self.provider_name,
                raw_data=dict(event),
            )
        except self._stripe.error.SignatureVerificationError as e:
            logger.error("stripe.webhook_signature_invalid", error=str(e))
            return None
        except Exception as e:
            logger.error("stripe.webhook_failed", error=str(e))
            return None
