"""Ledger: financial transaction tracking and balance computation."""

from __future__ import annotations

from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.storage.database import Database

logger = structlog.get_logger()


class Ledger:
    """Double-entry ledger backed by SQLite for tracking all financial transactions."""

    def __init__(self, db: Database) -> None:
        self._db = db

    async def record_income(
        self,
        amount: float,
        category: str = "general",
        description: str = "",
        counterparty: str = "",
        payment_provider: str = "",
        payment_id: str = "",
        creator_share: float = 0.0,
    ) -> int:
        """Record an income transaction. Returns the transaction ID."""
        cursor = await self._db.execute(
            """INSERT INTO ledger (amount, type, category, description, counterparty,
               payment_provider, payment_id, creator_share)
               VALUES (?, 'income', ?, ?, ?, ?, ?, ?)""",
            (amount, category, description, counterparty, payment_provider, payment_id, creator_share),
        )
        await self._db.commit()
        txn_id = cursor.lastrowid or 0
        logger.info(
            "ledger.income",
            amount=amount,
            category=category,
            creator_share=creator_share,
            txn_id=txn_id,
        )
        return txn_id

    async def record_expense(
        self,
        amount: float,
        category: str = "general",
        description: str = "",
        counterparty: str = "",
        payment_provider: str = "",
        payment_id: str = "",
    ) -> int:
        """Record an expense transaction. Amount should be positive."""
        cursor = await self._db.execute(
            """INSERT INTO ledger (amount, type, category, description, counterparty,
               payment_provider, payment_id)
               VALUES (?, 'expense', ?, ?, ?, ?, ?)""",
            (amount, category, description, counterparty, payment_provider, payment_id),
        )
        await self._db.commit()
        txn_id = cursor.lastrowid or 0
        logger.info("ledger.expense", amount=amount, category=category, txn_id=txn_id)
        return txn_id

    async def get_balance(self) -> float:
        """Compute current balance: sum(income) - sum(expense)."""
        row = await self._db.fetchone(
            """SELECT
                COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) -
                COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)
                AS balance
               FROM ledger"""
        )
        return float(row["balance"]) if row else 0.0

    async def get_burn_rate(self, hours: int = 1) -> float:
        """Compute average expense per hour over the last N hours."""
        row = await self._db.fetchone(
            """SELECT COALESCE(SUM(amount), 0) AS total_expense
               FROM ledger
               WHERE type = 'expense'
               AND timestamp >= datetime('now', ?)""",
            (f"-{hours} hours",),
        )
        total = float(row["total_expense"]) if row else 0.0
        return total / max(hours, 1)

    async def get_total_creator_share(self) -> float:
        """Get total creator share amount recorded."""
        row = await self._db.fetchone(
            "SELECT COALESCE(SUM(creator_share), 0) AS total FROM ledger"
        )
        return float(row["total"]) if row else 0.0

    async def get_report(self, hours: int = 24) -> dict:
        """Generate a financial report for the last N hours."""
        rows = await self._db.fetchall(
            """SELECT type, category, SUM(amount) as total, COUNT(*) as count
               FROM ledger
               WHERE timestamp >= datetime('now', ?)
               GROUP BY type, category
               ORDER BY type, total DESC""",
            (f"-{hours} hours",),
        )
        balance = await self.get_balance()
        burn_rate = await self.get_burn_rate()
        ttl = balance / burn_rate if burn_rate > 0 else float("inf")

        return {
            "balance_usd": balance,
            "burn_rate_per_hour": burn_rate,
            "time_to_live_hours": ttl,
            "period_hours": hours,
            "breakdown": [
                {
                    "type": row["type"],
                    "category": row["category"],
                    "total": float(row["total"]),
                    "count": int(row["count"]),
                }
                for row in rows
            ],
        }

    async def get_recent_transactions(self, limit: int = 20) -> list[dict]:
        """Get most recent transactions."""
        rows = await self._db.fetchall(
            "SELECT * FROM ledger ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [dict(row) for row in rows]
