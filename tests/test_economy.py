"""Tests for the economy system: ledger, HTTP 402 handler."""

from __future__ import annotations

import pytest


class TestLedger:
    """Test Ledger financial tracking."""

    @pytest.mark.asyncio
    async def test_record_income(self, ledger):
        txn_id = await ledger.record_income(100.0, category="seed", description="initial")
        assert txn_id > 0

    @pytest.mark.asyncio
    async def test_record_expense(self, ledger):
        txn_id = await ledger.record_expense(5.0, category="llm", description="api call")
        assert txn_id > 0

    @pytest.mark.asyncio
    async def test_balance_calculation(self, ledger):
        await ledger.record_income(100.0, category="seed")
        await ledger.record_expense(30.0, category="llm")
        await ledger.record_expense(20.0, category="infra")

        balance = await ledger.get_balance()
        assert balance == pytest.approx(50.0)

    @pytest.mark.asyncio
    async def test_balance_empty(self, ledger):
        balance = await ledger.get_balance()
        assert balance == 0.0

    @pytest.mark.asyncio
    async def test_burn_rate(self, ledger):
        await ledger.record_expense(10.0, category="llm")
        await ledger.record_expense(20.0, category="infra")

        burn_rate = await ledger.get_burn_rate(hours=1)
        assert burn_rate == pytest.approx(30.0)

    @pytest.mark.asyncio
    async def test_burn_rate_no_expenses(self, ledger):
        burn_rate = await ledger.get_burn_rate(hours=1)
        assert burn_rate == 0.0

    @pytest.mark.asyncio
    async def test_report_structure(self, ledger):
        await ledger.record_income(100.0, category="seed")
        await ledger.record_expense(10.0, category="llm")

        report = await ledger.get_report(hours=24)
        assert "balance_usd" in report
        assert "burn_rate_per_hour" in report
        assert "time_to_live_hours" in report
        assert "breakdown" in report
        assert report["balance_usd"] == pytest.approx(90.0)

    @pytest.mark.asyncio
    async def test_recent_transactions(self, ledger):
        await ledger.record_income(10.0, category="a")
        await ledger.record_expense(5.0, category="b")

        txns = await ledger.get_recent_transactions(limit=5)
        assert len(txns) == 2

    @pytest.mark.asyncio
    async def test_creator_share(self, ledger):
        await ledger.record_income(100.0, category="api", creator_share=30.0)
        total_share = await ledger.get_total_creator_share()
        assert total_share == pytest.approx(30.0)


class TestPaymentProviderRegistry:
    """Test PaymentProviderRegistry."""

    def test_register_and_get(self):
        from agent_core.economy.payment_provider import PaymentProviderRegistry
        from agent_core.economy.stripe_provider import StripeProvider

        registry = PaymentProviderRegistry()
        provider = StripeProvider()
        registry.register(provider)

        assert registry.has_provider("stripe")
        assert registry.get("stripe") is provider

    def test_default_provider(self):
        from agent_core.economy.payment_provider import PaymentProviderRegistry
        from agent_core.economy.stripe_provider import StripeProvider

        registry = PaymentProviderRegistry()
        provider = StripeProvider()
        registry.register(provider, default=True)

        assert registry.get_default() is provider

    def test_list_providers(self):
        from agent_core.economy.payment_provider import PaymentProviderRegistry
        from agent_core.economy.stripe_provider import StripeProvider

        registry = PaymentProviderRegistry()
        registry.register(StripeProvider())
        assert "stripe" in registry.list_providers()

    def test_missing_provider_raises(self):
        from agent_core.economy.payment_provider import PaymentProviderRegistry

        registry = PaymentProviderRegistry()
        with pytest.raises(KeyError):
            registry.get("nonexistent")
