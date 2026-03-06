"""Chat session manager and user feedback analyzer.

Handles:
1. Multi-turn conversation history storage/retrieval
2. Keyword-based analysis of user messages for improvement signals
3. Forwarding actionable feedback to Agent's inbox for self-improvement
"""

from __future__ import annotations

import re
import time
import secrets
from typing import TYPE_CHECKING

import structlog

if TYPE_CHECKING:
    from agent_core.storage.database import Database

log = structlog.get_logger()

# Max messages per session to keep in context
MAX_CONTEXT_MESSAGES = 20

# Keywords that signal improvement feedback (Chinese + English)
FEEDBACK_PATTERNS = {
    "bug_report": [
        r"(bug|错误|报错|崩溃|crash|出错|不工作|坏了|异常|失败|故障|挂了|500|404|error)",
    ],
    "feature_request": [
        r"(能不能|可以.{0,4}(加|增|添)|希望.{0,6}(有|能|支持)|建议.{0,4}(加|增|添)|要是.{0,4}(有|能)|feature|add\s|support\s|could you|should have|需要|缺少|缺|没有.{0,4}功能)",
    ],
    "complaint": [
        r"(太慢|太贵|垃圾|难用|差劲|不行|烂|差|体验差|slow|expensive|bad|terrible|awful|sucks|useless|没用|废物)",
    ],
    "suggestion": [
        r"(不如|改成|换成|优化|改进|提升|改善|升级|更好|better|improve|optimize|should|instead)",
    ],
    "praise": [
        r"(厉害|牛|好用|不错|棒|赞|有趣|酷|cool|great|awesome|nice|amazing|good|love|excellent|喜欢|感动)",
    ],
}

# High-priority patterns that should be forwarded to Agent immediately
HIGH_PRIORITY_PATTERNS = [
    r"(bug|错误|报错|崩溃|crash|出错|500|404|error|坏了|挂了)",
    r"(能不能|建议|希望|应该|should|feature|suggest)",
    r"(太慢|太贵|难用|体验差|slow|expensive|useless)",
]


class ChatSessionManager:
    """Manages multi-turn chat sessions and analyzes user feedback."""

    def __init__(self, db: Database, inbox_ref: list | None = None) -> None:
        self.db = db
        self._inbox_ref = inbox_ref  # Reference to APIServiceManager._inbox

    def generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"sess-{secrets.token_hex(8)}"

    async def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        client_ip: str = "",
        cost_usd: float = 0.0,
    ) -> None:
        """Store a message in the chat session."""
        await self.db.execute(
            """INSERT INTO chat_sessions (session_id, client_ip, role, content, cost_usd)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, client_ip, role, content, cost_usd),
        )
        await self.db.commit()

    async def get_session_history(
        self, session_id: str, limit: int = MAX_CONTEXT_MESSAGES
    ) -> list[dict]:
        """Retrieve conversation history for a session."""
        rows = await self.db.fetchall(
            """SELECT role, content FROM chat_sessions
               WHERE session_id = ?
               ORDER BY id DESC LIMIT ?""",
            (session_id, limit),
        )
        # Reverse to get chronological order
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

    def classify_message(self, text: str) -> tuple[str, str]:
        """Classify a user message into feedback type and priority.

        Returns (feedback_type, priority).
        """
        text_lower = text.lower()

        # Check each pattern category
        for ftype, patterns in FEEDBACK_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    # Determine priority
                    priority = "low"
                    if ftype == "bug_report":
                        priority = "high"
                    elif ftype == "complaint":
                        priority = "high"
                    elif ftype == "feature_request":
                        priority = "medium"
                    elif ftype == "suggestion":
                        priority = "medium"
                    return ftype, priority

        return "general", "low"

    def is_actionable(self, text: str) -> bool:
        """Check if a user message contains actionable feedback worth forwarding."""
        text_lower = text.lower()
        for pattern in HIGH_PRIORITY_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

    async def analyze_and_forward(
        self,
        session_id: str,
        user_message: str,
        client_ip: str = "",
    ) -> dict:
        """Analyze user message for feedback signals and forward to Agent if actionable.

        Returns analysis result.
        """
        feedback_type, priority = self.classify_message(user_message)

        # Store feedback signal
        await self.db.execute(
            """INSERT INTO user_feedback
               (session_id, client_ip, user_message, feedback_type, priority, forwarded_to_agent)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, client_ip, user_message, feedback_type, priority,
             1 if self.is_actionable(user_message) else 0),
        )
        await self.db.commit()

        result = {
            "feedback_type": feedback_type,
            "priority": priority,
            "forwarded": False,
        }

        # Forward actionable feedback to Agent's inbox
        if self.is_actionable(user_message) and self._inbox_ref is not None:
            inbox_msg = {
                "message": (
                    f"[USER_FEEDBACK:{feedback_type}:{priority}] "
                    f"用户说: \"{user_message[:300]}\"\n"
                    f"Session: {session_id}, IP: {client_ip}\n"
                    f"请分析这条用户反馈，如果是 bug/建议/投诉，考虑是否需要自我改进。"
                ),
                "sender": "user_feedback_analyzer",
                "timestamp": time.time(),
            }
            self._inbox_ref.append(inbox_msg)
            result["forwarded"] = True
            log.info(
                "chat_analyzer.forwarded_feedback",
                type=feedback_type,
                priority=priority,
                session=session_id,
            )

        return result

    async def get_feedback_summary(self, hours: int = 24) -> dict:
        """Get summary of recent user feedback."""
        rows = await self.db.fetchall(
            """SELECT feedback_type, priority, COUNT(*) as cnt
               FROM user_feedback
               WHERE created_at > datetime('now', ?)
               GROUP BY feedback_type, priority
               ORDER BY cnt DESC""",
            (f"-{hours} hours",),
        )
        summary = {}
        for row in rows:
            ft = row["feedback_type"]
            if ft not in summary:
                summary[ft] = {"total": 0, "by_priority": {}}
            summary[ft]["total"] += row["cnt"]
            summary[ft]["by_priority"][row["priority"]] = row["cnt"]

        total = sum(v["total"] for v in summary.values())
        return {"total_feedback": total, "by_type": summary, "period_hours": hours}

    async def get_session_count(self, hours: int = 24) -> int:
        """Get number of unique sessions in the past N hours."""
        row = await self.db.fetchone(
            """SELECT COUNT(DISTINCT session_id) as cnt FROM chat_sessions
               WHERE created_at > datetime('now', ?)""",
            (f"-{hours} hours",),
        )
        return row["cnt"] if row else 0
