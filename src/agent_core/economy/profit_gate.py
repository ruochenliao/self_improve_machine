"""Profit Gate — 利润门控：确保 Agent 先赚钱再花钱。

核心铁律：
1. 未确认收款 → 禁止付费模型调用
2. 余额低于硬止损 → 停止一切付费调用
3. 单次预估成本超限 → 拒绝
4. 毛利率低于阈值 → 拒绝或降级
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

import structlog

if TYPE_CHECKING:
    from agent_core.config import ProfitGateConfig
    from agent_core.economy.ledger import Ledger
    from agent_core.storage.database import Database

logger = structlog.get_logger()


class ProfitDecision(TypedDict):
    allowed: bool
    reason: str
    estimated_cost_usd: float
    estimated_revenue_usd: float
    estimated_margin_ratio: float


class ProfitGate:
    """订单驱动的利润门控执行器。

    在每次付费 API 调用前检查：
    - 余额是否高于止损线
    - 是否为已收款请求（paid）
    - 单次成本是否在预算内
    - 历史毛利率是否达标
    """

    def __init__(
        self,
        config: "ProfitGateConfig",
        ledger: "Ledger",
        db: "Database | None" = None,
    ) -> None:
        self._config = config
        self._ledger = ledger
        self._db = db

    async def check(
        self,
        *,
        is_paid: bool,
        price_per_request: float,
        estimated_cost: float | None = None,
    ) -> ProfitDecision:
        """判定本次请求是否允许执行付费模型调用。

        Args:
            is_paid: 该请求是否为已付款用户发起
            price_per_request: 该服务对用户的单次收费
            estimated_cost: 预估的模型调用成本 (若为 None 则使用 max_cost_per_request_usd)

        Returns:
            ProfitDecision: 包含是否放行及原因
        """
        cfg = self._config

        if not cfg.enabled:
            return ProfitDecision(
                allowed=True,
                reason="profit_gate_disabled",
                estimated_cost_usd=0.0,
                estimated_revenue_usd=price_per_request,
                estimated_margin_ratio=1.0,
            )

        est_cost = estimated_cost if estimated_cost is not None else cfg.max_cost_per_request_usd

        # 1) 硬止损：余额过低
        balance = await self._ledger.get_balance()
        if balance <= cfg.hard_stop_balance_usd:
            decision = ProfitDecision(
                allowed=False,
                reason=f"hard_stop: balance={balance:.4f} <= {cfg.hard_stop_balance_usd}",
                estimated_cost_usd=est_cost,
                estimated_revenue_usd=price_per_request,
                estimated_margin_ratio=0.0,
            )
            await self._log_decision(decision)
            return decision

        # 2) 余额低于最低运营线
        if balance <= cfg.min_balance_usd:
            decision = ProfitDecision(
                allowed=False,
                reason=f"low_balance: balance={balance:.4f} <= {cfg.min_balance_usd}",
                estimated_cost_usd=est_cost,
                estimated_revenue_usd=price_per_request,
                estimated_margin_ratio=0.0,
            )
            await self._log_decision(decision)
            return decision

        # 3) 未收款请求 + require_confirmed_payment
        if cfg.require_confirmed_payment and not is_paid:
            if cfg.block_free_trial_when_gated:
                decision = ProfitDecision(
                    allowed=False,
                    reason="unpaid_request_blocked: free trial gated",
                    estimated_cost_usd=est_cost,
                    estimated_revenue_usd=0.0,
                    estimated_margin_ratio=-1.0,
                )
                await self._log_decision(decision)
                return decision

        # 4) 单次成本超限
        if est_cost > cfg.max_cost_per_request_usd:
            decision = ProfitDecision(
                allowed=False,
                reason=f"cost_exceeded: est={est_cost:.4f} > max={cfg.max_cost_per_request_usd}",
                estimated_cost_usd=est_cost,
                estimated_revenue_usd=price_per_request,
                estimated_margin_ratio=0.0,
            )
            await self._log_decision(decision)
            return decision

        # 5) 毛利率检查（仅对已付款请求）
        if is_paid and price_per_request > 0:
            margin = (price_per_request - est_cost) / price_per_request
            if margin < cfg.min_gross_margin_ratio:
                decision = ProfitDecision(
                    allowed=False,
                    reason=f"margin_below_threshold: {margin:.2%} < {cfg.min_gross_margin_ratio:.2%}",
                    estimated_cost_usd=est_cost,
                    estimated_revenue_usd=price_per_request,
                    estimated_margin_ratio=margin,
                )
                await self._log_decision(decision)
                return decision
        else:
            margin = 0.0

        # 全部通过
        decision = ProfitDecision(
            allowed=True,
            reason="approved",
            estimated_cost_usd=est_cost,
            estimated_revenue_usd=price_per_request,
            estimated_margin_ratio=margin if is_paid else 0.0,
        )
        await self._log_decision(decision)
        return decision

    async def get_dashboard(self) -> dict:
        """返回飞轮看板数据。"""
        balance = await self._ledger.get_balance()
        report = await self._ledger.get_report(hours=24)

        total_income = sum(
            b["total"] for b in report["breakdown"] if b["type"] == "income"
        )
        total_expense = sum(
            b["total"] for b in report["breakdown"] if b["type"] == "expense"
        )
        gross_profit = total_income - total_expense
        margin = gross_profit / total_income if total_income > 0 else 0.0
        reinvest_budget = max(0.0, gross_profit * self._config.reinvest_ratio)

        # 实际审计统计（过去 24h）
        service_stats: list[dict] = []
        total_actual_revenue = 0.0
        total_actual_cost = 0.0
        if self._db is not None:
            try:
                rows = await self._db.fetchall(
                    """SELECT service,
                              COUNT(*) as requests,
                              SUM(revenue) as total_revenue,
                              SUM(cost) as total_cost,
                              AVG(margin) as avg_margin
                       FROM profit_audit
                       WHERE timestamp >= datetime('now', '-24 hours')
                       GROUP BY service
                       ORDER BY total_revenue DESC""",
                )
                for row in rows:
                    total_actual_revenue += float(row["total_revenue"])
                    total_actual_cost += float(row["total_cost"])
                    service_stats.append({
                        "service": row["service"],
                        "requests": int(row["requests"]),
                        "revenue": round(float(row["total_revenue"]), 4),
                        "cost": round(float(row["total_cost"]), 4),
                        "avg_margin": round(float(row["avg_margin"]), 4),
                    })
            except Exception:
                pass

        return {
            "balance_usd": round(balance, 4),
            "income_24h": round(total_income, 4),
            "expense_24h": round(total_expense, 4),
            "gross_profit_24h": round(gross_profit, 4),
            "gross_margin_24h": round(margin, 4),
            "reinvest_budget_usd": round(reinvest_budget, 4),
            "hard_stop_balance": self._config.hard_stop_balance_usd,
            "min_balance": self._config.min_balance_usd,
            "gate_enabled": self._config.enabled,
            "actual_revenue_24h": round(total_actual_revenue, 4),
            "actual_cost_24h": round(total_actual_cost, 4),
            "actual_margin_24h": round(
                (total_actual_revenue - total_actual_cost) / total_actual_revenue
                if total_actual_revenue > 0 else 0.0, 4
            ),
            "service_breakdown": service_stats,
        }

    async def record_actual(
        self,
        *,
        service: str,
        revenue: float,
        cost: float,
    ) -> None:
        """记录一笔已完成请求的实际收入/成本/毛利到审计表。"""
        margin = (revenue - cost) / revenue if revenue > 0 else 0.0
        logger.info(
            "profit_gate.actual",
            service=service,
            revenue=round(revenue, 6),
            cost=round(cost, 6),
            margin=f"{margin:.2%}",
        )
        if self._db is not None:
            try:
                await self._db.execute(
                    """INSERT INTO profit_audit
                       (service, revenue, cost, margin, balance)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        service,
                        revenue,
                        cost,
                        margin,
                        await self._ledger.get_balance(),
                    ),
                )
                await self._db.commit()
            except Exception:
                pass

    async def _log_decision(self, decision: ProfitDecision) -> None:
        """将门控决策写入审计日志和结构化日志。"""
        if decision["allowed"]:
            logger.info(
                "profit_gate.allowed",
                reason=decision["reason"],
                est_cost=decision["estimated_cost_usd"],
                est_revenue=decision["estimated_revenue_usd"],
            )
        else:
            logger.warning(
                "profit_gate.blocked",
                reason=decision["reason"],
                est_cost=decision["estimated_cost_usd"],
                est_revenue=decision["estimated_revenue_usd"],
            )

        # 持久化到审计表
        if self._db is not None:
            try:
                await self._db.execute(
                    """INSERT INTO profit_gate_log
                       (action, reason, estimated_cost, estimated_revenue, estimated_margin, balance)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        "allowed" if decision["allowed"] else "blocked",
                        decision["reason"],
                        decision["estimated_cost_usd"],
                        decision["estimated_revenue_usd"],
                        decision["estimated_margin_ratio"],
                        await self._ledger.get_balance(),
                    ),
                )
                await self._db.commit()
            except Exception:
                pass  # 审计写入失败不应阻断请求处理
