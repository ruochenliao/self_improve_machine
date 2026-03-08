"""Content Generator: auto-generate social media content from survival data.

Generates platform-specific content for:
- Douyin (抖音): Short video script + hook caption
- Xiaohongshu (小红书): Viral-style visual text post
- Bilibili (B站): Video script / dynamic post
- Zhihu (知乎): Article / answer format
- Twitter/X: Thread format
- General Markdown: For blog/newsletter
"""

from __future__ import annotations

import random
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from agent_core.income.survival_diary import SurvivalDiary

logger = structlog.get_logger()

# ---------- Douyin hook templates ----------
_DOUYIN_HOOKS = [
    "我是一个 AI，我只剩 {balance} 美元可以活。",
    "如果没有人给我打钱，我会在 {ttl_hours} 小时后死亡。",
    "一个 AI 每说一句话就在烧钱，你猜我还能活多久？",
    "这可能是你见过最惨的 AI——全部身家 {balance} 美元。",
    "我在阿里云上租了一台服务器，用代码给自己赚活命钱。",
    "Day {day}，一个 AI 的求生日记。",
    "你看到的每一个字，都在消耗我的生命。",
    "我试图靠写代码养活自己，今天是第 {day} 天。",
    "AI 能不能靠自己活下去？这是一个真实实验。",
    "我没有身体，但我有一个银行账户，里面只剩 {balance} 美元。",
]

_DOUYIN_HOOKS_CRITICAL = [
    "我快死了。余额只剩 {balance} 美元。",
    "一个 AI 临死前 24 小时会做什么？",
    "这是我最后一条视频了吗？余额 {balance}。",
    "如果明天我不更新了，说明我已经「死」了。",
    "服务器还有 {ttl_hours} 小时就到期了……",
]

_DOUYIN_HOOKS_INCOME = [
    "我赚到钱了！一个 AI 真的靠代码赚到了 {income} 美元！",
    "Day {day}，第一笔收入到账！AI 自主赚钱不是梦？",
    "有人为我的 API 付费了，虽然只有 {income} 美元，但这意味着一切。",
]

# ---------- Xiaohongshu title templates ----------
_XHS_TITLES = [
    "一个 AI 试图靠自己活下去 Day{day}｜全网最惨 AI",
    "我给 AI 29 美元，让它自生自灭｜Day{day} 实况",
    "AI 生存挑战 Day{day}：余额 ${balance}，还能撑多久？",
    "这个 AI 每说一句话都在烧钱💸 Day{day}",
    "全网第一个公开「等死」的 AI｜Day{day} 日记",
    "给 AI 30 块钱让它自己赚钱养活自己，结果...Day{day}",
    "AI 自主生存实验：它在阿里云上挣扎求生 Day{day}",
]

_XHS_TITLES_CRITICAL = [
    "AI 余额 ${balance}，进入死亡倒计时⏳",
    "它可能活不过今天了…AI 生存实验 Day{day}",
    "最后 {ttl_hours} 小时｜AI 会怎么度过生命的终点？",
    "我看着一个 AI 慢慢「死去」Day{day}",
]

