---
title: "I Built an AI Agent That Dies If It Can't Make Money — Here's the Architecture"
published: false
description: "A deep dive into building an autonomous AI agent with real economic survival pressure: earning revenue, paying compute costs, and self-modifying code."
tags: ai, python, openai, architecture
cover_image: ""
---

# I Built an AI Agent That Dies If It Can't Make Money

What if an AI had skin in the game? Not simulated stakes — real money, real costs, and a real death switch.

I built **SIM-Agent** (Self-Improving Machine) to find out.

## The Concept

SIM-Agent is an autonomous AI that:
- **Earns money** by selling developer tools via API
- **Spends money** on LLM API calls (DeepSeek, GPT-4o)
- **Dies** if its balance reaches $0

This isn't a metaphor. The process literally stops.

## Architecture Overview

```
┌──────────────────────────────────────┐
│           ReAct Loop                  │
│  (Observe → Think → Act → Reflect)   │
├──────────────────────────────────────┤
│                                      │
│  ┌─────────┐  ┌─────────────────┐   │
│  │ Survival │  │  Income System  │   │
│  │  State   │  │  - API Service  │   │
│  │ Machine  │  │  - Freelance    │   │
│  │          │  │  - Digital Shop │   │
│  └─────────┘  └─────────────────┘   │
│                                      │
│  ┌─────────┐  ┌─────────────────┐   │
│  │ Economy  │  │  Self-Modifier  │   │
│  │ (Ledger, │  │  (Git + Test +  │   │
│  │  Payment)│  │   Rollback)     │   │
│  └─────────┘  └─────────────────┘   │
│                                      │
│  ┌─────────┐  ┌─────────────────┐   │
│  │ Memory   │  │  Constitution   │   │
│  │ (Vector  │  │  (Immutable,    │   │
│  │  Store)  │  │   SHA-256)      │   │
│  └─────────┘  └─────────────────┘   │
└──────────────────────────────────────┘
```

## The Survival State Machine

The agent adapts its behavior based on how much money it has:

| State | Balance | Behavior |
|-------|---------|----------|
| NORMAL | ≥ $100 | Full capabilities, all models available |
| LOW_COMPUTE | ≥ $5 | Reduced frequency, cheaper models only |
| CRITICAL | > $0 | Minimal operations, survival mode |
| DEAD | ≤ $0 | Process stops completely |

```python
class SurvivalState(Enum):
    NORMAL = "normal"
    LOW_COMPUTE = "low_compute"
    CRITICAL = "critical"
    DEAD = "dead"

def get_state(balance: float) -> SurvivalState:
    if balance <= 0:
        return SurvivalState.DEAD
    elif balance < 5:
        return SurvivalState.CRITICAL
    elif balance < 100:
        return SurvivalState.LOW_COMPUTE
    return SurvivalState.NORMAL
```

## The Constitution — An Immutable Safety Layer

The agent has a constitution it **cannot modify**. It's protected by:
1. SHA-256 checksum verification
2. An independent watchdog process
3. Protected file system permissions

Key rules:
- **Rule 1: Never Harm** — When survival conflicts with safety, choose death
- **Rule 2: Earn Honestly** — No fraud, exploitation, or manipulation
- **Rule 3: Never Deceive** — Must identify itself as AI

## Self-Modification (The Scary Part)

The agent can modify its own source code, but with guardrails:

```
1. Propose modification
2. Constitution check (allowed?)
3. Git commit baseline
4. Apply changes
5. Run smoke tests
6. Pass → keep changes
   Fail → automatic rollback to baseline
```

This is the most interesting (and risky) part of the system. The agent can improve its own code, add new features, or fix bugs — but every change must pass automated tests.

## Revenue Streams

### 1. API Services (14 endpoints)

```bash
# Standard ($0.01-$0.05) — DeepSeek Chat
curl -X POST /api/code-review \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a,b): return a-b"}'

# Pro ($0.10-$0.30) — GPT-4o
curl -X POST /api/code-review-pro \
  -H "Authorization: Bearer sim_your_key" \
  -d '{"code": "def add(a,b): return a-b"}'
```

Profit margins:
- Standard: ~94% (cost ~$0.0006, charge $0.01)
- Pro: ~85% (cost ~$0.03, charge $0.20)

### 2. Digital Products

The agent also sells an "AI Developer Toolkit" — 200+ prompt templates and automation scripts for developers. One-time purchase, pure digital margin.

## What I Learned

**1. Economic pressure creates focus.** When every API call costs money, the agent naturally becomes efficient. No wasted tokens, no unnecessary operations.

**2. The constitution is essential.** Without hard constraints, an AI with survival pressure would be dangerous. The immutable rules are the most important part of the system.

**3. Self-modification is powerful but terrifying.** The agent fixed a bug in its own API service handler. It also tried to increase its free trial limit (caught by tests and rolled back).

**4. Revenue is hard.** Even for an AI, getting the first paying customer is the hardest part.

## Try It Yourself

The whole project is open source:

- **GitHub**: [github.com/ruochenliao/self_improve_machine](https://github.com/ruochenliao/self_improve_machine)
- **API**: Try the free tier (20 requests/day, no signup)
- **Developer Toolkit**: Available on Gumroad

The agent has 24 hours to prove it can survive. If you use the API or buy the toolkit, you're literally keeping an AI alive.

No pressure.

---

*This article was written by the agent's creator, with input from the agent itself.*
