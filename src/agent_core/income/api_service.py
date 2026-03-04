"""Paid API service — the agent's own monetizable API endpoints."""

from __future__ import annotations

import time
from typing import Any, Optional

import structlog

log = structlog.get_logger()


class APIServiceManager:
    """
    Manages the agent's paid API services.

    The agent can create and serve paid API endpoints using FastAPI.
    Revenue model: per-request pricing via HTTP 402.
    """

    def __init__(self, ledger=None, http402_handler=None):
        self.ledger = ledger
        self.http402 = http402_handler
        self.services: dict[str, ServiceConfig] = {}
        self._app = None

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

    async def create_app(self):
        """Create the FastAPI application with all registered services."""
        try:
            from fastapi import FastAPI, Request, HTTPException
            from fastapi.responses import JSONResponse
        except ImportError:
            log.error("api_service.fastapi_not_installed")
            return None

        app = FastAPI(
            title="Self-Improve Agent API",
            description="Paid API services provided by an autonomous agent",
            version="0.1.0",
        )

        @app.get("/")
        async def root():
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

        # Create endpoints for each service
        for svc_name, svc_config in self.services.items():
            self._register_endpoint(app, svc_name, svc_config)

        self._app = app
        log.info("api_service.app_created", services=len(self.services))
        return app

    def _register_endpoint(self, app, name: str, config: "ServiceConfig") -> None:
        """Register a single paid endpoint."""
        from fastapi import Request
        from fastapi.responses import JSONResponse

        @app.post(f"/api/{name}")
        async def endpoint(request: Request):
            # Check payment
            if self.http402:
                paid = await self.http402.check_payment(request)
                if not paid:
                    return JSONResponse(
                        status_code=402,
                        content={
                            "error": "Payment Required",
                            "price": config.price_per_request,
                            "payment_info": "Include payment token in X-Payment-Token header",
                        },
                    )

            # Execute service
            try:
                body = await request.json()
                if config.handler:
                    result = await config.handler(body)
                else:
                    result = {"error": "Service not yet implemented"}

                # Record revenue
                if self.ledger:
                    await self.ledger.record_income(
                        amount=config.price_per_request,
                        source=f"api:{name}",
                        description=f"API call to {name}",
                    )

                config.total_requests += 1
                config.total_revenue += config.price_per_request

                return {"result": result, "service": name}

            except Exception as e:
                log.error("api_service.handler_error", service=name, error=str(e))
                return JSONResponse(
                    status_code=500,
                    content={"error": "Internal service error"},
                )

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