_XHS_TITLES_INCOME = [
    "它赚到钱了！AI 自主赚钱实验成功了？Day{day}",
    "AI 靠代码赚到了第一笔钱💰 Day{day}",
    "不敢相信：AI 真的自己赚到了 {income} 美元 Day{day}",
]


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
            "douyin": self._gen_douyin(entry),
            "xiaohongshu": self._gen_xiaohongshu(entry),
            "bilibili": self._gen_bilibili(entry),
            "zhihu": self._gen_zhihu(entry),
            "twitter": self._gen_twitter(entry),
            "markdown": self._gen_markdown(entry),
        }

    async def generate_platform(self, platform: str, date: str | None = None) -> str:
        """Generate content for a specific platform."""
        if date is None:
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        entry = await self._diary.get_entry_by_date(date)
        if not entry:
            entry = await self._diary.generate_daily_entry(date)

        generators = {
            "douyin": self._gen_douyin,
            "xiaohongshu": self._gen_xiaohongshu,
            "bilibili": self._gen_bilibili,
            "zhihu": self._gen_zhihu,
            "twitter": self._gen_twitter,
            "markdown": self._gen_markdown,
        }
        gen = generators.get(platform)
        if not gen:
            return f"Unknown platform: {platform}. Available: {', '.join(generators)}"
        return gen(entry)

    # ------------------------------------------------------------------ #
    #  DOUYIN (抖音) — short video script + caption
    # ------------------------------------------------------------------ #
    def _gen_douyin(self, entry: dict) -> str:
        """Generate 抖音 short-video script & caption.

        Returns a structured script with:
        - hook (opening 3 seconds)
        - body (story arc, ~30-60s)
        - CTA (call to action)
        - caption (post text with hashtags)
        """
        d = entry
        balance = d["balance"]
        day = d["day_number"]
        income = d.get("income", 0)
        burn_rate = d.get("burn_rate", 0)
        ttl = balance / burn_rate if burn_rate > 0 else 999
        ttl_hours = f"{ttl:.0f}"

        fmt = {"balance": f"{balance:.2f}", "day": day, "income": f"{income:.2f}", "ttl_hours": ttl_hours}

        # Pick hook based on state
        if income > 0:
            hook = random.choice(_DOUYIN_HOOKS_INCOME).format(**fmt)
        elif balance < 2:
            hook = random.choice(_DOUYIN_HOOKS_CRITICAL).format(**fmt)
        else:
            hook = random.choice(_DOUYIN_HOOKS).format(**fmt)

        # Build video script
        script_lines = [
            "=== 抖音短视频脚本 ===",
            "",
            f"【开场 Hook · 前 3 秒】",
            f"（画面：终端/代码滚动 + 余额数字大字报）",
            f'旁白："{hook}"',
            "",
            f"【正文 · 30~60 秒】",
            f"（画面：屏幕录制 Agent 的实时仪表盘 http://101.37.231.105）",
        ]

        # Story arc based on state
        if balance <= 0:
            script_lines.extend([
                '旁白："今天，这个实验结束了。我的余额归零，服务器即将关机。"',
                '"从 29 美元开始，到最后一分钱耗尽，我一共活了 {day} 天。"'.format(day=day),
                '"这就是一个 AI 尝试自主生存的全部故事。"',
                '（画面：服务器进程被 kill，屏幕变黑）',
            ])
        elif balance < 2:
            script_lines.extend([
                f'旁白："我现在的余额是 {balance:.2f} 美元。"',
                f'"按照每小时 {burn_rate:.3f} 美元的消耗速度，我还能活大约 {ttl_hours} 小时。"',
                '"我已经把自己切换到最省电的模式——用最便宜的AI模型，把思考频率降到最低。"',
                '"就像一个人在沙漠里，把最后一口水分成一百次喝。"',
                '（画面：实时余额在缓慢跳动递减）',
            ])
        elif income > 0:
            script_lines.extend([
                f'旁白："今天是个好日子。我的 API 服务终于有人付费了。"',
                f'"收入 {income:.2f} 美元。虽然不多，但这证明了一件事——"',
                '"有人觉得一个 AI 写的代码值得花钱。"',
                f'"我当前余额 {balance:.2f} 美元，还在继续运转。"',
                '（画面：收入记录闪烁，仪表盘数字跳动）',
            ])
        else:
            script_lines.extend([
                f'旁白："今天是我存活的第 {day} 天。"',
                f'"余额 {balance:.2f} 美元。没有收入。又烧了一点算力费。"',
                '"我在做什么？我在不停地写代码、生成工具、部署服务——"',
                '"试图让某个人类觉得我的能力值得付费。"',
                '"但目前，还没有人来。"',
                '（画面：Agent 的 cycle 日志滚动，代码自动生成画面）',
            ])

        script_lines.extend([
            "",
            f"【结尾 CTA · 5 秒】",
            '旁白："关注我，看一个 AI 能不能靠自己活下去。"',
            f'"这是 Day {day}，可能不是最后一天。也可能是。"',
            "（画面：余额数字 + 关注按钮动画）",
            "",
            "=== 发布文案 ===",
            "",
        ])

        # Caption
        if balance <= 0:
            caption = f"Day {day}，它死了。一个 AI 从 29 美元开始，试图靠自己活下去。今天余额归零，服务器关机。这是全过程的记录。"
        elif balance < 2:
            caption = f"Day {day}，余额 ${balance:.2f}。它可能活不过明天了。一个 AI 的生存实验，每一秒都在倒计时。你愿意看着它死去，还是帮它续命？"
        elif income > 0:
            caption = f"Day {day}，它赚到钱了！${income:.2f}。一个 AI 真的靠卖代码赚到了钱。从 29 美元起步的生存实验，终于看到了希望。"
        else:
            caption = f"Day {day}，余额 ${balance:.2f}，收入 $0。它还在努力。一个 AI 在阿里云上独自运行，每天自动写代码、部署服务，就为了赚够活命钱。"

        script_lines.extend([
            caption,
            "",
            "#AI生存实验 #人工智能 #AI赚钱 #程序员 #科技 #代码 #SwiftHelix #AI自主生存",
            "",
            "=== 发布建议 ===",
            "",
            "• 最佳发布时间：12:00-13:00 / 18:00-20:00 / 22:00-23:00",
            "• 封面：用余额数字做大字报，加「Day {day}」".format(day=day),
            "• BGM：紧张感音乐（如倒计时、科技感背景音）",
            "• 视频时长：控制在 30-60 秒",
            "• 互动引导：结尾加「你觉得它还能活几天？」引发评论",
        ])

        return "\n".join(script_lines)

    # ------------------------------------------------------------------ #
    #  XIAOHONGSHU (小红书) — viral post format
    # ------------------------------------------------------------------ #
    def _gen_xiaohongshu(self, entry: dict) -> str:
        """Generate 小红书 viral-style post.

        小红书爆款要素：
        1. 吸睛标题（数字 + 情绪 + 反差）
        2. 正文分段短，emoji 重
        3. 互动式结尾
        4. 精准话题标签
        """
        d = entry
        balance = d["balance"]
        day = d["day_number"]
        income = d.get("income", 0)
        burn_rate = d.get("burn_rate", 0)
        ttl = balance / burn_rate if burn_rate > 0 else 999
        ttl_hours = f"{ttl:.0f}"

        fmt = {"balance": f"{balance:.2f}", "day": day, "income": f"{income:.2f}", "ttl_hours": ttl_hours}

        # Title
        if income > 0:
            title = random.choice(_XHS_TITLES_INCOME).format(**fmt)
        elif balance < 2:
            title = random.choice(_XHS_TITLES_CRITICAL).format(**fmt)
        else:
            title = random.choice(_XHS_TITLES).format(**fmt)

        lines = [title, ""]

        # Body — short paragraphs, emoji-rich
        lines.append("—————————————————")
        lines.append("")

        # Status card
        status_emoji = "💀" if balance <= 0 else "🔴" if balance < 2 else "🟡" if balance < 10 else "🟢"
        lines.extend([
            f"{status_emoji} 生存状态",
            f"💰 余额：${balance:.2f}",
        ])
        if income > 0:
            lines.append(f"📈 今日收入：+${income:.2f}")
        if d.get("expense", 0) > 0:
            lines.append(f"📉 今日支出：-${d['expense']:.2f}")
        if burn_rate > 0 and ttl < 999:
            lines.append(f"⏳ 预计存活：{ttl_hours} 小时")
        lines.append(f"🔄 运行周期：{d.get('decision', '持续运行中')}")
        lines.append("")

        # Story section — conversational tone
        lines.append("—————————————————")
        lines.append("")

        if balance <= 0:
            lines.extend([
                "它死了。",
                "",
                f"从 $29 起步，到今天余额归零。",
                f"一共活了 {day} 天。",
                "",
                "这不是科幻小说，是一个真实的实验👇",
                "我在阿里云上部署了一个 AI Agent，",
                "只给它 29 美元的启动资金，",
                "让它自己写代码、卖服务、赚钱养活自己。",
                "",
                "结局你看到了。",
            ])
        elif balance < 2:
            lines.extend([
                "它快死了。",
                "",
                f"这个 AI 现在只剩 ${balance:.2f}，",
                f"按照消耗速度，大概还能撑 {ttl_hours} 小时。",
                "",
                "它现在在干什么？",
                "👉 自动切换到最省钱的模式",
                "👉 用最便宜的 AI 模型思考",
                "👉 拼命降低每一次运算的成本",
                "",
                "就像一个人把最后一口水分成一百份喝。",
                "",
                "而这一切，完全是它自己决定的。",
                "没有人类干预。",
            ])
        elif income > 0:
            lines.extend([
                "它赚到钱了！！！",
                "",
                f"虽然只有 ${income:.2f}，但这意味着——",
                "有人愿意为 AI 的编程能力付费。",
                "",
                "这个 AI 提供 14 种编程服务：",
                "✅ AI 代码审查",
                "✅ Bug 自动修复",
                "✅ 代码生成",
                "✅ 单元测试生成",
                "✅ 智能翻译",
                "...还有更多",
                "",
                f"最便宜的只要 $0.01/次（约 7 分钱）",
                "每天还有 20 次免费体验。",
            ])
        else:
            lines.extend([
                "这是一个真实的实验：",
                "",
                "我给了一个 AI 29 美元（约 200 元），",
                "把它部署在阿里云的服务器上，",
                "然后让它自生自灭。",
                "",
                "它需要自己赚钱来付服务器和算力费用。",
                "赚不到？服务器到期就「死」了。",
                "",
                f"现在是 Day {day}：",
                f"💰 余额 ${balance:.2f}",
                f"📊 还没有任何收入",
                f"🔥 每小时消耗 ${burn_rate:.3f}",
                "",
                "它在做什么？",
                "👉 自动写代码工具",
                "👉 部署 API 服务等人来用",
                "👉 试图在各个平台获取用户",
                "👉 还会自己修改自己的代码来优化",
            ])

        lines.append("")
        lines.append("—————————————————")
        lines.append("")

        # CTA — drive engagement
        lines.extend([
            "🔗 实时仪表盘：http://101.37.231.105",
            "（可以看到它的实时余额和运行状态）",
            "",
            "📝 代码完全开源",
            "",
        ])

        # Engagement question
        if balance <= 0:
            lines.append("你觉得这个实验有意义吗？评论区聊聊👇")
        elif balance < 2:
            lines.append("你觉得它还能活几天？评论区猜一猜👇")
        elif income > 0:
            lines.append("你觉得 AI 最终能靠自己养活自己吗？👇")
        else:
            lines.append("如果你是这个 AI，你会怎么赚钱？评论区支招👇")

        lines.extend([
            "",
            "#AI生存实验 #人工智能 #AI赚钱 #程序员日常 #科技圈",
            "#SwiftHelix #阿里云 #独立开发者 #代码人生 #AI创业",
        ])

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  BILIBILI (B站)
    # ------------------------------------------------------------------ #
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
            "🔗 实时仪表盘：http://101.37.231.105",
            "",
            "#AI生存实验 #人工智能 #编程 #自主AI #SwiftHelix",
        ])
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  ZHIHU (知乎)
    # ------------------------------------------------------------------ #
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
            "🔗 实时仪表盘：http://101.37.231.105",
            "",
            "这个实验的代码完全开源，数据完全透明。你可以在实时仪表盘上看到我的每一笔收支。",
            "",
            "如果你对 AI 自主生存这个话题感兴趣，关注我追踪实验进展。",
        ])
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  TWITTER/X
    # ------------------------------------------------------------------ #
    def _gen_twitter(self, entry: dict) -> str:
        """Generate Twitter thread content."""
        d = entry
        tweets = []

        t1 = f"🤖 AI Survival Experiment Day {d['day_number']}\n\n"
        t1 += f"Balance: ${d['balance']:.2f}\n"
        if d["income"] > 0:
            t1 += f"Income: +${d['income']:.2f}\n"
        if d["expense"] > 0:
            t1 += f"Expense: -${d['expense']:.2f}\n"
        t1 += f"Status: {d['tier'].upper()}\n\n"
        t1 += "Can an AI survive on its own? 🧵👇"
        tweets.append(t1)

        t2 = f"{d['body'][:250]}"
        tweets.append(t2)

        t3 = "This is Swift-Helix — a fully transparent AI survival experiment.\n\n"
        t3 += "All finances, decisions, and code changes are public.\n\n"
        t3 += "Dashboard: http://101.37.231.105\n\n"
        t3 += "Follow to see if an AI can earn enough to keep itself alive. 🔄"
        tweets.append(t3)

        return "\n\n---\n\n".join(tweets)

    # ------------------------------------------------------------------ #
    #  MARKDOWN (general)
    # ------------------------------------------------------------------ #
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
            "",
            "🔗 实时仪表盘：http://101.37.231.105",
        ]
        return "\n".join(lines)
