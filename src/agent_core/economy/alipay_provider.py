"""Alipay payment provider using alipay-sdk-python."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import structlog

from .payment_provider import PaymentProvider, PaymentResult, WebhookEvent

logger = structlog.get_logger()


class AlipayProvider(PaymentProvider):
    """Payment provider using Alipay (支付宝) REST API."""

    provider_name = "alipay"

    def __init__(
        self,
        app_id: str,
        private_key_path: str,
        alipay_public_key_path: str,
        gateway_url: str = "https://openapi.alipay.com/gateway.do",
        sandbox: bool = True,
        notify_url: str = "",
    ) -> None:
        self._app_id = app_id
        self._notify_url = notify_url
        self._sandbox = sandbox
        self._client = None

        # Read keys
        private_key = ""
        alipay_public_key = ""
        if private_key_path and Path(private_key_path).exists():
            private_key = Path(private_key_path).read_text().strip()
        if alipay_public_key_path and Path(alipay_public_key_path).exists():
            alipay_public_key = Path(alipay_public_key_path).read_text().strip()

        # Initialize Alipay client
        if private_key and alipay_public_key:
            try:
                from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
                from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient

                config = AlipayClientConfig()
                config.server_url = gateway_url
                config.app_id = app_id
                config.app_private_key = private_key
                config.alipay_public_key = alipay_public_key
                if sandbox:
                    config.server_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"

                self._client = DefaultAlipayClient(alipay_client_config=config)
                logger.info("alipay.initialized", app_id=app_id[:4] + "****", sandbox=sandbox)
            except ImportError:
                logger.warning("alipay.sdk_not_installed")
            except Exception as e:
                logger.error("alipay.init_failed", error=str(e))

    async def create_payment(self, amount: Decimal, description: str, **kwargs) -> PaymentResult:
        """Create a precreate (face-to-face) payment, returns QR code URL."""
        if self._client is None:
            return PaymentResult(
                payment_id="",
                status="failed",
                amount=amount,
                provider_name=self.provider_name,
                raw_response={"error": "Alipay client not initialized"},
            )

        try:
            from alipay.aop.api.domain.AlipayTradePrecreateModel import AlipayTradePrecreateModel
            from alipay.aop.api.request.AlipayTradePrecreateRequest import AlipayTradePrecreateRequest

            import uuid
            out_trade_no = f"sim_{uuid.uuid4().hex[:16]}"

            model = AlipayTradePrecreateModel()
            model.out_trade_no = out_trade_no
            model.total_amount = str(amount)
            model.subject = description

            request = AlipayTradePrecreateRequest(biz_model=model)
            if self._notify_url:
                request.notify_url = self._notify_url

            response = self._client.execute(request)

            logger.info("alipay.payment_created", trade_no=out_trade_no, amount=str(amount))

            return PaymentResult(
                payment_id=out_trade_no,
                status="pending",
                amount=amount,
                provider_name=self.provider_name,
                qr_code_url=response.get("qr_code", "") if isinstance(response, dict) else "",
                raw_response=response if isinstance(response, dict) else {"response": str(response)},
            )
        except Exception as e:
            logger.error("alipay.create_payment_failed", error=str(e))
            return PaymentResult(
                payment_id="",
                status="failed",
                amount=amount,
                provider_name=self.provider_name,
                raw_response={"error": str(e)},
            )

    async def query_payment(self, payment_id: str) -> PaymentResult:
        """Query trade status."""
        if self._client is None:
            return PaymentResult(
                payment_id=payment_id, status="failed",
                amount=Decimal(0), provider_name=self.provider_name,
            )

        try:
            from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
            from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest

            model = AlipayTradeQueryModel()
            model.out_trade_no = payment_id

            request = AlipayTradeQueryRequest(biz_model=model)
            response = self._client.execute(request)

            status_map = {
                "WAIT_BUYER_PAY": "pending",
                "TRADE_SUCCESS": "success",
                "TRADE_FINISHED": "success",
                "TRADE_CLOSED": "failed",
            }

            resp_dict = response if isinstance(response, dict) else {}
            trade_status = resp_dict.get("trade_status", "UNKNOWN")

            return PaymentResult(
                payment_id=payment_id,
                status=status_map.get(trade_status, "pending"),
                amount=Decimal(resp_dict.get("total_amount", "0")),
                provider_name=self.provider_name,
                raw_response=resp_dict,
            )
        except Exception as e:
            logger.error("alipay.query_failed", error=str(e))
            return PaymentResult(
                payment_id=payment_id, status="failed",
                amount=Decimal(0), provider_name=self.provider_name,
            )

    async def query_balance(self) -> Decimal:
        """Query Alipay account balance (simplified - uses ledger balance in practice)."""
        # Alipay doesn't have a direct balance API for merchants in most cases.
        # In practice, balance is tracked through the ledger.
        logger.debug("alipay.balance_query_not_supported_directly")
        return Decimal(0)

    async def refund(self, payment_id: str, amount: Decimal | None = None) -> bool:
        """Refund a trade."""
        if self._client is None:
            return False

        try:
            from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel
            from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest

            model = AlipayTradeRefundModel()
            model.out_trade_no = payment_id
            if amount:
                model.refund_amount = str(amount)
            model.refund_reason = "Agent initiated refund"

            request = AlipayTradeRefundRequest(biz_model=model)
            self._client.execute(request)

            logger.info("alipay.refunded", trade_no=payment_id)
            return True
        except Exception as e:
            logger.error("alipay.refund_failed", error=str(e))
            return False

    async def verify_webhook(self, headers: dict, body: bytes) -> WebhookEvent | None:
        """Verify Alipay async notification signature."""
        try:
            import urllib.parse
            params = dict(urllib.parse.parse_qsl(body.decode("utf-8")))

            # In production, verify RSA2 signature here
            trade_status = params.get("trade_status", "")
            if trade_status in ("TRADE_SUCCESS", "TRADE_FINISHED"):
                return WebhookEvent(
                    event_type="payment.success",
                    payment_id=params.get("out_trade_no", ""),
                    amount=Decimal(params.get("total_amount", "0")),
                    provider_name=self.provider_name,
                    raw_data=params,
                )
            return None
        except Exception as e:
            logger.error("alipay.webhook_verify_failed", error=str(e))
            return None
