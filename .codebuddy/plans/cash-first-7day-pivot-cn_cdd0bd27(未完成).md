---
name: cash-first-7day-pivot-cn
overview: 放弃现有API售卖框架，改为7天内优先回款的中国本地服务型变现方案，并给出可直接执行的获客-成交-交付路径。
design:
  architecture:
    framework: html
  styleKeywords:
    - 高转化
    - 专业可信
    - 轻运营
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
  - id: lock-main-offer
    content: 使用[mcp:graphlit-mcp-server]锁定单一主卖品与价格梯度
    status: pending
  - id: scan-change-scope
    content: 使用[subagent:code-explorer]确认页面改版影响文件范围
    status: pending
    dependencies:
      - lock-main-offer
  - id: revamp-landing-page
    content: 改造index.html为本地商家短视频获客服务成交页
    status: pending
    dependencies:
      - scan-change-scope
  - id: build-offer-docs
    content: 新增主卖品说明与标准交付边界文档
    status: pending
    dependencies:
      - revamp-landing-page
  - id: ship-7day-sop
    content: 发布7天首单SOP与每日复盘模板并执行验证
    status: pending
    dependencies:
      - build-offer-docs
---

## User Requirements

- 放弃“在现有接口售卖框架上继续扩展”的路径，改为全新变现思路。
- 目标是 **7天内拿到第一笔真实回款**，并且每天可投入 3-6 小时。
- 允许小额投入，但要以真实成交为核心，不做高风险长周期尝试。
- 输出必须可直接执行，且能明确判断继续投入或止损。

## Product Overview

将项目定位为“本地商家短视频获客代执行”现金流服务：先卖可交付结果（脚本、拍摄清单、发布计划、复盘建议），再考虑工具化。成交流程以人工沟通与交付为主，页面只负责说明服务、展示价格、收集咨询信息与引导付款。

## Core Features

- 单一主卖品：只做一个高需求、低交付复杂度服务包。
- 快速成交页：突出“7天见到内容产出”的承诺与边界。
- 标准化交付包：固定模板交付，压缩交付时间与返工。
- 7天冲刺SOP：按日触达、报价、跟进、交付、复盘。
- 止损与扩投规则：按真实回款和转化率决定加码或暂停。

## Tech Stack Selection

- 复用现有项目结构：Python 服务端、SQLite 数据层、静态 `index.html` 前端。
- 本轮不新增复杂后端交易链路，优先将技术工作收敛到页面改版与运营文档资产。
- 关键已验证约束（来自代码探索）：
- 现首页强绑定接口售卖路径：`/Users/nebula/Desktop/proj/self_improve_machine/index.html`
- 现有购买与订单接口集中在：`/Users/nebula/Desktop/proj/self_improve_machine/src/agent_core/income/api_service.py`
- 低成本开关已可用：`survival.enable_react_loop=false`（`config/default.toml`、`src/agent_core/main.py`）

## Implementation Approach

采用“**运营优先、代码最小化**”策略：先把首页从“接口售卖”改为“服务成交页”，并补齐报价与交付SOP文档，形成可执行获客脚本。
工作方式：页面负责转化入口与信任展示，成交与交付在线下人工完成，首单验证后再决定是否产品化。
关键决策：

- 不在当前接口售卖流程上继续叠加线索/报价/交付模块，避免重复失败路径。
- 不恢复高成本自主循环，维持低成本常驻。
- 以“首单回款时间”优先于“系统完备度”。

## Implementation Notes (Execution Details)

- **Performance**：本轮主要为静态页面与文档资产，无新增高频计算；避免引入额外后台轮询。
- **Logging**：沿用现有日志体系，仅保留运行与健康日志；运营数据放入SOP台账模板。
- **Blast radius control**：不改动核心数据库结构与订单表；尽量不触及 `api_service.py` 的既有业务。
- **Reliability**：保留现有服务可启动能力，确保 `main.py` 当前低成本运行行为不回退。

## Architecture Design

沿用当前单体结构，不引入新架构：

- 展示层：`index.html`（服务说明、报价、转化引导）
- 运行层：`main.py` 保持服务进程稳定与低成本策略
- 数据层：现有 SQLite 维持原状，本轮不做新表扩展
- 运营层：新增标准化文档驱动人工成交与交付

## Directory Structure

## Directory Structure Summary

本次改造重点是“页面转化 + 运营资产”，避免再次进入重后端开发。

/Users/nebula/Desktop/proj/self_improve_machine/

- `index.html`  # [MODIFY] 从“API售卖页”改为“本地商家短视频获客代执行”成交页。实现服务包展示、适用对象、交付边界、试做申请引导、付款与联系说明，删除/弱化API购买主路径文案。
- `README.md`  # [MODIFY] 更新项目定位为“7天首单现金流项目”，新增启动步骤、每日执行节奏与验收口径，避免继续误导为接口产品主项目。
- `products/marketing/china-local-shortvideo-offer.md`  # [NEW] 主卖品说明书。包含目标客群、套餐梯度、交付清单、不做事项、加价项、标准话术。
- `scripts/ops_7day_first-revenue_cn.md`  # [NEW] 7天冲刺SOP。按天定义触达量、跟进频次、报价动作、交付节奏、复盘指标和止损阈值。
- `scripts/ops_metrics_template_cn.md`  # [NEW] 每日数据模板。记录线索数、沟通数、报价数、付款数、客单价、回款额、问题与调整动作。

## 设计方案

单页桌面优先，采用“高信任成交页”结构：顶部价值主张、服务包对比、试做申请、成交流程、常见异议、底部行动入口。
页面区块（自上而下）：

1. 顶部导航与主Banner：一句话承诺 + 明确适用对象 + 主CTA。  
2. 服务包与价格区：三档套餐、交付边界、预计交付时长。  
3. 试做申请区：提交商家信息与目标，获得样稿说明。  
4. 成交与交付流程区：咨询→确认→付款→交付→复盘。  
5. 信任与FAQ区：案例样式、风险说明、退款边界。  
6. 底部导航与二次CTA：联系入口与当日名额提醒。

## Agent Extensions

- **MCP: graphlit-mcp-server**
- Purpose: 复核中国市场细分需求、报价带与竞争密度，持续校准主卖品。
- Expected outcome: 形成每周可更新的报价与话术依据，降低方向偏差。

- **SubAgent: code-explorer**
- Purpose: 快速定位并确认页面与文档改造影响面，避免误改核心运行链路。
- Expected outcome: 输出精准文件级改造清单，控制回归风险与改动范围。