"""Alipay Face-to-Face Payment (当面付) integration.

Uses alipay.trade.precreate to generate QR codes for payment,
and receives async notifications (notify_url) when payment completes.
"""

from __future__ import annotations

import os
import logging
from typing import Optional

import structlog

log = structlog.get_logger()

# Lazy-load the heavy SDK imports
_sdk_available = False
try:
    from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
    from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
    from alipay.aop.api.domain.AlipayTradePrecreateModel import AlipayTradePrecreateModel
    from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
    from alipay.aop.api.request.AlipayTradePrecreateRequest import AlipayTradePrecreateRequest
    from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
    from alipay.aop.api.util.SignatureUtils import verify_with_rsa
    _sdk_available = True
except ImportError:
    log.warning("alipay_payment.sdk_not_installed", hint="pip install alipay-sdk-python")


class AlipayPayment:
    """Wrapper for Alipay Face-to-Face (当面付) payment."""

    def __init__(
        self,
        app_id: str = "",
        app_private_key: str = "",
        alipay_public_key: str = "",
        notify_url: str = "",
        sandbox: bool = False,
    ):
        self.app_id = app_id or os.environ.get("ALIPAY_APP_ID", "")
        self.app_private_key = app_private_key or os.environ.get("ALIPAY_APP_PRIVATE_KEY", "")
        self.alipay_public_key = alipay_public_key or os.environ.get("ALIPAY_PUBLIC_KEY", "")
        self.notify_url = notify_url or os.environ.get("ALIPAY_NOTIFY_URL", "")
        self.sandbox = sandbox
        self._client = None

        if not all([self.app_id, self.app_private_key, self.alipay_public_key]):
            log.warning(
                "alipay_payment.missing_config",
                hint="Set ALIPAY_APP_ID, ALIPAY_APP_PRIVATE_KEY, ALIPAY_PUBLIC_KEY",
            )

    @property
    def is_configured(self) -> bool:
        """Check if Alipay is properly configured."""
        return bool(
            _sdk_available
            and self.app_id
            and self.app_private_key
            and self.alipay_public_key
        )

    def _get_client(self) -> "DefaultAlipayClient":
        """Get or create the Alipay client (lazy init)."""
        if self._client is not None:
            return self._client

        if not _sdk_available:
            raise RuntimeError("alipay-sdk-python not installed")

        config = AlipayClientConfig()
        config.app_id = self.app_id
        config.app_private_key = self.app_private_key
        config.alipay_public_key = self.alipay_public_key

        if self.sandbox:
            config.server_url = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
        else:
            config.server_url = "https://openapi.alipay.com/gateway.do"

        # Suppress noisy SDK logging
        logging.getLogger("alipay.aop.api").setLevel(logging.WARNING)

        self._client = DefaultAlipayClient(alipay_client_config=config)
        log.info("alipay_payment.client_created", app_id=self.app_id, sandbox=self.sandbox)
        return self._client

    def precreate(
        self,
        out_trade_no: str,
        total_amount: str,
        subject: str,
        timeout_express: str = "30m",
    ) -> dict:
        """Create a pre-order and get QR code URL.

        Args:
            out_trade_no: Merchant order number (unique per order)
            total_amount: Amount in CNY, e.g. "9.90"
            subject: Order title/description
            timeout_express: Payment timeout, e.g. "30m", "1h"

        Returns:
            {"success": True, "qr_code": "https://qr.alipay.com/xxx", "out_trade_no": "..."}
            or {"success": False, "error": "..."}
        """
        if not self.is_configured:
            return {"success": False, "error": "Alipay not configured"}

        try:
            client = self._get_client()

            model = AlipayTradePrecreateModel()
            model.out_trade_no = out_trade_no
            model.total_amount = total_amount
            model.subject = subject
            model.timeout_express = timeout_express

            request = AlipayTradePrecreateRequest(biz_model=model)
            if self.notify_url:
                request.notify_url = self.notify_url

            response = client.execute(request)

            log.info(
                "alipay_payment.precreate",
                out_trade_no=out_trade_no,
                amount=total_amount,
                response_type=type(response).__name__,
            )

            # The SDK returns the response body as a dict-like object
            if isinstance(response, dict):
                resp = response
            elif hasattr(response, "body"):
                resp = response.body if isinstance(response.body, dict) else {"raw": str(response.body)}
            else:
                # For string responses, the SDK returns the parsed response
                resp = {"raw": str(response)}

            # Check for qr_code in various response formats
            qr_code = None
            if isinstance(resp, dict):
                qr_code = resp.get("qr_code") or resp.get("qrCode")
                code = resp.get("code", "")
                msg = resp.get("msg", "")
                sub_code = resp.get("sub_code", "")
                sub_msg = resp.get("sub_msg", "")
            else:
                # Response might be a string containing the qr_code URL
                resp_str = str(resp)
                if "qr.alipay.com" in resp_str:
                    import re
                    match = re.search(r'https://qr\.alipay\.com/\S+', resp_str)
                    if match:
                        qr_code = match.group(0).rstrip('"\'')
                code = ""
                msg = resp_str
                sub_code = ""
                sub_msg = ""

            if qr_code:
                return {
                    "success": True,
                    "qr_code": qr_code,
                    "out_trade_no": out_trade_no,
                }

            # Try to get qr_code from string response
            resp_str = str(response)
            if "qr.alipay.com" in resp_str:
                import re
                match = re.search(r'https://qr\.alipay\.com/\S+', resp_str)
                if match:
                    return {
                        "success": True,
                        "qr_code": match.group(0).rstrip('"\''),
                        "out_trade_no": out_trade_no,
                    }

            error_msg = sub_msg or msg or str(resp)
            log.error("alipay_payment.precreate_failed", error=error_msg, code=code, sub_code=sub_code)
            return {"success": False, "error": error_msg, "code": code, "sub_code": sub_code}

        except Exception as e:
            log.error("alipay_payment.precreate_error", error=str(e))
            return {"success": False, "error": str(e)}

    def query_trade(self, out_trade_no: str) -> dict:
        """Query trade status by merchant order number.

        Returns:
            {"success": True, "trade_status": "TRADE_SUCCESS", "trade_no": "...", ...}
            or {"success": False, "error": "..."}
        """
        if not self.is_configured:
            return {"success": False, "error": "Alipay not configured"}

        try:
            client = self._get_client()

            model = AlipayTradeQueryModel()
            model.out_trade_no = out_trade_no

            request = AlipayTradeQueryRequest(biz_model=model)
            response = client.execute(request)

            if isinstance(response, dict):
                resp = response
            elif hasattr(response, "body"):
                resp = response.body if isinstance(response.body, dict) else {}
            else:
                resp = {}

            trade_status = ""
            trade_no = ""
            buyer_logon_id = ""

            if isinstance(resp, dict):
                trade_status = resp.get("trade_status", "")
                trade_no = resp.get("trade_no", "")
                buyer_logon_id = resp.get("buyer_logon_id", "")

            return {
                "success": bool(trade_status),
                "trade_status": trade_status,
                "trade_no": trade_no,
                "buyer_logon_id": buyer_logon_id,
                "raw": resp,
            }

        except Exception as e:
            log.error("alipay_payment.query_error", error=str(e))
            return {"success": False, "error": str(e)}

    def verify_notify(self, params: dict) -> bool:
        """Verify Alipay async notification signature.

        Args:
            params: All POST parameters from Alipay notification (as dict).

        Returns:
            True if signature is valid.
        """
        if not self.alipay_public_key:
            log.error("alipay_payment.verify_no_public_key")
            return False

        try:
            sign = params.get("sign", "")
            sign_type = params.get("sign_type", "RSA2")

            if not sign:
                return False

            # Build the string to verify: sorted key=value pairs, excluding sign and sign_type
            filtered = {k: v for k, v in params.items() if k not in ("sign", "sign_type") and v}
            sorted_params = sorted(filtered.items())
            unsigned_str = "&".join(f"{k}={v}" for k, v in sorted_params)

            message = bytes(unsigned_str, encoding="utf-8")

            result = verify_with_rsa(self.alipay_public_key, message, sign)
            log.info("alipay_payment.verify_notify", result=result)
            return result

        except Exception as e:
            log.error("alipay_payment.verify_error", error=str(e))
            return False


def _format_amount(amount: float | int | str) -> str:
    """Format amount to 2 decimal places string for Alipay."""
    return f"{float(amount):.2f}"
