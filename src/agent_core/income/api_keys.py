"""API Key management — authentication and credit-based billing."""

from __future__ import annotations

import secrets
import structlog

from agent_core.storage.database import Database

log = structlog.get_logger()


class APIKeyManager:
    """Manages API keys with pre-paid credit balances.

    Flow:
    1. Admin creates a key via create_key() with an initial credit.
    2. User calls API with header `Authorization: Bearer <key>`.
    3. Middleware calls authenticate() → checks key exists, is active, has enough credit.
    4. After serving, deduct() subtracts the service price from credit balance.
    """

    def __init__(self, db: Database) -> None:
        self.db = db

    async def create_key(
        self,
        user_name: str = "",
        email: str = "",
        initial_credit: float = 0.0,
        notes: str = "",
    ) -> str:
        """Create a new API key and return it."""
        key = f"sim_{secrets.token_hex(24)}"
        await self.db.execute(
            """INSERT INTO api_keys (api_key, user_name, email, credit_balance, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (key, user_name, email, initial_credit, notes),
        )
        await self.db.commit()
        log.info("api_key.created", user=user_name, credit=initial_credit)
        return key

    async def authenticate(self, key: str) -> dict | None:
        """Validate an API key. Returns key info dict or None if invalid."""
        row = await self.db.fetchone(
            "SELECT * FROM api_keys WHERE api_key = ? AND is_active = 1", (key,)
        )
        if row is None:
            return None
        return dict(row)

    async def has_credit(self, key: str, amount: float) -> bool:
        """Check if key has enough credit for a request."""
        row = await self.db.fetchone(
            "SELECT credit_balance FROM api_keys WHERE api_key = ? AND is_active = 1",
            (key,),
        )
        if row is None:
            return False
        return row["credit_balance"] >= amount

    async def deduct(self, key: str, amount: float, service_name: str) -> bool:
        """Deduct credit from key after serving a request."""
        row = await self.db.fetchone(
            "SELECT credit_balance FROM api_keys WHERE api_key = ?", (key,)
        )
        if row is None or row["credit_balance"] < amount:
            return False

        await self.db.execute(
            """UPDATE api_keys
               SET credit_balance = credit_balance - ?,
                   total_spent = total_spent + ?,
                   total_requests = total_requests + 1,
                   last_used_at = datetime('now')
               WHERE api_key = ?""",
            (amount, amount, key),
        )
        await self.db.execute(
            """INSERT INTO api_key_usage (api_key, service_name, amount_charged)
               VALUES (?, ?, ?)""",
            (key, service_name, amount),
        )
        await self.db.commit()
        return True

    async def add_credit(self, key: str, amount: float) -> float:
        """Add credit to a key. Returns new balance."""
        await self.db.execute(
            "UPDATE api_keys SET credit_balance = credit_balance + ? WHERE api_key = ?",
            (amount, key),
        )
        await self.db.commit()
        row = await self.db.fetchone(
            "SELECT credit_balance FROM api_keys WHERE api_key = ?", (key,)
        )
        new_balance = row["credit_balance"] if row else 0.0
        log.info("api_key.credit_added", key_suffix=key[-6:], added=amount, balance=new_balance)
        return new_balance

    async def get_balance(self, key: str) -> float | None:
        """Get current credit balance for a key."""
        row = await self.db.fetchone(
            "SELECT credit_balance FROM api_keys WHERE api_key = ? AND is_active = 1",
            (key,),
        )
        return row["credit_balance"] if row else None

    async def deactivate(self, key: str) -> bool:
        """Deactivate an API key."""
        cursor = await self.db.execute(
            "UPDATE api_keys SET is_active = 0 WHERE api_key = ?", (key,)
        )
        await self.db.commit()
        return cursor.rowcount > 0

    async def list_keys(self) -> list[dict]:
        """List all API keys (admin use)."""
        rows = await self.db.fetchall(
            """SELECT api_key, user_name, email, credit_balance, total_spent,
                      total_requests, created_at, last_used_at, is_active
               FROM api_keys ORDER BY created_at DESC"""
        )
        return [dict(r) for r in rows]
