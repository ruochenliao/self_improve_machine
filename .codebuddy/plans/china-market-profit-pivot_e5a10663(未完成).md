---
name: china-market-profit-pivot
overview: 基于国内市场做深度调研，确定最可行的低预算盈利项目，并制定可执行的30天变现路径与项目改造方案。
todos:
  - id: select-main-offer
    content: 使用[mcp:graphlit-mcp-server]收敛单一主卖品与价格梯度
    status: pending
  - id: trace-change-chain
    content: 使用[subagent:code-explorer]确认接口与数据库改造链路
    status: pending
    dependencies:
      - select-main-offer
  - id: implement-service-flow
    content: 实现线索创建、报价审核、付款凭证与交付状态接口
    status: pending
    dependencies:
      - trace-change-chain
  - id: revamp-conversion-page
    content: 改版index.html为咨询到成交闭环并接入新接口
    status: pending
    dependencies:
      - implement-service-flow
  - id: ship-ops-playbook
    content: 发布30天SOP与复盘模板，验证首单回款闭环
    status: pending
    dependencies:
      - revamp-conversion-page
---

## User Requirements

- 基于已有沟通与前期调研结果，给出“在中国市场能更快赚钱”的明确项目方向，而不是继续泛化尝试。
- 方案必须以低预算、快速成交、真实回款为优先，支持小额持续投入。
- 需要可执行、可验证的落地路径：做什么、怎么卖、如何交付、如何判断是否继续投入。
- 输出应可直接用于当前项目下一阶段改造与运营执行。

## Product Overview

将当前系统定位为“面向中国小微商家的 AI 获客代执行服务”，核心是按单收费交付（内容方案、线索承接、执行模板），而非继续依赖高成本自主循环。页面与后端围绕“咨询-报价-付款凭证-人工核验-交付”建立成交闭环。

## Core Features

- 单一主赛道收敛：从候选方向中固定一个主卖品与价格梯度，避免分散。
- 线索到订单闭环：收集客户需求、生成报价、记录付款凭证、人工审核放行。
- 标准化交付：为不同套餐自动生成可交付物（脚本、发布计划、执行清单）。
- 成本与止损：持续保持低成本运行，按真实回款与转化率决定扩投或暂停。
- 30天执行节奏：按周推进获客、转化、交付与复盘，确保首单可验证。

## Tech Stack Selection

- 复用现有项目技术栈：Python + FastAPI + SQLite + 静态落地页（index.html）。
- 复用既有订单与管理模式：`src/agent_core/income/api_service.py`、`src/agent_core/storage/database.py`。
- 复用现有止损机制：`survival.enable_react_loop=false`（已在配置与主流程中生效）。

## Implementation Approach

采用“单赛道服务化改造”策略：在现有 API 售卖框架上新增“线索/报价/交付”能力，保留人工核验，避免自动化收款误记收入。
高层流程：落地页收集需求 → 后端创建线索/报价单 → 用户付款并提交凭证 → 管理端审核通过 → 自动生成交付包。
关键决策：

- 不新建重系统，优先复用 `purchase_orders` 与管理接口模式，降低改造风险与时间成本。
- 不恢复高频 ReAct 循环，先以真实订单驱动成本投入，避免技术债与现金流风险。
- 先做“服务成交”再做“产品化订阅”，以首单速度优先。

## Implementation Notes

- **Performance**：线索与订单查询走时间索引，列表接口分页，避免全表扫描。
- **Logging**：复用 structlog；记录订单状态变更、审核动作、交付生成结果；不记录敏感隐私全文。
- **Blast Radius**：保持现有 API Key 逻辑可用，仅新增服务化接口与页面区块，不做大范围重构。
- **Reliability**：付款凭证始终 `pending` 到人工审核，收入仅在审核通过后写入账本。
- **Complexity**：线索列表/筛选为 O(n)，单订单状态变更 O(1)；满足当前规模。

## Architecture Design

沿用现有分层：`index.html`（展示与提交）→ `api_service.py`（业务路由）→ `database.py`（持久化）→ `ledger`（收入记录）。
新增模块仅围绕“服务订单生命周期”，不引入新架构范式。

## Directory Structure

## Directory Structure Summary

本次改造以“可成交服务闭环”为目标，主要在现有 API 服务、数据库与落地页上扩展。

/Users/nebula/Desktop/proj/self_improve_machine/
├── index.html  # [MODIFY] 改为中国市场服务成交页：需求收集、套餐说明、付款凭证提交、订单进度可视化。保持现有风格并强化转化文案。
├── src/agent_core/income/api_service.py  # [MODIFY] 新增线索创建/报价/审核/交付状态接口；对接人工审核后入账；复用现有 admin secret 机制。
├── src/agent_core/storage/database.py  # [MODIFY] 新增服务线索与交付追踪表（含状态、报价、备注、时间索引），保证审计可追踪。
├── config/default.toml  # [MODIFY] 增加服务套餐与运营参数（SLA、默认报价、人工审核超时阈值）。
├── src/agent_core/main.py  # [MODIFY] 保持低成本运行策略，确保服务接口常驻、空转循环关闭。
├── products/china-service-packages.md  # [NEW] 明确主卖品、交付边界、报价锚点与加购项，供页面与人工销售复用。
└── scripts/ops_30day_runbook_cn.md  # [NEW] 30天执行SOP：每日动作、数据记录模板、止损/扩投规则。

## Key Code Structures

- `ServiceLead`：`lead_id / contact / business_type / demand / budget / status / created_at`
- `ServiceQuote`：`quote_id / lead_id / package_name / price_cny / sla_days / status`
- `DeliveryRecord`：`order_id / deliverable_type / artifact_path / delivered_at / reviewer`

## Agent Extensions

- **SubAgent: code-explorer**
- Purpose: 精准定位新增线索/报价/交付功能在现有代码中的调用链与影响面。
- Expected outcome: 输出可直接实施的文件级改造点，减少回归风险。

- **MCP: graphlit-mcp-server**
- Purpose: 持续做中文市场赛道与报价信号复核（webSearch），避免一次性调研偏差。
- Expected outcome: 形成可更新的价格与需求依据，支持每周策略微调。