"""Tests for the survival state machine and balance monitor."""

from __future__ import annotations

import pytest
import pytest_asyncio

from agent_core.survival.state_machine import (
    SurvivalStateMachine,
    SurvivalTier,
    TierConfig,
)


class TestSurvivalTier:
    """Test SurvivalTier enum."""

    def test_tier_values(self):
        assert SurvivalTier.NORMAL.value == "normal"
        assert SurvivalTier.LOW_COMPUTE.value == "low_compute"
        assert SurvivalTier.CRITICAL.value == "critical"
        assert SurvivalTier.DEAD.value == "dead"

    def test_all_tiers_exist(self):
        assert len(SurvivalTier) == 4


class TestSurvivalStateMachine:
    """Test state machine transitions and configuration."""

    def test_default_state_is_normal(self, state_machine):
        assert state_machine.current_tier == SurvivalTier.NORMAL

    def test_configure_thresholds(self, state_machine):
        state_machine.configure_thresholds(normal=200.0, low_compute=50.0, critical=5.0)
        assert state_machine.tier_configs[SurvivalTier.NORMAL].balance_threshold_usd == 200.0
        assert state_machine.tier_configs[SurvivalTier.LOW_COMPUTE].balance_threshold_usd == 50.0
        assert state_machine.tier_configs[SurvivalTier.CRITICAL].balance_threshold_usd == 5.0

    def test_transition_normal_to_low(self, state_machine):
        state_machine.configure_thresholds(normal=100, low_compute=10, critical=1)
        tier = state_machine.update_balance(50.0)
        assert tier == SurvivalTier.LOW_COMPUTE

    def test_transition_low_to_critical(self, state_machine):
        state_machine.configure_thresholds(normal=100, low_compute=10, critical=1)
        tier = state_machine.update_balance(3.0)
        assert tier == SurvivalTier.CRITICAL

    def test_transition_to_dead(self, state_machine):
        tier = state_machine.update_balance(0.0)
        assert tier == SurvivalTier.DEAD
        assert not state_machine.is_alive()

    def test_transition_dead_to_normal(self, state_machine):
        state_machine.update_balance(0.0)
        assert state_machine.current_tier == SurvivalTier.DEAD
        tier = state_machine.update_balance(200.0)
        assert tier == SurvivalTier.NORMAL
        assert state_machine.is_alive()

    def test_negative_balance_is_dead(self, state_machine):
        tier = state_machine.update_balance(-5.0)
        assert tier == SurvivalTier.DEAD

    def test_callback_on_transition(self, state_machine):
        transitions = []
        state_machine.on_transition(lambda old, new: transitions.append((old, new)))
        state_machine.update_balance(0.0)
        assert len(transitions) == 1
        assert transitions[0] == (SurvivalTier.NORMAL, SurvivalTier.DEAD)

    def test_no_callback_when_no_transition(self, state_machine):
        state_machine.configure_thresholds(normal=10, low_compute=5, critical=1)
        state_machine.update_balance(200.0)  # Still NORMAL
        transitions = []
        state_machine.on_transition(lambda old, new: transitions.append((old, new)))
        state_machine.update_balance(150.0)  # Still NORMAL
        assert len(transitions) == 0

    def test_get_current_config(self, state_machine):
        config = state_machine.get_current_config()
        assert isinstance(config, TierConfig)
        assert config.tier == SurvivalTier.NORMAL

    def test_get_status_dict(self, state_machine):
        status = state_machine.get_status()
        assert "tier" in status
        assert "balance_usd" in status
        assert "is_alive" in status
        assert status["is_alive"] is True

    def test_multiple_callbacks(self, state_machine):
        calls = {"a": 0, "b": 0}
        state_machine.on_transition(lambda o, n: calls.__setitem__("a", calls["a"] + 1))
        state_machine.on_transition(lambda o, n: calls.__setitem__("b", calls["b"] + 1))
        state_machine.update_balance(0.0)
        assert calls["a"] == 1
        assert calls["b"] == 1


class TestBalanceMonitor:
    """Test BalanceMonitor integration with ledger and state machine."""

    @pytest.mark.asyncio
    async def test_check_updates_state(self, ledger, state_machine):
        from agent_core.survival.balance_monitor import BalanceMonitor
        monitor = BalanceMonitor(ledger, state_machine)

        # Seed some balance
        await ledger.record_income(50.0, category="seed", description="test seed")
        result = await monitor.check()

        assert result["balance_usd"] == 50.0
        assert monitor.balance == 50.0

    @pytest.mark.asyncio
    async def test_ttl_with_expenses(self, ledger, state_machine):
        from agent_core.survival.balance_monitor import BalanceMonitor
        monitor = BalanceMonitor(ledger, state_machine)

        await ledger.record_income(100.0, category="seed")
        await ledger.record_expense(10.0, category="llm", description="test")

        result = await monitor.check()
        assert result["balance_usd"] == 90.0
        assert result["burn_rate_per_hour"] >= 0
