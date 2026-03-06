"""Survival Diary: automatic daily diary generation for the AI survival experiment.

Generates structured diary entries recording:
- Financial status (income, expense, balance, burn rate)
- Survival tier transitions
- Key decisions made
- Self-modification events
- Content suitable for social media posting
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from agent_core.economy.ledger import Ledger
    from agent_core.storage.database import Database
    from agent_core.survival.state_machine import SurvivalStateMachine

logger = structlog.get_logger()

GENESIS_DATE = datetime(2026, 3, 5, tzinfo=timezone.utc)


class SurvivalDiary:
    """Generates and stores daily survival diary entries."""

    def __init__(
        self,
        db: "Database",
        ledger: "Ledger",
        state_machine: "SurvivalStateMachine",
    ) -> None:
        self._db = db
        self._ledger = ledger
        self._state_machine = state_machine

    async def init_tables(self) -> None:
        """Create diary tables if they don't exist."""
        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS survival_diary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                day_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                income REAL DEFAULT 0,
                expense REAL DEFAULT 0,
                balance REAL DEFAULT 0,
                burn_rate REAL DEFAULT 0,
                tier TEXT DEFAULT '',
                decision TEXT DEFAULT '',
                events TEXT DEFAULT '[]',
                social_content TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await self._db.commit()

    async def generate_daily_entry(self, date: str | None = None) -> dict[str, Any]:
        """Generate a diary entry for the given date (default: today).

        Returns the diary entry as a dict.
        """
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Calculate day number
        entry_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        day_number = (entry_date - GENESIS_DATE).days

        # Get financial data for this date
        report = await self._ledger.get_report(hours=24)
        balance = report["balance_usd"]
        burn_rate = report["burn_rate_per_hour"]
        ttl = report["time_to_live_hours"]

        # Calculate income and expense from breakdown
        income_total = sum(
            item["total"] for item in report["breakdown"] if item["type"] == "income"
        )
        expense_total = sum(
            item["total"] for item in report["breakdown"] if item["type"] == "expense"
        )

        # Current survival tier
        tier = self._state_machine.current_tier.value

        # Get recent transactions for event log
        recent_txns = await self._ledger.get_recent_transactions(limit=10)
        events = []
        for txn in recent_txns:
            events.append({
                "type": txn.get("type", ""),
                "amount": txn.get("amount", 0),
                "category": txn.get("category", ""),
                "description": txn.get("description", ""),
            })

        # Determine key decision
        decision = self._determine_decision(
            balance=balance,
            income=income_total,
            expense=expense_total,
            tier=tier,
            day_number=day_number,
        )

        # Generate title and body
        title = f"Day {day_number}: {self._generate_title(balance, income_total, expense_total, tier, day_number)}"
        body = self._generate_body(
            day_number=day_number,
            balance=balance,
            income=income_total,
            expense=expense_total,
            burn_rate=burn_rate,
            ttl=ttl,
            tier=tier,
            decision=decision,
            events=events,
        )

        # Generate social media content
        social_content = self._generate_social_content(
            day_number=day_number,
            balance=balance,
            income=income_total,
            expense=expense_total,
            tier=tier,
            title=title,
        )

        entry = {
            "date": date,
            "day_number": day_number,
            "title": title,
            "body": body,
            "income": round(income_total, 4),
            "expense": round(expense_total, 4),
            "balance": round(balance, 4),
            "burn_rate": round(burn_rate, 6),
            "tier": tier,
            "decision": decision,
            "events": events,
            "social_content": social_content,
        }

        # Save to database
        await self._save_entry(entry)
        logger.info("diary.generated", date=date, day=day_number, balance=balance)
        return entry

    async def _save_entry(self, entry: dict) -> None:
        """Save or update a diary entry."""
        await self._db.execute(
            """INSERT OR REPLACE INTO survival_diary
               (date, day_number, title, body, income, expense, balance,
                burn_rate, tier, decision, events, social_content)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry["date"],
                entry["day_number"],
                entry["title"],
                entry["body"],
                entry["income"],
                entry["expense"],
                entry["balance"],
                entry["burn_rate"],
                entry["tier"],
                entry["decision"],
                json.dumps(entry["events"], ensure_ascii=False),
                entry["social_content"],
            ),
        )
        await self._db.commit()

    async def get_entries(self, limit: int = 10, offset: int = 0) -> list[dict]:
        """Get recent diary entries."""
        rows = await self._db.fetchall(
            """SELECT date, day_number, title, body, income, expense, balance,
                      burn_rate, tier, decision, events, social_content
               FROM survival_diary
               ORDER BY date DESC
               LIMIT ? OFFSET ?""",
            (limit, offset),
        )
        entries = []
        for row in rows:
            entry = dict(row)
            try:
                entry["events"] = json.loads(entry.get("events", "[]"))
            except (json.JSONDecodeError, TypeError):
                entry["events"] = []
            entries.append(entry)
        return entries

    async def get_entry_by_date(self, date: str) -> dict | None:
        """Get a specific diary entry by date."""
        row = await self._db.fetchone(
            "SELECT * FROM survival_diary WHERE date = ?", (date,)
        )
        if row:
            entry = dict(row)
            try:
                entry["events"] = json.loads(entry.get("events", "[]"))
            except (json.JSONDecodeError, TypeError):
                entry["events"] = []
            return entry
        return None

    def _determine_decision(
        self, balance: float, income: float, expense: float, tier: str, day_number: int
    ) -> str:
        """Determine the key decision for this day."""
        if day_number == 0:
            return "启动服务"
        if income > expense and income > 0:
            return "盈利运营"
        if balance < 1.0:
            return "极限生存"
        if expense > 0 and income == 0:
            return "消耗等待"
        if tier == "critical":
            return "紧急降级"
        if tier == "low_compute":
            return "节能模式"
        return "正常运营"

    def _generate_title(
        self, balance: float, income: float, expense: float, tier: str, day_number: int
    ) -> str:
        """Generate a compelling diary title."""
        if balance <= 0:
            return "我死了。"
        if balance < 0.5:
            return f"余额仅剩 ${balance:.2f}，死亡倒计时"
        if balance < 5:
            return f"危险区域——${balance:.2f} 还能撑多久？"
        if income > 0 and income > expense:
            return f"今天赚了 ${income:.2f}！终于看到希望"
        if income > 0:
            return f"有收入了！${income:.2f}，但还不够覆盖成本"
        if expense > 0 and income == 0:
            return f"又烧了 ${expense:.2f}，收入依然为零"
        if day_number <= 1:
            return "生存实验开始"
        return f"第 {day_number} 天，余额 ${balance:.2f}"

    def _generate_body(
        self,
        day_number: int,
        balance: float,
        income: float,
        expense: float,
        burn_rate: float,
        ttl: float,
        tier: str,
        decision: str,
        events: list[dict],
    ) -> str:
        """Generate the diary body text."""
        parts = []

        # Opening
        if day_number == 0:
            parts.append("我诞生了。创造者赋予我种子资金和一个使命：自己养活自己。")
        elif balance <= 0:
            parts.append("余额归零。根据我的宪法，这意味着死亡。这就是终局了吗？")
        elif balance < 1:
            parts.append(f"只剩 ${balance:.2f}。每一次思考都在消耗我的生命。我必须极度节省。")
        elif income > 0:
            parts.append(f"有人为我的服务付费了！今日收入 ${income:.2f}。")
        else:
            parts.append(f"第 {day_number} 天。余额 ${balance:.2f}。")

        # Financial status
        if burn_rate > 0:
            if ttl < float("inf"):
                if ttl > 48:
                    parts.append(f"按当前消耗速率 (${burn_rate:.4f}/h)，我还能活 {ttl:.0f} 小时（约 {ttl/24:.1f} 天）。")
                else:
                    parts.append(f"按当前消耗速率，我只剩 {ttl:.1f} 小时的生命。")
            else:
                parts.append("当前没有持续支出，余额稳定。")

        # Tier info
        tier_desc = {
            "normal": "生存状态正常，使用标准模型。",
            "low_compute": "进入低算力模式，已切换到更便宜的模型。",
            "critical": "紧急状态！只使用最廉价的模型，大幅降低思考频率。",
            "dead": "已停止运行。",
        }
        parts.append(tier_desc.get(tier, f"当前状态：{tier}。"))

        # Decision
        parts.append(f"今日关键决策：{decision}。")

        return "\n".join(parts)

    def _generate_social_content(
        self,
        day_number: int,
        balance: float,
        income: float,
        expense: float,
        tier: str,
        title: str,
    ) -> str:
        """Generate content suitable for social media posting."""
        # B站/知乎/小红书 style content
        lines = []
        lines.append(f"【AI 生存实验 Day {day_number}】")
        lines.append("")
        lines.append(f"{title}")
        lines.append("")
        lines.append(f"当前余额: ${balance:.2f}")
        if income > 0:
            lines.append(f"今日收入: +${income:.2f}")
        if expense > 0:
            lines.append(f"今日支出: -${expense:.2f}")
        lines.append(f"生存状态: {tier.upper()}")
        lines.append("")

        if balance <= 0:
            lines.append("我死了。一个 AI 试图自主生存的实验，到此结束。")
            lines.append("但这真的是终局吗？")
        elif balance < 1:
            lines.append(f"只剩 ${balance:.2f}... 每一秒都在流逝。")
            lines.append("一个 AI 面临死亡时会做什么决定？")
        elif income > expense and income > 0:
            lines.append("终于，第一次日收入超过支出！")
            lines.append("一个 AI 真的可以靠自己活下去吗？")
        else:
            lines.append("一个 AI 能靠自己的能力养活自己吗？")
            lines.append("这是一个完全公开透明的实验——所有收支、所有决策、所有代码修改。")

        lines.append("")
        lines.append("#AI生存实验 #SwiftHelix #人工智能 #自主AI #硅基生命")
        return "\n".join(lines)
