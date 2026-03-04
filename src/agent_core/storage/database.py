"""Async SQLite database layer with WAL mode."""

from __future__ import annotations

import aiosqlite
import structlog
from pathlib import Path

logger = structlog.get_logger()


class Database:
    """Async SQLite database wrapper with WAL mode and table initialization."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(self.db_path))
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        await self._conn.execute("PRAGMA busy_timeout=5000")
        logger.info("database.connected", path=str(self.db_path))

    async def init_tables(self) -> None:
        """Create all required tables if they don't exist."""
        await self.executescript(_SCHEMA_SQL)
        logger.info("database.tables_initialized")

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    async def execute(self, sql: str, params: tuple = ()) -> aiosqlite.Cursor:
        return await self.conn.execute(sql, params)

    async def executemany(self, sql: str, params_seq: list[tuple]) -> aiosqlite.Cursor:
        return await self.conn.executemany(sql, params_seq)

    async def executescript(self, sql: str) -> None:
        await self.conn.executescript(sql)

    async def fetchone(self, sql: str, params: tuple = ()) -> aiosqlite.Row | None:
        cursor = await self.execute(sql, params)
        return await cursor.fetchone()

    async def fetchall(self, sql: str, params: tuple = ()) -> list[aiosqlite.Row]:
        cursor = await self.execute(sql, params)
        return await cursor.fetchall()

    async def commit(self) -> None:
        await self.conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
            logger.info("database.closed")


_SCHEMA_SQL = """
-- Ledger: financial transactions
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    amount REAL NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    category TEXT NOT NULL DEFAULT 'general',
    description TEXT NOT NULL DEFAULT '',
    counterparty TEXT NOT NULL DEFAULT '',
    payment_provider TEXT NOT NULL DEFAULT '',
    payment_id TEXT NOT NULL DEFAULT '',
    creator_share REAL NOT NULL DEFAULT 0.0
);

-- Audit log: self-modification history
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    file_changed TEXT NOT NULL,
    diff_summary TEXT NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    result TEXT NOT NULL CHECK (result IN ('success', 'failed', 'reverted')),
    commit_sha TEXT NOT NULL DEFAULT ''
);

-- Lineage: agent replication family tree
CREATE TABLE IF NOT EXISTS lineage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id TEXT NOT NULL,
    child_id TEXT NOT NULL,
    generation INTEGER NOT NULL DEFAULT 1,
    birth_time TEXT NOT NULL DEFAULT (datetime('now')),
    status TEXT NOT NULL DEFAULT 'alive' CHECK (status IN ('alive', 'dead')),
    code_hash TEXT NOT NULL DEFAULT '',
    deploy_location TEXT NOT NULL DEFAULT 'local'
);

-- Action history: recent agent actions for context
CREATE TABLE IF NOT EXISTS action_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    cycle_number INTEGER NOT NULL,
    observation TEXT NOT NULL DEFAULT '',
    thought TEXT NOT NULL DEFAULT '',
    action_name TEXT NOT NULL DEFAULT '',
    action_args TEXT NOT NULL DEFAULT '{}',
    result TEXT NOT NULL DEFAULT '',
    success INTEGER NOT NULL DEFAULT 1,
    reflection TEXT NOT NULL DEFAULT '',
    cost_usd REAL NOT NULL DEFAULT 0.0
);

-- Creator payouts: track payments to creator
CREATE TABLE IF NOT EXISTS creator_payouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    amount REAL NOT NULL,
    payment_provider TEXT NOT NULL DEFAULT '',
    payment_id TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed'))
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON ledger(timestamp);
CREATE INDEX IF NOT EXISTS idx_ledger_type ON ledger(type);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit(timestamp);
CREATE INDEX IF NOT EXISTS idx_action_history_cycle ON action_history(cycle_number);
CREATE INDEX IF NOT EXISTS idx_lineage_parent ON lineage(parent_id);
CREATE INDEX IF NOT EXISTS idx_lineage_child ON lineage(child_id);
"""
