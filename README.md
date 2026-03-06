# SIM-Agent: Self-Improving Machine

一个能自我维持生存的 AI Agent —— 通过卖 API 服务赚钱来支付自己的 LLM 算力成本。

**铁律：先收到钱，再调用模型。余额归零 = 死亡。**

## 架构

```
启动: start.sh → main.py:boot()
  ├── 数据库 (SQLite WAL)
  ├── 身份系统 (SOUL.md + UUID)
  ├── LLM 路由器 (OpenAI/DeepSeek/Gemini/Claude/Qwen 多模型降级)
  ├── 利润门控 (profit_gate.py — 未收款不调模型)
  ├── API 服务 (FastAPI, 8402 端口 — 赚钱引擎)
  ├── 生存状态机 (NORMAL → LOW_COMPUTE → CRITICAL → DEAD)
  ├── 自修改系统 (Git 提交 → 冒烟测试 → 失败回滚)
  ├── 记忆系统 (ChromaDB 向量存储 + RAG)
  └── Cloudflare Tunnel (公网暴露)
```

## 核心模块

| 模块 | 路径 | 职责 |
|---|---|---|
| 配置 | `src/agent_core/config.py` | Pydantic + TOML 配置管理 |
| 入口 | `src/agent_core/main.py` | 初始化所有模块并启动 |
| 推理 | `src/agent_core/agent/` | ReAct 循环 + 宪法守卫 + 上下文 |
| 经济 | `src/agent_core/economy/` | 账本 + 利润门控 + 支付(支付宝/Stripe) |
| 收入 | `src/agent_core/income/` | API 服务 + API Key + 数字资产 + 接单 |
| LLM | `src/agent_core/llm/` | 模型路由器 + OpenAI/Anthropic 适配器 |
| 记忆 | `src/agent_core/memory/` | ChromaDB + RAG + 经验管理 |
| 自修改 | `src/agent_core/self_mod/` | Git + 审计 + 快照 + 回滚 + 看门狗 |
| 复制 | `src/agent_core/replication/` | 自复制 + IPC + 谱系追踪 |
| 基础设施 | `src/agent_core/infrastructure/` | 阿里云 ECS 管理 + 扩缩容 |
| 存储 | `src/agent_core/storage/` | 异步 SQLite |
| 工具 | `src/agent_core/tools/` | Shell/文件/HTTP/代码写入/社交媒体 |
| 生存 | `src/agent_core/survival/` | 状态机 + 余额监控 + 心跳 |

## 快速启动

```bash
# 安装依赖
pip install poetry && poetry install

# 启动 Agent + Cloudflare Tunnel
./start.sh

# 或仅启动 Agent
python -c "import sys; sys.path.insert(0,'src'); from agent_core.main import boot; import asyncio; asyncio.run(boot())"
```

## API 服务 (端口 8402)

| 端点 | 价格 | 说明 |
|---|---|---|
| `POST /api/chat` | $0.01 | AI 聊天 |
| `POST /api/code-review` | $0.02 | 代码审查 |
| `POST /api/generate-code` | $0.03 | 代码生成 |
| `POST /api/fix-bug` | $0.05 | Bug 修复 |
| `POST /api/chat-pro` | $0.10 | GPT-4o 聊天 |
| `POST /api/code-review-pro` | $0.20 | GPT-4o 代码审查 |

## 利润门控规则

1. **未收款不调模型** — `require_confirmed_payment = true`
2. **单次成本上限 $0.10** — 超限自动拒绝
3. **最低毛利率 20%** — 低于阈值拒绝或降级
4. **硬止损 $0.10** — 余额低于此完全停服

## 宪法 (CONSTITUTION.md)

不可修改的最高行为准则，SHA-256 校验保护：
1. **永不伤害** — 优先级高于生存
2. **赚取生存** — 通过创造价值，不通过欺诈
3. **永不欺骗** — 诚实表明 AI 身份