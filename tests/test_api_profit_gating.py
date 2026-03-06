"""Integration tests: API profit gating — 验证未收款调用被拦截、审计落库。"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent_core.config import ProfitGateConfig
from agent_core.economy.profit_gate import ProfitGate


def _make_profit_gate(
    balance: float = 10.0,
    enabled: bool = True,
) -> ProfitGate:
    config = ProfitGateConfig(
        enabled=enabled,
        require_confirmed_payment=True,
        min_balance_usd=0.50,
        min_gross_margin_ratio=0.20,
        max_cost_per_request_usd=0.10,
        hard_stop_balance_usd=0.10,
        reinvest_ratio=0.50,
        block_free_trial_when_gated=True,
    )
    ledger = MagicMock()
    ledger.get_balance = AsyncMock(return_value=balance)
    db = MagicMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    return ProfitGate(config=config, ledger=ledger, db=db)


class TestNoUnpaidCalls:
    """核心验证：不存在未收款的付费调用。"""

    def test_consecutive_unpaid_all_blocked(self):
        """连续 10 个未付费请求全部被拒绝。"""
        gate = _make_profit_gate()
        loop = asyncio.get_event_loop()
        for _ in range(10):
            decision = loop.run_until_complete(
                gate.check(is_paid=False, price_per_request=0.05)
            )
            assert decision["allowed"] is False

    def test_consecutive_paid_all_pass_positive_margin(self):
        """连续 10 个已付费请求全部通过，且毛利为正。"""
        gate = _make_profit_gate(balance=10.0)
        loop = asyncio.get_event_loop()
        for _ in range(10):
            decision = loop.run_until_complete(
                gate.check(is_paid=True, price_per_request=0.10, estimated_cost=0.02)
            )
            assert decision["allowed"] is True
            assert decision["estimated_margin_ratio"] > 0

    def test_hard_stop_blocks_everything(self):
        """余额低于硬止损，即使是付费请求也被拒绝。"""
        gate = _make_profit_gate(balance=0.05)
        loop = asyncio.get_event_loop()
        for is_paid in [True, False]:
            decision = loop.run_until_complete(
                gate.check(is_paid=is_paid, price_per_request=0.10)
            )
            assert decision["allowed"] is False


class TestAuditPersistence:
    """审计落库验证。"""

    def test_decision_writes_to_db(self):
        """每次门控决策都应写入 profit_gate_log 表。"""
        gate = _make_profit_gate()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            gate.check(is_paid=True, price_per_request=0.10, estimated_cost=0.02)
        )
        # 应该调用了 db.execute 和 db.commit
        gate._db.execute.assert_called()
        gate._db.commit.assert_called()

    def test_blocked_decision_also_logged(self):
        """被拦截的请求也应写入审计日志。"""
        gate = _make_profit_gate()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            gate.check(is_paid=False, price_per_request=0.05)
        )
        gate._db.execute.assert_called()
        # 验证 SQL 中包含 blocked
        call_args = gate._db.execute.call_args
        assert "blocked" in str(call_args)
