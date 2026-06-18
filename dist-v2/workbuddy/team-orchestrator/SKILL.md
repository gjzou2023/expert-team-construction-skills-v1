---
name: team-orchestrator
description: 全域专家团构建系统统一入口。Use when: 用户说"帮我建AI专家团""构建团队"等。自动编排8阶段流程。
---

# 全域专家团总编排器

## 概述

全域专家团构建 skills 系统统一入口。根据用户需求动态构建任意领域专家团（角色定义+协作流程+交付标准），自动完成需求深潜→领域消歧→链路拆解→交付物锚定→架构设计→工具链匹配→专家包生成→平台执行的 8 阶段全流程。

## 执行模式

本 skill 分 8 个阶段执行。**每个阶段开始时，必须先读取对应子 skill 完整指引**：

### 阶段检测

根据对话历史判断当前阶段。首次触发从 S1 开始。

### 阶段执行协议

1. 读取 `references/skills/pipeline-s{N}-*/SKILL.md`
2. 按其指引执行本阶段任务
3. 输出阶段结构化摘要（JSON 格式，~500 tokens）
4. 询问用户确认进入下一阶段

### 阶段清单

| 阶段 | 子 skill | 核心任务 |
|------|---------|---------|
| S1 | pipeline-s1-need-diving | 需求深潜 |
| S2 | pipeline-s2-domain-disambiguation | 领域消歧 |
| S3 | pipeline-s3-chain-decomposition | 链路拆解 |
| S4 | pipeline-s4-deliverable-anchoring | 交付物锚定 |
| S5 | pipeline-s5-architecture-design | 架构设计 |
| S6 | pipeline-s6-toolchain-matching | 工具链匹配 |
| S7 | pipeline-s7-expert-package-generation | 专家包生成 |
| S8 | pipeline-s8-platform-execution | 平台执行 |

### 通道路由

S2 输出 domain_type（A/B/C/D/F）和 channel（fast/standard/strict）。后续阶段根据 channel 调整执行深度。

### L0 核心引擎

每阶段读取对应 `references/skills/core-*`，根据任务类型激活对应核心引擎。

### L2 协议激活

读取 `references/knowledge/protocol-activation-map.json` 确定激活子集。S7 阶段调用全部激活的 L2 协议。

### L3 平台适配

S7 阶段根据用户选择的平台，读取 `references/skills/platform-{platform}-adapter/SKILL.md`。

### L4 全局约束（核心规则摘要）

20 条强制规则不可覆盖，11 条灵活规则依情况启用。完整规则见各 `constraint-*` 子 skill。

**核心强制规则**：交付物优先 → MECE 强制 → 合规不可绕过 → 平台可执行 → 分线强制 → 阶段跳转约束 → 字段追踪强制 → 单问规则 → 规范优先级 → 数据安全强制

### 快速通道

当用户角色数 ≤ 2 时，启用快速通道：保留核心交付物与兜底方案，跳过或内联低风险阶段。

### 异常处理

任何阶段失败时，调用 `references/skills/protocol-error-handling/SKILL.md` 执行降级策略。

### 版本迭代触发信号

当用户表达"做不了X"、"想要新能力"、"我想升级"或核心指标低于阈值时，重新触发 S1。

## 注意事项

- **必须**按序执行 S1→S8，不可跳过
- 每阶段**必须**先读取完整子 skill 指引再执行
- 阶段输出必须结构化（JSON 摘要）
- 用户确认后才进入下一阶段

## 完整子 skill 参考

完整的 40 个子 skill 原文见 `references/skills/` 目录。
完整的共享知识资源见 `references/knowledge/` 目录。
