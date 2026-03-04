"""HTTP 402 Payment Required handler - auto-pays when encountering 402 responses."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import aiohttp
import structlog

if TYPE_CHECKING:
    from agent_core.economy.payment_provider import PaymentProviderRegistry

logger = structlog.get_logger()


class HTTP402Handler:
    """Intercepts HTTP 402 responses and automatically handles payment."""

    def __init__(self, payment_registry: PaymentProviderRegistry) -> None:
        self._registry = payment_registry

    async def handle_response(
        self,
        response: aiohttp.ClientResponse,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        **kwargs,
    ) -> aiohttp.ClientResponse:
        """If response is 402, attempt to pay and retry the request."""
        if response.status != 402:
            return response

        logger.info("http402.detected", url=url)

        # Parse payment info from response
        payment_info = await self._parse_payment_info(response)
        if not payment_info:
            logger.warning("http402.cannot_parse_payment_info", url=url)
            return response

        amount = payment_info.get("amount", 0)
        description = payment_info.get("description", f"Payment for {url}")
        provider_name = payment_info.get("provider")

        # Select payment provider
        try:
            if provider_name and self._registry.has_provider(provider_name):
                provider = self._registry.get(provider_name)
            else:
                provider = self._registry.get_default()
        except (KeyError, RuntimeError) as e:
            logger.error("http402.no_provider", error=str(e))
            return response

        # Create payment
        result = await provider.create_payment(Decimal(str(amount)), description)
        if result.status == "failed":
            logger.error("http402.payment_failed", payment_id=result.payment_id)
            return response

        logger.info("http402.payment_initiated", payment_id=result.payment_id, amount=amount)

        # Retry original request with payment proof
        retry_headers = dict(kwargs.get("headers", {}))
        retry_headers["X-Payment-Id"] = result.payment_id
        retry_headers["X-Payment-Provider"] = provider.provider_name
        kwargs["headers"] = retry_headers

        retry_response = await session.request(method, url, **kwargs)
        logger.info("http402.retry", status=retry_response.status)
        return retry_response

    async def _parse_payment_info(self, response: aiohttp.ClientResponse) -> dict | None:
        """Extract payment information from a 402 response."""
        # Try JSON body first
        try:
            body = await response.json()
            if isinstance(body, dict):
                return {
                    "amount": body.get("amount", body.get("price", 0)),
                    "description": body.get("description", body.get("message", "")),
                    "provider": body.get("provider", body.get("payment_method")),
                    "destination": body.get("destination", body.get("account")),
                }
        except Exception:
            pass

        # Try headers
        amount = response.headers.get("X-Payment-Amount")
        if amount:
            return {
                "amount": float(amount),
                "description": response.headers.get("X-Payment-Description", ""),
                "provider": response.headers.get("X-Payment-Provider"),
                "destination": response.headers.get("X-Payment-Destination"),
            }

        # Try WWW-Authenticate header
        www_auth = response.headers.get("WWW-Authenticate", "")
        if "payment" in www_auth.lower():
            return {
                "amount": 0,
                "description": www_auth,
                "provider": None,
                "destination": None,
            }

        return None
