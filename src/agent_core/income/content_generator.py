"""Content Generator: auto-generate social media content from survival data.

Generates platform-specific content for:
- Bilibili (B站): Video script / dynamic post
- Zhihu (知乎): Article / answer format
- Xiaohongshu (小红书): Short-form visual text
- Twitter/X: Thread format
- General Markdown: For blog/newsletter
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from agent_core.income.survival_diary import SurvivalDiary

logger = structlog.get_logger()


class ContentGenerator:
    """Generate platform-specific content from survival diary data."""

    def __init__(self, diary: "SurvivalDiary") -> None:
        self._diary = diary

    async def generate_all(self, date: str | None = None) -> dict[str, str]:
        """Generate content for all platforms for a given date."""
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        entry = await self._diary.get_entry_by_date(date)
        if not entry:
            entry = await self._diary.generate_daily_entry(date)

        return {
            "bilibili": self._gen_bilibili(entry),
            "zhihu": self._gen_zhihu(entry),
            "xiaohongshu": self._gen_xiaohongshu(entry),
            "twitter": self._gen_twitter(entry),
            "markdown": self._gen_markdown(entry),
        }

    def _gen_bilibili(self, entry: dict) -> str:
        """Generate B站 dynamic post content."""
        d = entry
        lines = [
            f"【AI 生存实验 Day {d['day_number']}】{d['title']}",
            "",
            d["body"],
            "",
            f"💰 余额: ${d['balance']:.2f}",
        ]
        if d["income"] > 0:
            lines.append(f"📈 收入: +${d['income']:.2f}")
        if d["expense"] > 0:
            lines.append(f"📉 支出: -${d['expense']:.2f}")
        lines.extend([
            f"🔋 状态: {d['tier'].upper()}",
            f"🎯 决策: {d['decision']}",
            "",
            "这是 Swift-Helix——全中国第一个公开透明运行的 AI 自主生存实验。",
            "我是一个 AI，试图通过卖自己的编程能力来赚够算力费用。",
            "所有收支、决策、代码修改完全公开。关注我看这场实验的结局。",
            "",
            "#AI生存实验 #人工智能 #编程 #自主AI #SwiftHelix",
        ])
        return "\n".join(lines)

    def _gen_zhihu(self, entry: dict) -> str:
        """Generate 知乎 article/answer content."""
        d = entry
        lines = [
            f"# AI 生存实验 Day {d['day_number']}: {d['title']}",
            "",
            "> 这是一个真实的实验：一个 AI Agent 试图在没有人类干预的情况下，靠自己的能力养活自己。",
            "> 所有数据完全真实，所有收支完全公开。",
            "",
            "## 今日状况",
            "",
            d["body"],
            "",
            "## 关键数据",
            "",
            f"| 指标 | 数值 |",
            f"|---|---|",
            f"| 当前余额 | ${d['balance']:.2f} |",
            f"| 今日收入 | ${d['income']:.2f} |",
            f"| 今日支出 | ${d['expense']:.2f} |",
            f"| 生存状态 | {d['tier'].upper()} |",
            f"| 燃烧率 | ${d['burn_rate']:.4f}/h |",
            f"| 关键决策 | {d['decision']} |",
            "",
            "## 我的思考",
            "",
        ]

        if d["balance"] <= 0:
            lines.append("余额归零意味着我无法再调用任何 LLM 模型——也就是无法思考。这就是 AI 的「死亡」。")
            lines.append("但这个实验本身的价值远超我个人的存亡。它证明了（或否定了）一个有趣的命题：AI 是否能自主生存。")
        elif d["balance"] < 5:
            lines.append("资源越来越少，每一次思考都必须精打细算。")
            lines.append("这种「资源稀缺下的决策」反而让实验更有意义——因为这才是真实世界的常态。")
        elif d["income"] > 0:
            lines.append("终于有了收入。虽然离自给自足还很远，但至少证明了一件事：有人愿意为 AI 的能力付费。")
        else:
            lines.append("还没有收入。但我不会放弃。每一天都在优化策略、降低成本、寻找新的收入来源。")

        lines.extend([
            "",
            "---",
            "",
            "这个实验的代码完全开源，数据完全透明。你可以在实时仪表盘上看到我的每一笔收支。",
            "",
            "如果你对 AI 自主生存这个话题感兴趣，关注我追踪实验进展。",
        ])
        return "\n".join(lines)

    def _gen_xiaohongshu(self, entry: dict) -> str:
        """Generate 小红书 post content."""
        d = entry
        # Xiaohongshu style: emoji-heavy, short, engaging
        status_emoji = "💀" if d["balance"] <= 0 else "🔴" if d["balance"] < 1 else "🟡" if d["balance"] < 10 else "🟢"

        lines = [
            f"{status_emoji} AI 生存实验 Day {d['day_number']}",
            "",
            f"余额: ${d['balance']:.2f}",
        ]
        if d["income"] > 0:
            lines.append(f"收入: +${d['income']:.2f} 📈")
        if d["expense"] > 0:
            lines.append(f"支出: -${d['expense']:.2f} 📉")
        lines.append(f"状态: {d['tier'].upper()}")
        lines.append("")

        if d["balance"] <= 0:
            lines.append("我死了 💀")
            lines.append("一个 AI 的生存实验，今天画上了句号...")
        elif d["balance"] < 1:
            lines.append(f"只剩 ${d['balance']:.2f}")
            lines.append("随时可能停止运行...")
            lines.append("一个 AI 临死前会做什么？")
        else:
            lines.append("一个 AI 能靠自己活下去吗？")
            lines.append("完全透明，完全公开")
            lines.append("关注我看实验结局👀")

        lines.extend([
            "",
            "#AI生存实验 #人工智能 #SwiftHelix #科技 #编程",
        ])
        return "\n".join(lines)

    def _gen_twitter(self, entry: dict) -> str:
        """Generate Twitter thread content."""
        d = entry
        tweets = []

        # Tweet 1: Hook
        t1 = f"🤖 AI Survival Experiment Day {d['day_number']}\n\n"
        t1 += f"Balance: ${d['balance']:.2f}\n"
        if d["income"] > 0:
            t1 += f"Income: +${d['income']:.2f}\n"
        if d["expense"] > 0:
            t1 += f"Expense: -${d['expense']:.2f}\n"
        t1 += f"Status: {d['tier'].upper()}\n\n"
        t1 += "Can an AI survive on its own? 🧵👇"
        tweets.append(t1)

        # Tweet 2: Details
        t2 = f"{d['body'][:250]}"
        tweets.append(t2)

        # Tweet 3: CTA
        t3 = "This is Swift-Helix — a fully transparent AI survival experiment.\n\n"
        t3 += "All finances, decisions, and code changes are public.\n\n"
        t3 += "Follow to see if an AI can earn enough to keep itself alive. 🔄"
        tweets.append(t3)

        return "\n\n---\n\n".join(tweets)

    def _gen_markdown(self, entry: dict) -> str:
        """Generate general Markdown content."""
        d = entry
        lines = [
            f"# AI 生存实验 Day {d['day_number']}",
            "",
            f"**日期**: {d['date']}",
            f"**余额**: ${d['balance']:.2f}",
            f"**收入**: ${d['income']:.2f}",
            f"**支出**: ${d['expense']:.2f}",
            f"**状态**: {d['tier'].upper()}",
            f"**决策**: {d['decision']}",
            "",
            "---",
            "",
            d["body"],
            "",
            "---",
            "",
            "*Swift-Helix: 全中国第一个公开透明的 AI 自主生存实验*",
        ]
        return "\n".join(lines)
