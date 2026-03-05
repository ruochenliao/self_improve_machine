"""Shared pytest fixtures for agent_core tests."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio

# Project root for path-based tests
PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """Provide a temporary data directory for tests."""
    data = tmp_path / "data"
    data.mkdir()
    return data


@pytest_asyncio.fixture
async def database(tmp_data_dir: Path):
    """Provide a fresh in-memory-like temporary database."""
    from agent_core.storage.database import Database
    db = Database(tmp_data_dir / "test.db")
    await db.connect()
    await db.init_tables()
    yield db
    await db.close()


@pytest_asyncio.fixture
async def ledger(database):
    """Provide a Ledger instance backed by the temp database."""
    from agent_core.economy.ledger import Ledger
    return Ledger(database)


@pytest.fixture
def state_machine():
    """Provide a fresh SurvivalStateMachine."""
    from agent_core.survival.state_machine import SurvivalStateMachine
    return SurvivalStateMachine()


@pytest.fixture
def tool_registry():
    """Provide a fresh ToolRegistry (reset singleton)."""
    from agent_core.tools.registry import ToolRegistry
    ToolRegistry.reset()
    reg = ToolRegistry()
    yield reg
    ToolRegistry.reset()


@pytest.fixture
def audit_logger(tmp_data_dir: Path):
    """Provide an AuditLogger writing to temp directory."""
    from agent_core.self_mod.audit import AuditLogger
    return AuditLogger(db=None, log_dir=tmp_data_dir / "audit")
