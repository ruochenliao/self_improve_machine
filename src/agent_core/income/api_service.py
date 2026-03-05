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

    def __init__(self, ledger=None, http402_handler=None, api_key_mgr=None):
        self.ledger = ledger
        self.http402 = http402_handler
        self.api_key_mgr = api_key_mgr
        self.alipay_qr_url: str = ""
        self.wechat_qr_url: str = ""
        self.services: dict[str, ServiceConfig] = {}
        self._app = None
        self._free_trial_tracker: dict[str, list[float]] = {}  # ip -> [timestamps]

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

        # Pricing plans
        PLANS = {
            "starter": {"price": 1.0, "credit": 1.0, "label": "Starter ($1)"},
            "standard": {"price": 5.0, "credit": 5.0, "label": "Standard ($5)"},
            "pro": {"price": 10.0, "credit": 10.0, "label": "Pro ($10)"},
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
                "payment_method": payment_method,
                "instructions": f"Please transfer ${plan['price']:.2f} and include '{order_id}' in the payment note/memo. After payment, click 'I have paid' on the page.",
            }

        @app.post("/api/purchase/confirm")
        async def confirm_purchase(request: Request):
            """User confirms they have paid. Auto-generate API key immediately (trust-first model)."""
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
                    "message": "Order already confirmed. Here is your API key.",
                }
            if row["status"] != "pending":
                return JSONResponse(status_code=400, content={
                    "error": f"Order status is '{row['status']}', cannot confirm",
                })

            # AUTO-APPROVE: Generate API key immediately (trust-first, verify later)
            api_key = await api_key_mgr.create_key(
                user_name=row["email"].split("@")[0],
                email=row["email"],
                initial_credit=row["credit"],
                notes=f"Auto-approved purchase {order_id}, plan={row['plan']}",
            )

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
                    description=f"Auto-approved: {row['plan']} plan, order {order_id}",
                    counterparty=row["email"],
                )

            log.info("purchase.auto_approved", order_id=order_id, credit=row["credit"])
            return {
                "order_id": order_id,
                "status": "confirmed",
                "api_key": api_key,
                "credit": row["credit"],
                "message": "Payment confirmed! Your API key is ready to use.",
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
                if config.handler:
                    result = await config.handler(body)
                else:
                    result = {"error": "Service not yet implemented"}

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
