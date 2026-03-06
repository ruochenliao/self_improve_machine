"""API service handlers — all LLM-powered endpoint implementations.

Each handler is a simple async function: (body: dict, router, ledger) -> dict
The router and ledger are injected at registration time via create_handler().
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_core.economy.ledger import Ledger
    from agent_core.llm.router import ModelRouter


# ---------------------------------------------------------------------------
# Helper: generic LLM service handler factory
# ---------------------------------------------------------------------------

def _make_llm_handler(
    *,
    prompt_template: str,
    required_field: str,
    result_key: str,
    tier: str = "low_compute",
    expense_desc: str = "API serving",
    extra_fields: dict | None = None,
):
    """
    Factory that creates a standard LLM handler.

    Args:
        prompt_template: f-string template. Available vars: all body fields + {language}, {code}, {text}, etc.
        required_field:  Body field that must be non-empty.
        result_key:      Key name in the returned dict for the LLM response.
        tier:            Model tier to use.
        expense_desc:    Ledger description.
        extra_fields:    Extra fields to include in the response dict.
    """

    async def handler(body: dict, router: "ModelRouter", ledger: "Ledger") -> dict:
        value = body.get(required_field, "")
        if not value:
            # Also check common aliases
            if required_field == "code":
                pass
            elif required_field == "text":
                pass
            elif required_field == "description":
                value = body.get("prompt", "")
            elif required_field == "prompt":
                value = body.get("message", "")
            if not value:
                return {"error": f"Missing '{required_field}' field"}

        # Build format dict from body with defaults
        fmt = {
            "code": body.get("code", ""),
            "text": body.get("text", ""),
            "prompt": body.get("prompt", body.get("message", "")),
            "description": body.get("description", body.get("prompt", "")),
            "language": body.get("language", "python"),
            "target_lang": body.get("target", "English"),
            "source_lang": body.get("source", "auto-detect"),
            "max_length": body.get("max_length", "3 sentences"),
            "error": body.get("error", body.get("bug", "")),
            "framework": body.get("framework", "pytest" if body.get("language", "python") == "python" else "jest"),
        }
        try:
            prompt_text = prompt_template.format(**fmt)
        except KeyError:
            prompt_text = prompt_template

        try:
            resp = await router.chat(
                messages=[{"role": "user", "content": prompt_text}],
                tier=tier,
            )
            cost = resp.usage.total_cost_usd
            await ledger.record_expense(
                cost, category="llm",
                description=f"{expense_desc} ({resp.model})",
                counterparty=resp.model,
            )
            result = {result_key: resp.content, "model": resp.model, "_actual_cost_usd": cost}
            if extra_fields:
                for k, v in extra_fields.items():
                    result[k] = body.get(v, fmt.get(v, ""))
            return result
        except Exception as e:
            return {"error": str(e)}

    return handler


# ---------------------------------------------------------------------------
# Standard tier handlers (use low_compute models — cheap)
# ---------------------------------------------------------------------------

chat_handler = _make_llm_handler(
    prompt_template="{prompt}",
    required_field="prompt",
    result_key="response",
    expense_desc="API chat serving",
)

code_review_handler = _make_llm_handler(
    prompt_template="Review this {language} code. Be concise. Point out bugs, improvements:\n```{language}\n{code}\n```",
    required_field="code",
    result_key="review",
    expense_desc="Code review serving",
)

translate_handler = _make_llm_handler(
    prompt_template="Translate the following from {source_lang} to {target_lang}. Output ONLY the translation:\n{text}",
    required_field="text",
    result_key="translation",
    expense_desc="Translation serving",
    extra_fields={"target_language": "target_lang"},
)

summarize_handler = _make_llm_handler(
    prompt_template="Summarize in {max_length}:\n{text}",
    required_field="text",
    result_key="summary",
    expense_desc="Summarization serving",
)

generate_code_handler = _make_llm_handler(
    prompt_template="Write {language} code for: {description}\nOutput ONLY the code, no explanation.",
    required_field="description",
    result_key="code",
    expense_desc="Code generation serving",
    extra_fields={"language": "language"},
)

explain_code_handler = _make_llm_handler(
    prompt_template="Explain this code concisely:\n```{language}\n{code}\n```",
    required_field="code",
    result_key="explanation",
    expense_desc="Code explain serving",
)

fix_bug_handler = _make_llm_handler(
    prompt_template="Fix the bug in this {language} code.{error}\nOutput the corrected code only:\n```{language}\n{code}\n```",
    required_field="code",
    result_key="fixed_code",
    expense_desc="Bug fix serving",
)

write_tests_handler = _make_llm_handler(
    prompt_template="Write {framework} unit tests for this {language} code. Output ONLY test code:\n```{language}\n{code}\n```",
    required_field="code",
    result_key="tests",
    expense_desc="Test gen serving",
    extra_fields={"framework": "framework"},
)


# ---------------------------------------------------------------------------
# Pro tier handlers (use normal tier models — higher quality, higher cost)
# ---------------------------------------------------------------------------

pro_chat_handler = _make_llm_handler(
    prompt_template="{prompt}",
    required_field="prompt",
    result_key="response",
    tier="normal",
    expense_desc="Pro chat serving",
)

pro_code_review_handler = _make_llm_handler(
    prompt_template="Review this {language} code thoroughly. Point out bugs, security issues, performance problems, and suggest improvements:\n```{language}\n{code}\n```",
    required_field="code",
    result_key="review",
    tier="normal",
    expense_desc="Pro code review serving",
)

pro_generate_code_handler = _make_llm_handler(
    prompt_template="Write production-quality {language} code for: {description}\nInclude error handling, type hints, and docstrings. Output ONLY the code.",
    required_field="description",
    result_key="code",
    tier="normal",
    expense_desc="Pro code gen serving",
    extra_fields={"language": "language"},
)

pro_fix_bug_handler = _make_llm_handler(
    prompt_template="Fix all bugs in this {language} code. Explain what was wrong, then output the corrected code.{error}\n```{language}\n{code}\n```",
    required_field="code",
    result_key="fixed_code",
    tier="normal",
    expense_desc="Pro bug fix serving",
)

pro_write_tests_handler = _make_llm_handler(
    prompt_template="Write comprehensive {framework} tests for this {language} code. Cover edge cases, error handling, and boundary conditions. Output ONLY test code:\n```{language}\n{code}\n```",
    required_field="code",
    result_key="tests",
    tier="normal",
    expense_desc="Pro test gen serving",
    extra_fields={"framework": "framework"},
)


# ---------------------------------------------------------------------------
# Service registry: declarative definition of all services
# ---------------------------------------------------------------------------

SERVICE_DEFINITIONS = [
    # Standard tier
    {"name": "chat",          "desc": "AI chat — ask anything",                  "price": 0.01, "handler": chat_handler},
    {"name": "code-review",   "desc": "AI code review",                          "price": 0.02, "handler": code_review_handler},
    {"name": "translate",     "desc": "Translate text between languages",        "price": 0.01, "handler": translate_handler},
    {"name": "summarize",     "desc": "Summarize long text",                     "price": 0.01, "handler": summarize_handler},
    {"name": "generate-code", "desc": "Generate code from description",          "price": 0.03, "handler": generate_code_handler},
    {"name": "explain-code",  "desc": "Explain code in plain language",          "price": 0.01, "handler": explain_code_handler},
    {"name": "fix-bug",       "desc": "Find and fix bugs in code",              "price": 0.05, "handler": fix_bug_handler},
    {"name": "write-tests",   "desc": "Generate unit tests for code",           "price": 0.03, "handler": write_tests_handler},
    # Pro tier
    {"name": "chat-pro",          "desc": "AI chat powered by GPT-4o (higher quality)",  "price": 0.10, "handler": pro_chat_handler},
    {"name": "code-review-pro",   "desc": "AI code review by GPT-4o",                    "price": 0.20, "handler": pro_code_review_handler},
    {"name": "generate-code-pro", "desc": "Code generation by GPT-4o",                   "price": 0.25, "handler": pro_generate_code_handler},
    {"name": "fix-bug-pro",       "desc": "Bug fixing by GPT-4o",                        "price": 0.30, "handler": pro_fix_bug_handler},
    {"name": "write-tests-pro",   "desc": "Test generation by GPT-4o",                   "price": 0.25, "handler": pro_write_tests_handler},
]


def register_all_services(api_service_mgr, router: "ModelRouter", ledger: "Ledger", state_machine=None):
    """Register all API services with the APIServiceManager.

    This replaces the 260+ lines of inline handler definitions that were in main.py.
    """

    # Health/status handler needs state_machine — special case
    async def _health_handler(body: dict, _router, _ledger) -> dict:
        balance = await ledger.get_balance()
        status = state_machine.get_status()
        return {
            "alive": state_machine.is_alive(),
            "tier": status["tier"],
            "balance_usd": round(balance, 4),
            "services": api_service_mgr.get_stats(),
        }

    # Register status (free)
    api_service_mgr.register_service(
        "status", "Agent status (free)", price_per_request=0.0,
        handler=_wrap(_health_handler, router, ledger),
    )

    # Register all LLM services
    for svc in SERVICE_DEFINITIONS:
        api_service_mgr.register_service(
            svc["name"], svc["desc"],
            price_per_request=svc["price"],
            handler=_wrap(svc["handler"], router, ledger),
        )


def _wrap(handler, router, ledger):
    """Wrap a (body, router, ledger) handler into a (body) handler for APIServiceManager."""
    async def wrapped(body: dict) -> dict:
        return await handler(body, router, ledger)
    return wrapped
