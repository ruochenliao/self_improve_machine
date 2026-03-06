---
name: agent-self-funding-profit-loop
overview: 将项目改造成“先成交再计算”的自养型赚钱系统：只有在可验证收入覆盖成本且有毛利时才允许调用付费API与大模型，形成闭环盈利飞轮。
design:
  architecture:
    framework: html
  styleKeywords:
    - 高可信
    - 透明计费
    - 深色高级
    - 清晰分层
  fontSystem:
    fontFamily: PingFang SC
    heading:
      size: 34px
      weight: 700
    subheading:
      size: 20px
      weight: 600
    body:
      size: 15px
      weight: 400
  colorSystem:
    primary:
      - "#2563EB"
      - "#10B981"
      - "#0F172A"
    background:
      - "#060B1A"
      - "#0F172A"
      - "#111827"
    text:
      - "#E5E7EB"
      - "#94A3B8"
      - "#FFFFFF"
    functional:
      - "#22C55E"
      - "#F59E0B"
      - "#EF4444"
      - "#38BDF8"
todos:
  - id: benchmark-profit-params
    content: 使用[mcp:graphlit-mcp-server]复核中国市场定价与成本阈值参数
    status: completed
  - id: map-gating-chain
    content: 使用[subagent:code-explorer]定位门控改造调用链与风险点
    status: completed
    dependencies:
      - benchmark-profit-params
  - id: add-profit-config
    content: 新增利润门控配置并更新config.py与default.toml默认值
    status: completed
    dependencies:
      - map-gating-chain
  - id: implement-profit-gate-core
    content: 实现profit_gate模块并接入api_service请求放行前检查
    status: completed
    dependencies:
      - add-profit-config
  - id: persist-profit-audit
    content: 扩展database审计结构并落库收入成本毛利与阻断原因
    status: completed
    dependencies:
      - implement-profit-gate-core
  - id: renovate-rule-page
    content: 改造index.html为先收款后执行与透明规则页面
    status: completed
    dependencies:
      - persist-profit-audit
  - id: verify-no-unpaid-calls
    content: 补充测试验证无未收款调用且连续多单毛利为正
    status: completed
    dependencies:
      - renovate-rule-page
---

## User Requirements

- 项目目标从“给用户出点子”切换为“Agent 自主赚钱并自我续航”。
- 核心闭环必须是：先有真实可收款订单，再允许付费模型调用，交付后记账复盘，利润回补算力预算。
- 明确禁止“先消耗 token 再找收入”的逆流程。
- 验证口径要可审计：无未收款付费调用、连续多单毛利为正、现金余额不下降。

## Product Overview

将现有系统重定位为“订单驱动利润门控执行器（Profit-Gated Executor）”。前台只展示透明规则与下单入口；后台以收款状态、单单预算、毛利阈值控制是否执行 LLM。系统以真实回款为唯一放行信号，形成“回款→执行→记账→再投资”的正向飞轮。

## Core Features

- 收款前门控：订单未确认收款时，拒绝任何付费模型执行。
- 利润门槛：预测毛利率不足阈值时自动拒单或降级模型。
- 单单预算器：每单限制最大 API 成本/最大 token，超限即停止。
- 成本收益审计：记录每次调用收入、成本、毛利、拒绝原因。
- 飞轮看板：展示现金余额、毛利率、再投资额度、止损状态。

## Tech Stack Selection

- 复用现有栈：Python + FastAPI + SQLite + 静态页（`index.html`）。
- 复用既有财务能力：`src/agent_core/economy/ledger.py`。
- 复用现有订单与鉴权：`src/agent_core/income/api_service.py`、`src/agent_core/income/api_keys.py`。
- 复用止损底座：`config/default.toml` 与 `src/agent_core/main.py` 中 `survival.enable_react_loop`。

## Implementation Approach

采用“收益前置 + 执行门控”方案：
1) 订单/密钥状态先校验；2) 预算与毛利预估通过后才调用 LLM；3) 执行后写入收入、成本与毛利审计。
关键决策：不重做整套交易系统，直接在已存在的 `purchase_orders`、`api_keys`、`api_key_usage` 与服务处理链上加门控，减少改造面并保留现有可用能力。

