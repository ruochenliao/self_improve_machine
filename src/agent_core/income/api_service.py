"""Paid API service — the agent's own monetizable API endpoints.

Supports two modes:
- Free trial: No API key needed, limited usage (tracked by IP)
- Paid: API key with pre-paid credit balance, auto-deducted per request
"""

from __future__ import annotations

import os
import secrets
import time
from typing import Any

import structlog

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse

log = structlog.get_logger()

# Admin secret for management endpoints (set via env or default)
ADMIN_SECRET = os.environ.get("SIM_ADMIN_SECRET", "sim-admin-2026")

# Free trial limits per IP
FREE_TRIAL_MAX_REQUESTS = 20  # max free requests per IP per day


class APIServiceManager:
    """
    Manages the agent's paid API services with API Key authentication.

    Revenue model:
    - Users buy API keys with pre-paid credits
    - Each API call deducts from their credit balance
    - No key = free trial (limited requests per day)
    """

    def __init__(self, ledger=None, http402_handler=None, api_key_mgr=None, profit_gate=None):
        self.ledger = ledger
        self.http402 = http402_handler
        self.api_key_mgr = api_key_mgr
        self.profit_gate = profit_gate
        self.alipay_qr_url: str = ""
        self.wechat_qr_url: str = ""
        self.services: dict[str, ServiceConfig] = {}
        self._app = None
        self._free_trial_tracker: dict[str, list[float]] = {}  # ip -> [timestamps]
        # Survival experiment modules (set externally after init)
        self.survival_diary: Any = None
        self.content_generator: Any = None
        self.balance_monitor: Any = None
        self.state_machine: Any = None

    def register_service(
        self,
        name: str,
        description: str,
        price_per_request: float,
        handler=None,
    ) -> None:
        """Register a paid API service."""
        self.services[name] = ServiceConfig(
            name=name,
            description=description,
            price_per_request=price_per_request,
            handler=handler,
        )
        log.info(
            "api_service.registered",
            name=name,
            price=price_per_request,
        )

    def _check_free_trial(self, client_ip: str) -> bool:
        """Check if a free-trial IP has remaining requests today."""
        now = time.time()
        day_start = now - 86400
        if client_ip in self._free_trial_tracker:
            self._free_trial_tracker[client_ip] = [
                t for t in self._free_trial_tracker[client_ip] if t > day_start
            ]
        else:
            self._free_trial_tracker[client_ip] = []
        return len(self._free_trial_tracker[client_ip]) < FREE_TRIAL_MAX_REQUESTS

    def _record_free_trial(self, client_ip: str) -> None:
        """Record a free trial usage."""
        if client_ip not in self._free_trial_tracker:
            self._free_trial_tracker[client_ip] = []
        self._free_trial_tracker[client_ip].append(time.time())

    async def create_app(self):
        """Create the FastAPI application with all registered services."""
        app = FastAPI(
            title="SIM-Agent API",
            description="Paid API services provided by an autonomous self-improving AI agent",
            version="0.3.0",
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/")
        async def root(request: Request):
            accept = request.headers.get("accept", "")
            if "text/html" in accept:
                html_path = os.path.join(os.getcwd(), "index.html")
                if os.path.exists(html_path):
                    with open(html_path, "r") as f:
                        return HTMLResponse(content=f.read())
            return {
                "agent": "self-improve-machine",
                "services": {
                    name: {
                        "description": s.description,
                        "price_per_request": s.price_per_request,
                    }
                    for name, s in self.services.items()
                },
            }

        @app.get("/health")
        async def health():
            return {"status": "alive", "timestamp": time.time()}

        # Serve static files from data/ directory (for QR code images etc.)
        @app.get("/static/{filename:path}")
        async def serve_static(filename: str):
            data_dir = os.path.join(os.getcwd(), "data")
            file_path = os.path.join(data_dir, filename)
            # Security: prevent path traversal
            if not os.path.realpath(file_path).startswith(os.path.realpath(data_dir)):
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not os.path.isfile(file_path):
                return JSONResponse(status_code=404, content={"error": "Not found"})
            return FileResponse(file_path)

        # === Management endpoints (admin only) ===
        self._register_admin_routes(app)

        # === User self-service endpoints ===
        self._register_user_routes(app)

        # Create endpoints for each service
        for svc_name, svc_config in self.services.items():
            self._register_endpoint(app, svc_name, svc_config)

        self._app = app
        log.info("api_service.app_created", services=len(self.services))
        return app

    def _register_admin_routes(self, app: FastAPI) -> None:
        """Register admin management endpoints."""
        api_key_mgr = self.api_key_mgr

        @app.post("/admin/keys/create")
        async def admin_create_key(request: Request):
            body = await request.json()
            secret = body.get("admin_secret", "")
            if secret != ADMIN_SECRET:
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "API Key system not initialized"})
            key = await api_key_mgr.create_key(
                user_name=body.get("user_name", ""),
                email=body.get("email", ""),
                initial_credit=body.get("credit", 0.0),
                notes=body.get("notes", ""),
            )
            return {"api_key": key, "credit": body.get("credit", 0.0)}

        @app.post("/admin/keys/add-credit")
        async def admin_add_credit(request: Request):
            body = await request.json()
            secret = body.get("admin_secret", "")
            if secret != ADMIN_SECRET:
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "API Key system not initialized"})
            key = body.get("api_key", "")
            amount = body.get("amount", 0.0)
            if not key or amount <= 0:
                return JSONResponse(status_code=400, content={"error": "Invalid key or amount"})
            new_balance = await api_key_mgr.add_credit(key, amount)
            return {"api_key": key, "added": amount, "new_balance": new_balance}

        @app.post("/admin/keys/list")
        async def admin_list_keys(request: Request):
            body = await request.json()
            secret = body.get("admin_secret", "")
            if secret != ADMIN_SECRET:
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "API Key system not initialized"})
            keys = await api_key_mgr.list_keys()
            # Mask keys in list view
            for k in keys:
                full_key = k["api_key"]
                k["api_key"] = full_key[:8] + "..." + full_key[-6:]
            return {"keys": keys}

        @app.post("/admin/keys/deactivate")
        async def admin_deactivate_key(request: Request):
            body = await request.json()
            secret = body.get("admin_secret", "")
            if secret != ADMIN_SECRET:
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "API Key system not initialized"})
            key = body.get("api_key", "")
            ok = await api_key_mgr.deactivate(key)
            return {"deactivated": ok}

    def _register_user_routes(self, app: FastAPI) -> None:
        """Register user self-service endpoints."""
        api_key_mgr = self.api_key_mgr
        ledger = self.ledger
        mgr = self

        # Pricing plans (China market, CNY)
        PLANS = {
            "starter": {"price": 9.9, "credit": 9.9, "label": "入门版 (¥9.9)"},
            "growth": {"price": 29.9, "credit": 32.0, "label": "增长版 (¥29.9，赠送¥2.1额度)"},
            "pro": {"price": 99.0, "credit": 120.0, "label": "专业版 (¥99，赠送¥21额度)"},
        }

        @app.get("/api/balance")
        async def check_balance(request: Request):
            """Check API key credit balance."""
            key = _extract_api_key(request)
            if not key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Missing API key. Use header: Authorization: Bearer <key>"},
                )
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "API Key system not initialized"})
            balance = await api_key_mgr.get_balance(key)
            if balance is None:
                return JSONResponse(status_code=401, content={"error": "Invalid API key"})
            return {"credit_balance": balance}

        @app.get("/api/pricing")
        async def pricing():
            """List all services with pricing."""
            return {
                "services": {
                    name: {
                        "description": s.description,
                        "price_per_request": s.price_per_request,
                    }
                    for name, s in mgr.services.items()
                },
                "plans": PLANS,
                "free_trial": {
                    "requests_per_day": FREE_TRIAL_MAX_REQUESTS,
                    "note": "No API key needed for free trial",
                },
            }

        @app.get("/api/payment-info")
        async def payment_info():
            """Return payment QR code URLs for the purchase flow."""
            return {
                "alipay_qr_url": mgr.alipay_qr_url,
                "wechat_qr_url": mgr.wechat_qr_url,
            }

        @app.get("/api/profit-dashboard")
        async def profit_dashboard():
            """飞轮看板：展示 Agent 经济指标（余额、毛利、再投资额度、门控状态）。"""
            if mgr.profit_gate:
                return await mgr.profit_gate.get_dashboard()
            return {"error": "Profit gate not initialized"}

        @app.get("/api/survival-status")
        async def survival_status():
            """Return current survival tier, balance, burn rate, and TTL."""
            if mgr.balance_monitor:
                status = await mgr.balance_monitor.check()
                return status
            if mgr.state_machine:
                return mgr.state_machine.get_status()
            return {"error": "Survival system not initialized"}

        @app.get("/api/diary")
        async def get_diary(limit: int = 10, offset: int = 0):
            """Get survival diary entries."""
            if not mgr.survival_diary:
                return {"entries": [], "note": "Diary module not initialized"}
            entries = await mgr.survival_diary.get_entries(limit=limit, offset=offset)
            return {"entries": entries}

        @app.post("/api/diary/generate")
        async def generate_diary(request: Request):
            """Generate today's diary entry (admin)."""
            if not mgr.survival_diary:
                return JSONResponse(status_code=501, content={"error": "Diary not initialized"})
            try:
                body = await request.json()
            except Exception:
                body = {}
            date = body.get("date")
            entry = await mgr.survival_diary.generate_daily_entry(date)
            return entry

        @app.get("/api/content")
        async def get_content(date: str = ""):
            """Get auto-generated social media content for a date."""
            if not mgr.content_generator:
                return {"error": "Content generator not initialized"}
            content = await mgr.content_generator.generate_all(date or None)
            return content

        @app.post("/api/purchase")
        async def create_purchase(request: Request):
            """Create a purchase order. User selects plan, provides email, gets order ID + payment instructions."""
            try:
                body = await request.json()
            except Exception:
                return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

            plan_name = body.get("plan", "")
            email = body.get("email", "")
            payment_method = body.get("payment_method", "alipay")

            if plan_name not in PLANS:
                return JSONResponse(status_code=400, content={
                    "error": f"Invalid plan. Choose from: {list(PLANS.keys())}",
                })
            if not email or "@" not in email:
                return JSONResponse(status_code=400, content={"error": "Valid email required"})

            plan = PLANS[plan_name]
            order_id = f"SIM-{secrets.token_hex(6).upper()}"

            # Save to database
            if api_key_mgr:
                await api_key_mgr.db.execute(
                    """INSERT INTO purchase_orders (order_id, email, plan, amount, credit, payment_method, status)
                       VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
                    (order_id, email, plan_name, plan["price"], plan["credit"], payment_method),
                )
                await api_key_mgr.db.commit()

            log.info("purchase.created", order_id=order_id, plan=plan_name, email=email)
            return {
                "order_id": order_id,
                "plan": plan_name,
                "amount": plan["price"],
                "credit": plan["credit"],
                "currency": "CNY",
                "payment_method": payment_method,
                "instructions": f"请支付 ¥{plan['price']:.2f}，并在备注中填写订单号 {order_id}。支付后在页面提交付款凭证，系统人工核验通过后发放 API Key。",
            }

        @app.post("/api/purchase/confirm")
        async def confirm_purchase(request: Request):
            """User submits payment proof. No auto-approval; admin verification required."""
            try:
                body = await request.json()
            except Exception:
                return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

            order_id = body.get("order_id", "")
            if not order_id or not api_key_mgr:
                return JSONResponse(status_code=400, content={"error": "Missing order_id"})

            row = await api_key_mgr.db.fetchone(
                "SELECT * FROM purchase_orders WHERE order_id = ?", (order_id,)
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Order not found"})

            if row["status"] == "confirmed":
                return {
                    "order_id": order_id,
                    "status": "confirmed",
                    "api_key": row["api_key"],
                    "credit": row["credit"],
                    "message": "订单已确认，API Key 已发放。",
                }

            if row["status"] != "pending":
                return JSONResponse(status_code=400, content={
                    "error": f"Order status is '{row['status']}', cannot submit payment proof",
                })

            payer_name = str(body.get("payer_name", "")).strip()
            payment_channel = str(body.get("payment_channel", "")).strip() or row["payment_method"]
            payment_reference = str(body.get("payment_reference", "")).strip()
            paid_amount = body.get("paid_amount", row["amount"])

            proof_note = (
                f"[PAYMENT_PROOF] channel={payment_channel}; payer={payer_name}; "
                f"amount={paid_amount}; ref={payment_reference}; submitted_at=now"
            )
            merged_notes = f"{row['notes']}\n{proof_note}".strip()

            await api_key_mgr.db.execute(
                """UPDATE purchase_orders
                   SET notes = ?
                   WHERE order_id = ?""",
                (merged_notes, order_id),
            )
            await api_key_mgr.db.commit()

            log.info(
                "purchase.proof_submitted",
                order_id=order_id,
                payment_channel=payment_channel,
                paid_amount=paid_amount,
            )
            return {
                "order_id": order_id,
                "status": "pending",
                "message": "已提交付款凭证，系统将在人工核验后发放 API Key。",
            }

        @app.post("/admin/orders/list")
        async def admin_list_orders(request: Request):
            """Admin: list all purchase orders."""
            body = await request.json()
            if body.get("admin_secret") != ADMIN_SECRET:
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "Not initialized"})
            status_filter = body.get("status", "pending")
            rows = await api_key_mgr.db.fetchall(
                "SELECT * FROM purchase_orders WHERE status = ? ORDER BY created_at DESC",
                (status_filter,),
            )
            return {"orders": [dict(r) for r in rows]}

        @app.post("/admin/orders/approve")
        async def admin_approve_order(request: Request):
            """Admin: approve a pending order — generates API key and adds credit."""
            body = await request.json()
            if body.get("admin_secret") != ADMIN_SECRET:
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "Not initialized"})

            order_id = body.get("order_id", "")
            row = await api_key_mgr.db.fetchone(
                "SELECT * FROM purchase_orders WHERE order_id = ? AND status = 'pending'",
                (order_id,),
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Pending order not found"})

            # Create API key with credit
            api_key = await api_key_mgr.create_key(
                user_name=row["email"].split("@")[0],
                email=row["email"],
                initial_credit=row["credit"],
                notes=f"Purchase order {order_id}, plan={row['plan']}",
            )

            # Update order
            await api_key_mgr.db.execute(
                """UPDATE purchase_orders
                   SET status = 'confirmed', api_key = ?, confirmed_at = datetime('now')
                   WHERE order_id = ?""",
                (api_key, order_id),
            )
            await api_key_mgr.db.commit()

            # Record income
            if ledger:
                await ledger.record_income(
                    amount=row["amount"],
                    category="api_key_sale",
                    description=f"API key sale: {row['plan']} plan, order {order_id}",
                    counterparty=row["email"],
                )

            log.info("purchase.approved", order_id=order_id, credit=row["credit"])
            return {
                "order_id": order_id,
                "api_key": api_key,
                "credit": row["credit"],
                "email": row["email"],
            }

        @app.post("/admin/orders/reject")
        async def admin_reject_order(request: Request):
            """Admin: reject a purchase order."""
            body = await request.json()
            if body.get("admin_secret") != ADMIN_SECRET:
                return JSONResponse(status_code=403, content={"error": "Forbidden"})
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "Not initialized"})

            order_id = body.get("order_id", "")
            reason = body.get("reason", "")
            await api_key_mgr.db.execute(
                "UPDATE purchase_orders SET status = 'rejected', notes = ? WHERE order_id = ?",
                (reason, order_id),
            )
            await api_key_mgr.db.commit()
            return {"order_id": order_id, "status": "rejected"}

        @app.get("/api/order/{order_id}")
        async def check_order_status(order_id: str):
            """User: check the status of their purchase order."""
            if not api_key_mgr:
                return JSONResponse(status_code=501, content={"error": "Not initialized"})
            row = await api_key_mgr.db.fetchone(
                "SELECT order_id, email, plan, amount, credit, status, api_key, created_at, confirmed_at FROM purchase_orders WHERE order_id = ?",
                (order_id,),
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Order not found"})
            result = dict(row)
            # Only show API key if order is confirmed
            if result["status"] != "confirmed":
                result["api_key"] = ""
            return result

        # === Creator-to-Agent communication (external world → Agent memory) ===
        @app.post("/api/chat/message")
        async def receive_chat_message(request: Request):
            """Receive a message from the outside world. Agent will remember it.
            Body: {"message": "...", "sender": "creator|user|system"}
            """
            try:
                body = await request.json()
            except Exception:
                return JSONResponse(status_code=400, content={"error": "Invalid JSON"})
            message = body.get("message", "").strip()
            sender = body.get("sender", "creator").strip()
            if not message:
                return JSONResponse(status_code=400, content={"error": "Empty message"})
            # Store in the inbox queue (read by ReAct loop)
            if not hasattr(mgr, "_inbox"):
                mgr._inbox = []
            mgr._inbox.append({
                "message": message,
                "sender": sender,
                "timestamp": time.time(),
            })
            log.info("chat.message_received", sender=sender, length=len(message))
            return {"status": "received", "queued": len(mgr._inbox)}

        @app.get("/api/chat/messages")
        async def get_chat_messages():
            """Get pending messages (for debugging)."""
            inbox = getattr(mgr, "_inbox", [])
            return {"messages": inbox, "count": len(inbox)}

    def _create_handler(self, name: str, config: "ServiceConfig"):
        """Create a handler with API Key auth + credit deduction."""
        ledger = self.ledger
        api_key_mgr = self.api_key_mgr
        mgr = self  # reference to self for free trial tracking

        async def handler(request: Request):
            try:
                api_key = _extract_api_key(request)
                is_paid = False

                # Auth flow: check API key if provided
                if api_key and api_key_mgr:
                    key_info = await api_key_mgr.authenticate(api_key)
                    if key_info is None:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Invalid or deactivated API key"},
                        )
                    if not await api_key_mgr.has_credit(api_key, config.price_per_request):
                        return JSONResponse(
                            status_code=402,
                            content={
                                "error": "Insufficient credit",
                                "required": config.price_per_request,
                                "balance": key_info["credit_balance"],
                                "top_up": "POST /admin/keys/add-credit",
                            },
                        )
                    is_paid = True
                elif config.price_per_request > 0:
                    # No key: free trial mode
                    client_ip = request.client.host if request.client else "unknown"
                    if not mgr._check_free_trial(client_ip):
                        return JSONResponse(
                            status_code=402,
                            content={
                                "error": "Free trial limit reached (20 requests/day). Get an API key for unlimited access.",
                                "pricing": f"${config.price_per_request}/request",
                                "get_key": "Visit the landing page to purchase an API key — instant delivery!",
                            },
                        )

                body = await request.json()

                # === 利润门控检查 ===
                if mgr.profit_gate and config.price_per_request > 0:
                    gate_decision = await mgr.profit_gate.check(
                        is_paid=is_paid,
                        price_per_request=config.price_per_request,
                    )
                    if not gate_decision["allowed"]:
                        log.warning(
                            "api_service.profit_gate_blocked",
                            service=name,
                            reason=gate_decision["reason"],
                        )
                        return JSONResponse(
                            status_code=503,
                            content={
                                "error": "Service temporarily paused (cost control)",
                                "reason": gate_decision["reason"],
                            },
                        )

                if config.handler:
                    result = await config.handler(body)
                else:
                    result = {"error": "Service not yet implemented"}

                # 提取实际成本并写入利润审计（闭环追踪）
                actual_cost = result.pop("_actual_cost_usd", None) if isinstance(result, dict) else None
                if mgr.profit_gate and actual_cost is not None and is_paid:
                    try:
                        await mgr.profit_gate.record_actual(
                            service=name,
                            revenue=config.price_per_request,
                            cost=actual_cost,
                        )
                    except Exception:
                        pass  # 审计记录失败不阻断请求

                # Deduct credit if paid user
                if is_paid and api_key and api_key_mgr:
                    await api_key_mgr.deduct(api_key, config.price_per_request, name)

                # Record income in ledger
                if ledger and config.price_per_request > 0 and is_paid:
                    await ledger.record_income(
                        amount=config.price_per_request,
                        category=f"api:{name}",
                        description=f"Paid API call to {name}",
                        counterparty=api_key[:8] + "..." if api_key else "free_trial",
                    )

                # Track free trial
                if not is_paid:
                    client_ip = request.client.host if request.client else "unknown"
                    mgr._record_free_trial(client_ip)

                config.total_requests += 1
                config.total_revenue += config.price_per_request if is_paid else 0
                return {"result": result, "service": name}
            except Exception as e:
                log.error("api_service.handler_error", service=name, error=str(e))
                return JSONResponse(status_code=500, content={"error": "Internal service error"})

        handler.__name__ = f"api_{name.replace('-', '_')}"
        return handler

    def _register_endpoint(self, app, name: str, config: "ServiceConfig") -> None:
        """Register a single paid endpoint."""
        handler = self._create_handler(name, config)
        app.add_api_route(f"/api/{name}", handler, methods=["POST"], response_model=None)

    async def start_server(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Start the API server."""
        if not self._app:
            await self.create_app()

        if not self._app:
            log.error("api_service.cannot_start")
            return

        try:
            import uvicorn
            config = uvicorn.Config(
                self._app, host=host, port=port, log_level="info"
            )
            server = uvicorn.Server(config)
            log.info("api_service.starting", host=host, port=port)
            await server.serve()
        except ImportError:
            log.error("api_service.uvicorn_not_installed")

    def get_stats(self) -> dict[str, Any]:
        """Get API service statistics."""
        return {
            "services": len(self.services),
            "total_requests": sum(s.total_requests for s in self.services.values()),
            "total_revenue": sum(s.total_revenue for s in self.services.values()),
            "by_service": {
                name: {
                    "requests": s.total_requests,
                    "revenue": s.total_revenue,
                    "price": s.price_per_request,
                }
                for name, s in self.services.items()
            },
        }


class ServiceConfig:
    """Configuration for a single API service."""

    def __init__(
        self,
        name: str,
        description: str,
        price_per_request: float,
        handler=None,
    ):
        self.name = name
        self.description = description
        self.price_per_request = price_per_request
        self.handler = handler
        self.total_requests: int = 0
        self.total_revenue: float = 0.0


def _extract_api_key(request: Request) -> str | None:
    """Extract API key from Authorization header or query param."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    # Also support ?api_key=xxx query param
    key = request.query_params.get("api_key")
    return key if key else None
