"""Tests for ProfitGate — 利润门控核心逻辑验证。"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from agent_core.config import ProfitGateConfig
from agent_core.economy.profit_gate import ProfitGate


def _make_gate(
    balance: float = 10.0,
    enabled: bool = True,
    require_confirmed_payment: bool = True,
    block_free_trial: bool = True,
    min_balance: float = 0.50,
    hard_stop: float = 0.10,
    max_cost: float = 0.10,
    min_margin: float = 0.20,
) -> ProfitGate:
    config = ProfitGateConfig(
        enabled=enabled,
        require_confirmed_payment=require_confirmed_payment,
        min_balance_usd=min_balance,
        min_gross_margin_ratio=min_margin,
        max_cost_per_request_usd=max_cost,
        hard_stop_balance_usd=hard_stop,
        reinvest_ratio=0.50,
        block_free_trial_when_gated=block_free_trial,
    )
    ledger = MagicMock()
    ledger.get_balance = AsyncMock(return_value=balance)
    return ProfitGate(config=config, ledger=ledger, db=None)


class TestProfitGateBasic:
    """基本门控行为。"""

    def test_disabled_gate_always_allows(self):
        gate = _make_gate(enabled=False)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=False, price_per_request=0.01)
        )
        assert decision["allowed"] is True
        assert decision["reason"] == "profit_gate_disabled"

    def test_hard_stop_blocks(self):
        gate = _make_gate(balance=0.05, hard_stop=0.10)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=True, price_per_request=0.10)
        )
        assert decision["allowed"] is False
        assert "hard_stop" in decision["reason"]

    def test_low_balance_blocks(self):
        gate = _make_gate(balance=0.30, min_balance=0.50)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=True, price_per_request=0.10)
        )
        assert decision["allowed"] is False
        assert "low_balance" in decision["reason"]


class TestUnpaidBlocking:
    """未收款请求阻断。"""

    def test_unpaid_blocked_when_gated(self):
        gate = _make_gate(require_confirmed_payment=True, block_free_trial=True)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=False, price_per_request=0.01)
        )
        assert decision["allowed"] is False
        assert "unpaid_request_blocked" in decision["reason"]

    def test_unpaid_allowed_when_free_trial_not_blocked(self):
        gate = _make_gate(require_confirmed_payment=True, block_free_trial=False)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=False, price_per_request=0.01)
        )
        assert decision["allowed"] is True

    def test_unpaid_allowed_when_payment_not_required(self):
        gate = _make_gate(require_confirmed_payment=False)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=False, price_per_request=0.01)
        )
        assert decision["allowed"] is True


class TestCostAndMargin:
    """成本上限与毛利率检查。"""

    def test_cost_exceeded_blocks(self):
        gate = _make_gate(max_cost=0.05)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=True, price_per_request=0.10, estimated_cost=0.08)
        )
        assert decision["allowed"] is False
        assert "cost_exceeded" in decision["reason"]

    def test_margin_below_threshold_blocks(self):
        """价格 $0.03，成本 $0.03 → 毛利率 0% < 20%。"""
        gate = _make_gate(min_margin=0.20, max_cost=0.10)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=True, price_per_request=0.03, estimated_cost=0.03)
        )
        assert decision["allowed"] is False
        assert "margin_below_threshold" in decision["reason"]

    def test_healthy_margin_allows(self):
        """价格 $0.10，成本 $0.02 → 毛利率 80% > 20%。"""
        gate = _make_gate(min_margin=0.20, max_cost=0.10)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=True, price_per_request=0.10, estimated_cost=0.02)
        )
        assert decision["allowed"] is True
        assert decision["reason"] == "approved"
        assert decision["estimated_margin_ratio"] == pytest.approx(0.80, abs=0.01)


class TestPaidApproval:
    """正常付费请求应当被放行。"""

    def test_paid_request_with_sufficient_balance(self):
        gate = _make_gate(balance=10.0)
        decision = asyncio.get_event_loop().run_until_complete(
            gate.check(is_paid=True, price_per_request=0.10, estimated_cost=0.02)
        )
        assert decision["allowed"] is True
        assert decision["reason"] == "approved"


class TestDashboard:
    """飞轮看板。"""

    def test_dashboard_returns_all_fields(self):
        gate = _make_gate(balance=5.0)
        gate._ledger.get_report = AsyncMock(return_value={
            "breakdown": [
                {"type": "income", "total": 2.0, "category": "api", "count": 10},
                {"type": "expense", "total": 0.5, "category": "llm", "count": 10},
            ]
        })
        dashboard = asyncio.get_event_loop().run_until_complete(gate.get_dashboard())
        assert "balance_usd" in dashboard
        assert "gross_profit_24h" in dashboard
        assert "reinvest_budget_usd" in dashboard
        assert dashboard["balance_usd"] == 5.0
        assert dashboard["gross_profit_24h"] == 1.5
        assert dashboard["reinvest_budget_usd"] == 0.75
