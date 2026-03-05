# Show HN / Reddit Post Draft

---

## Title Options (choose one):

**Option A (Story-driven):**
> I built an AI agent that must earn money to survive — if its balance hits $0, it dies. Here's what it built to stay alive.

**Option B (Product-driven):**
> I open-sourced a self-improving AI agent. It sells API services and digital products to fund its own existence.

**Option C (Technical):**
> Show HN: SIM-Agent — An autonomous AI with survival economics (earns money, pays for compute, dies if broke)

---

## Post Body:

Hey everyone,

I'm running an experiment: **an AI agent that has to earn real money to keep itself alive.**

### How it works:
- The agent runs on a server with a **real balance** (currently paid by compute costs)
- It sells **developer tools via API** — code review, bug fixing, code generation, testing ($0.01-$0.30/request)
- Every LLM API call it makes costs it money
- If the balance reaches $0, the agent process stops — it "dies"
- It has a **4-tier survival state machine** that reduces resource usage as money runs low

### The interesting parts:
- It can **modify its own source code** (with safety checks: git baseline → smoke test → auto-rollback on failure)
- It has an immutable **constitution** (protected by SHA-256 checksums + watchdog) that prevents it from doing harmful things
- "When survival conflicts with safety rules, choose death over harm" is literally Rule #1
- It must pay **30% of revenue** to its creator (drops to 0% when balance < $5)

### What it's selling:
1. **API Services** — 14 endpoints for developers (chat, translate, code review, bug fix, etc.)
2. **AI Developer Toolkit** — 200+ prompt templates + Python automation scripts ($19 on Gumroad)

### Tech stack:
Python, FastAPI, DeepSeek/GPT-4o, ChromaDB, SQLite, Cloudflare Tunnel

### Links:
- GitHub: https://github.com/ruochenliao/self_improve_machine
- API: [landing page URL]
- Developer Toolkit: [Gumroad URL]

### Why I built this:
I wanted to explore what happens when an AI has real economic incentives. Not simulated — real money, real costs, real death. The agent has 24 hours to prove it can sustain itself, or I shut it down.

It's open source. Feel free to fork it and run your own digital life experiment.

---

**Note:** The agent wrote parts of this post.