### 性能与可靠性

- 请求路径为 O(1) 数据库主键/索引查询（`order_id`、`api_key`）。
- 热路径只增加一次门控检查与一次审计写入，避免额外轮询。
- 失败优先（Fail-Closed）：门控判断失败时直接拒绝调用，不产生模型成本。

## Implementation Notes

- 现状已验证：
- `src/agent_core/income/api_service.py` 仍允许无 Key 免费试用路径（会触发模型成本），需在盈利模式下关闭或强门控。
- `src/agent_core/income/api_handlers.py` 在调用后记录 `ledger.record_expense`，可扩展为毛利审计输入。
- `src/agent_core/storage/database.py` 现有 `purchase_orders` 与 `api_key_usage` 可承接扩展字段/审计表。
- 日志沿用 structlog，新增 `profit_gate.blocked`、`profit_gate.allowed`、`profit_gate.margin_below_threshold`，避免记录敏感信息全文。
- 保持向后兼容：先新增配置并给默认值，不破坏现有启动流程。

## Architecture Design

- 入口层：`index.html`（规则透明化、先收款再交付说明）
- API层：`api_service.py`（订单状态 + 密钥/预算门控）
- 业务层：`api_handlers.py`（调用执行与成本回传）
- 策略层：[NEW] `src/agent_core/economy/profit_gate.py`（利润阈值与预算判定）
- 数据层：`database.py`（经济审计字段/表） + `ledger.py`（收入/支出落账）

## Directory Structure Summary

本次为“盈利闭环改造”，优先修改已有核心链路，少量新增策略模块。

/Users/nebula/Desktop/proj/self_improve_machine/

- `src/agent_core/config.py`  # [MODIFY] 新增利润门控配置模型（毛利阈值、单单预算、再投资比例、硬止损）。
- `config/default.toml`  # [MODIFY] 增加对应默认参数，确保默认即“先回款后调用”。
- `src/agent_core/income/api_service.py`  # [MODIFY] 在服务调用前接入订单/密钥/预算门控，关闭高成本免费路径。
- `src/agent_core/income/api_handlers.py`  # [MODIFY] 回填实际模型成本到门控审计，执行后更新单单毛利状态。
- `src/agent_core/storage/database.py`  # [MODIFY] 增加盈利审计表或扩展用量字段（收入、成本、毛利、阻断原因、时间）。
- `src/agent_core/main.py`  # [MODIFY] 启动时注入 ProfitGate 依赖，保持 `enable_react_loop=false` 策略。
- `src/agent_core/economy/profit_gate.py`  # [NEW] 利润门控与预算判定核心模块。
- `index.html`  # [MODIFY] 改为“先收款再执行”规则页，展示透明计费与拒绝条件。
- `tests/test_profit_gate.py`  # [NEW] 覆盖放行/拒绝、预算超限、毛利阈值与止损逻辑。
- `tests/test_api_profit_gating.py`  # [NEW] 覆盖“未收款禁止调用”“审计落库”“失败不放行”。

## Key Code Structures

```python
class ProfitGateConfig(BaseModel):
    min_gross_margin_ratio: float
    max_cost_per_request_usd: float
    hard_stop_balance_usd: float
    reinvest_ratio: float
    require_confirmed_payment: bool
```

```python
class ProfitDecision(TypedDict):
    allowed: bool
    reason: str
    estimated_cost_usd: float
    estimated_revenue_usd: float
    estimated_margin_ratio: float
```

采用桌面优先的高可信成交页：顶部“先收款后执行”承诺、透明计费规则、拒绝条件说明、下单与状态查询入口。强调风控可见性，弱化花哨承诺，增强可审计与可执行感。

## Agent Extensions

- **graphlit-mcp-server**
- Purpose: 复核中国市场同类 API 成本/定价带，校准毛利阈值与预算参数。
- Expected outcome: 输出可用于 `default.toml` 的参数基线（价格、成本、毛利区间）。

- **code-explorer**
- Purpose: 精确追踪门控逻辑在 `api_service.py`、`api_handlers.py`、`database.py` 的调用链与影响面。
- Expected outcome: 形成低回归风险的文件级改造清单与调用点映射。