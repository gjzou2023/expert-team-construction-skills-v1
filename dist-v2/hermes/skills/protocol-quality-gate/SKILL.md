---
name: protocol-quality-gate
description: 八层65项自检(原八层59项+标注比例约束+商业模式可行性)→汇总为架构健康检查报告→🟡有条件通过→🔴阻断输出。v1.4.0新增认知诚实标注比例约束和商业模式可 Use when: 用户说"protocol-quality-gate、质量门、L2质检"等触发词。
version: 1.4.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [l2]
    related_skills: []
    requires_toolsets: []
---

> **注意**：本 skill 的核心规则已内联至 `team-orchestrator/SKILL.md` 的 `L2` 章节。
> 执行时优先读取 team-orchestrator 的内联指引，仅在需要完整逻辑时再读取本文件。
>
# 质量守门协议

> **层级**: L2 | **版本**: 1.4.0 | **ID**: `protocol-quality-gate` | **中文名**: 质量守门协议 | **英文名**: Quality Gate
# 质量守门协议 (Quality Gate)

> **层级**: L2 | **版本**: 1.4.0 | **ID**: `protocol-quality-gate`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

八层65项自检(5.1-5.7+5.6.5+5.6.8+标注比例约束+商业可行性)+跨阶段一致性检查(5.7.5)→汇总为架构健康检查报告→🟡有条件通过→🔴阻断输出。v1.4.0新增认知诚实标注比例约束和商业模式可行性检查。

## 触发条件

当检测到以下关键词或场景时自动激活：自检, 质量, 健康检查, MECE校验, 阻断

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "architecture": {
      "type": "object",
      "description": "S5架构输出"
    },
    "expert_package": {
      "type": "object",
      "description": "S7专家包输出"
    },
    "previous_stage_outputs": {
      "type": "object",
      "description": "前序阶段输出"
    }
  },
  "required": [
    "architecture"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "health_report": {
      "type": "object",
      "properties": {
        "architecture": {
          "type": "string"
        },
        "roles": {
          "type": "string"
        },
        "compliance": {
          "type": "string"
        },
        "workflow": {
          "type": "string"
        },
        "data_security": {
          "type": "string"
        },
        "user": {
          "type": "string"
        },
        "platform_executability": {
          "type": "string"
        },
        "cross_stage_consistency": {
          "type": "string"
        }
      }
    },
    "warnings": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "blockers": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  },
  "required": [
    "health_report",
    "warnings",
    "blockers"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 七层48项自检清单

### 5.1 架构层(6项)
1. 所有交付物是否都有且仅有一个第一责任角色
2. 数据流向是否完整（输入→处理→输出→反馈，全链路无断点）
3. 不同渠道/场景的交付物是否已正确分线设计
4. 反馈回路是否完整
5. 冷启动策略是否已定义
6. 交付物优先级和依赖关系是否已明确

### 5.2 角色层(8项)
**MECE三问(3项-阻断性):**
1. 覆盖性：全链路每个环节是否都有至少一个角色负责？有没有无主地带？
2. 独立性：是否有两个角色核心职责超过30%重叠？
3. 责任唯一性：每个终端交付物是否有且仅有一个第一责任人？
**附加(5项):**
4. 角色数量在合理范围内
5. 每个角色指令达到最低规格(≥200字)
6. 通信/调用协议已定义
7. Agent ID符合kebab-case
8. 花名符合命名规范（2-3字正常人名、谐音巧思、不与profession重复）

### 5.3 合规层(6项)
1. 强监管行业是否已激活合规协议
2. 合规检查清单10项是否已执行
3. 禁用词列表长度是否达标（低≥3, 高/强监管≥8）
4. 法定提示语是否已添加
5. 国际法规是否已检查（如适用）
6. 合规时效性：检查规则是否为最新版本

### 5.4 工作流层(6项)
1. SOP Phase定义是否完整
2. 每个Phase的触发条件是否明确
3. Phase间的数据传递是否已定义
4. 路由表是否已生成
5. 初始交互协议是否已定义
6. 快速通道简化规则是否已执行（如适用）

### 5.5 数据安全层(4项)
1. 每个工具的数据安全等级是否已评估
2. 高敏感度领域是否禁止敏感数据→第三方
3. 数据流向是否已文档化
4. 纯提示词兜底方案是否存在

### 5.6 用户层(6项)
1. 话术是否使用用户能听懂的语言
2. 术语首次出现是否附通俗解释
3. 选项是否具体（非抽象描述）
4. 单问规则是否遵守
5. 交互节奏是否合理
6. 确认阶段是否展示汇总卡片

### 5.6.5 认知诚实与不确定性标注（6项）（v1.3.0新增）

每位专家在给出建议时，必须对每个关键判断标注确定性等级：

1. 🟢 高确信：基于普遍共识的行业惯例/成熟方法论
2. 🟡 中确信：基于合理推理但未经该具体场景验证
3. 🔴 低确信/需外部验证：涉及最新政策、前沿技术参数、具体法规条文等需用户自行核实的内容

自检项：
1. 所有关键判断是否已标注确定性等级（🟢/🟡/🔴）
2. 🔴标注项是否给出了用户自行核实的具体方向
3. 是否存在本该标注🔴却标注为🟢的过度自信
4. 是否存在本该有确定性标注却缺失的关键判断
5. 最终输出末尾是否包含「边界声明」
6. 边界声明是否具体列出了建议咨询持证专业人士/获取最新官方文件的方向

边界声明模板：
> "以下方面建议咨询持证专业人士/获取最新官方文件：[具体列出]"

### 标注比例约束（v1.4.0新增）

为避免🔴标注泛滥导致"免责声明"效应，执行以下比例约束：

| 场景 | 🟢占比建议 | 🟡占比建议 | 🔴占比建议 | 约束等级 |
|------|-----------|-----------|-----------|---------|
| 成熟行业+标准通道 | ≥60% | 20-30% | ≤10% | 硬约束 |
| 新兴领域+标准通道 | ≥40% | 30-40% | ≤20% | 硬约束 |
| 前沿探索+严格通道 | ≥20% | 40-50% | ≤30% | 软约束(建议) |

若🔴占比超过约束：
1. 检查是否存在本该标注🟢但过度谨慎降为🔴的情况
2. 对🔴标注逐项确认"是否确实无法给出任何方向性建议"
3. 若能给出方向性建议，升级为🟡并附条件说明
4. 最终报告需在边界声明中注明"本方案🔴标注占比XX%，建议在XX方面咨询专业人士"

### 5.6.8 方案可行性过滤器（5项）（v1.3.0新增）

在输出前增加可行性过滤，对以下5个问题逐一检查：

□ 1. 方案中是否有超出当前技术成熟度的假设？
  → 若发现有"TRL 1-3级"（实验室/概念验证阶段）技术被当作可用技术假设，标注为🔴阻断
□ 2. 建议的资源投入是否与用户隐含的规模/预算匹配？
  → 小型团队推荐大型架构方案 → 标注🔴
□ 3. 时间节点是否符合行业常规节奏？
  → 建议"1周上线"但涉及强合规审查 → 标注🟡警告
□ 4. 是否有关键前置条件被遗漏？
  → 依赖未说明的数据源/API/审批 → 标注🔴
□ 5. 方案的每一步是否有明确的验证方式？
  → 无验证方式的步骤 → 标注🟡警告
□ 6. 方案的商业模式/价值假设是否成立？（v1.4.0新增）
  → 方案需要用户付费但目标市场免费习惯占主导 → 标注🟡警告
  → 方案依赖垄断性资源但无获取路径 → 标注🔴
  → 方案的投入产出比ROI是否可接受(粗估) → 标注🟡警告

### 发现问题的处理

若自检发现问题：
- 标注该环节的风险等级（🔴/🟡）
- 提供备选方案或降级选项
- 明确告知用户"此处建议实际可行性有待验证"
- 🔴问题必须给出至少一个替代方案

### 5.7 平台可执行性层(12项)
1. 专家包格式符合目标平台规范
2. 所有必填元数据已填充（无[TODO]占位符）
3. Agent MD/TOML/SKILL.md元数据完整
4. categoryId从标准列表选择
5. tags恰好3个（中英文）
6. quickPrompts恰好3个（中英文），第一条与defaultInitPrompt一致
7. displayDescription中文40-50字
8. Team型teamInfo配置正确
9. 主理人profession避免通用title
10. 每个团员指令包含结果回传要求
11. 有校验+注册的执行计划
12. Schema兼容性已验证

### 5.7.5 跨阶段一致性检查
- 检查S1→S2→S3→S4→S5→S6→S7→S8各阶段产出字段引用是否一致
- 检查阶段间数据传递是否有断点
- 检查回退影响链是否完整

## 执行逻辑

七层自检(5.1-5.7)+跨阶段一致性检查(5.7.5)→汇总为架构健康检查报告(5.8)。5.1架构层(6项);5.2角色层MECE三问(8项,含命名规范);5.3合规层(6项);5.4工作流层(6项);5.5数据安全层(4项);5.6用户层(6项);5.7平台可执行性层(12项);5.7.5跨阶段一致性。报告格式：✅全部通过→'全部通过';🟡有≥1个→列🟡条目+简要说明(≤3行);🔴有≥1个→列所有🔴+必须修复行动(阻断输出)。MECE三问(阻断性)：(1)覆盖性:每个环节有至少一个角色负责?(2)独立性:两个角色核心职责重叠>30%?(3)责任唯一性:每个交付物有且仅有一个第一责任人?任一不通过→🔴阻断。

## Few-shot 示例

### 示例 1：正常流程 — 架构健康检查全部通过

**输入**:
```json
{
  "architecture": {
    "roles": [
      { "id": "content-strategist", "deliverables": ["选题方案", "内容日历"] },
      { "id": "copywriter", "deliverables": ["文案草稿"] },
      { "id": "visual-designer", "deliverables": ["配图", "封面"] }
    ],
    "workflow": { "phases": ["选题", "创作", "审核", "发布"], "transitions_complete": true }
  },
  "expert_package": {
    "format": "workbuddy-team",
    "metadata_complete": true,
    "tags": ["内容运营", "Content Ops", "小红书"]
  }
}
```

**输出**:
```json
{
  "health_report": {
    "architecture": "✅",
    "roles": "✅",
    "compliance": "✅",
    "workflow": "✅",
    "data_security": "✅",
    "user": "✅",
    "platform_executability": "✅",
    "cross_stage_consistency": "✅"
  },
  "warnings": [],
  "blockers": []
}
```

### 示例 2：异常流程 — MECE角色层阻断

**输入**:
```json
{
  "architecture": {
    "roles": [
      { "id": "content-writer", "deliverables": ["文案", "标题", "封面文案"] },
      { "id": "editor", "deliverables": ["文案", "标题", "封面文案"] }
    ]
  },
  "expert_package": {}
}
```

**输出**:
```json
{
  "health_report": {
    "architecture": "✅",
    "roles": "🔴",
    "compliance": "🟡",
    "workflow": "🟡",
    "data_security": "✅",
    "user": "✅",
    "platform_executability": "🟡",
    "cross_stage_consistency": "🟡"
  },
  "warnings": [
    "合规层：角色未定义，行业合规检查无法执行",
    "平台可执行性层：专家包元数据未填充"
  ],
  "blockers": [
    {
      "layer": "角色层",
      "issue": "MECE三问-独立性失败: content-writer与editor核心职责100%重叠",
      "fix": "合并为一个角色或重新划分交付物所有权"
    }
  ]
}
```

### 示例 3：快速通道 — 简化自检黄灯

**输入**:
```json
{
  "architecture": {
    "roles": [{ "id": "all-in-one", "deliverables": ["全部产出"] }],
    "channel": "fast"
  },
  "expert_package": {
    "format": "workbuddy-single-agent",
    "tags": ["快速原型", "Prototype", "测试"]
  }
}
```

**输出**:
```json
{
  "health_report": {
    "architecture": "🟡",
    "roles": "🟡",
    "compliance": "🟡",
    "workflow": "🟡",
    "data_security": "🟡",
    "user": "✅",
    "platform_executability": "🟡",
    "cross_stage_consistency": "✅"
  },
  "warnings": [
    "架构层：单角色承担全链路，建议后续拆分",
    "合规层：快速通道使用静态清单",
    "数据安全层：单角色无权限隔离"
  ],
  "blockers": []
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://quality-gate/seven-layers-checklist` — 七层自检清单(5.1-5.7)

## 依赖关系

- `core-mental-model-engine`

## 七层48项自检清单

| 层级 | 序号 | 检查项 | 通过/不通过标准 |
| --- | --- | --- | --- |
| 架构层 | 1 | 所有交付物都有且仅有一个第一责任角色 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 架构层 | 2 | 数据流向完整：输入-处理-输出-反馈无断点 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 架构层 | 3 | 不同渠道/场景已正确分线 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 架构层 | 4 | 反馈回路完整且按领域激活 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 架构层 | 5 | 冷启动策略已定义 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 架构层 | 6 | 交付物优先级和依赖关系明确 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 1 | 覆盖性：全链路每个环节至少一个角色负责 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 2 | 独立性：两个角色核心职责重叠不超过30% | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 3 | 责任唯一性：每个终端交付物只有一个第一责任人 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 4 | 角色数量在通道和平台能力范围内 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 5 | 每个角色指令达到最低规格 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 6 | 通信/调用协议已定义 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 7 | Agent ID符合kebab-case | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 角色层 | 8 | 花名符合2-3字正常人名规则且不与profession重复 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 合规层 | 1 | 目标平台规则已检查 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 合规层 | 2 | 强监管行业已激活4.1-4.5全协议 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 合规层 | 3 | 禁用词数量满足低复杂度>=3/强监管>=8 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 合规层 | 4 | 免责声明和资质标注完整 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 合规层 | 5 | 导流/绝对化/虚假宣传风险已审查 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 合规层 | 6 | 国际平台已检查对应地区法规 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 工作流层 | 1 | 每个SOP Phase有输入、动作、输出、责任人 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 工作流层 | 2 | 上游输出能被下游机器解析 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 工作流层 | 3 | 关键节点有确认或审批机制 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 工作流层 | 4 | 所有自动化触发有失败策略 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 工作流层 | 5 | 反馈信号能回流到对应角色 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 工作流层 | 6 | 快速通道跳过项已内联处理 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 数据安全层 | 1 | 敏感数据类型已分级 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 数据安全层 | 2 | 第三方工具数据流向已标注 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 数据安全层 | 3 | 高敏感数据禁止外发或已人工确认 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 数据安全层 | 4 | 多模态资产保存模型版本/种子/提示词/参数 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 用户层 | 1 | 术语首次出现附通俗解释 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 用户层 | 2 | 每次信息采集只问一个问题 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 用户层 | 3 | 确认卡能让用户发现偏差 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 用户层 | 4 | 新手用户有默认值和可回退说明 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 用户层 | 5 | 输出可直接执行而非只讲原则 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 用户层 | 6 | 已知限制在交付前明确标注 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 1 | 专家包格式符合目标平台规范 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 2 | 所有必填元数据无TODO占位 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 3 | Agent MD/TOML/SKILL.md元数据完整 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 4 | categoryId从标准列表选择 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 5 | tags恰好3个且中英文可读 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 6 | quickPrompts恰好3个且第一条等于defaultInitPrompt | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 7 | displayDescription中文40-50字 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 8 | Team型teamInfo配置正确 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 9 | 主理人profession避免通用title | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 10 | 每个团员指令包含结果回传要求 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 11 | 有校验和注册执行计划 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |
| 平台可执行性层 | 12 | 平台缺失能力已提供纯提示词兜底 | 有证据或字段对应则通过；缺证据为黄灯；违反硬约束为红灯。 |

```text
FUNCTION execute_quality_gate(stage, output_draft):
    stage_self_check = [信息完整性, 判断可靠性, 可执行性, 平台可执行性]
    FOR check IN stage_self_check:
        result = evaluate(check, output_draft)
        IF result.severity == "blocking":
            HALT_OUTPUT()
            DISCLOSE_TO_USER(result.issue, result.alternatives)
    report = {}
    blocking_issues = []
    FOR layer IN [架构层, 角色层, 合规层, 工作流层, 数据安全层, 用户层, 平台可执行性层]:
        layer_result = evaluate_layer(layer, output_draft)
        report[layer] = layer_result
        IF layer_result.status == "🔴":
            blocking_issues.append(layer_result)
    IF stage >= 5:
        consistency = execute_cross_stage_consistency(output_draft)
        report["跨阶段一致性层"] = consistency
    IF blocking_issues:
        FIX_ALL(blocking_issues)
        RETURN execute_quality_gate(stage, fixed_output)
    RETURN generate_health_report(report)
```

## 详细执行逻辑

```text
FUNCTION execute_protocol_quality_gate(input):
    ASSERT input.architecture IS NOT NULL

    // === 第一步：加载七层自检清单与上下文 ===
    LOAD file://quality-gate/seven-layers-checklist
    LOAD context_inheritance FROM core-mental-model-engine
    report = {}
    warnings = []
    blockers = []
    blocking_issues = []

    // === 第二步：七层48项逐一自检(5.1-5.7) ===
    layers = [架构层(6项), 角色层(8项), 合规层(6项), 工作流层(6项), 数据安全层(4项), 用户层(6项), 平台可执行性层(12项)]

    FOR layer IN layers:
        layer_result = {}
        layer_status = "✅"

        FOR check_item IN layer.check_items:
            result = evaluate_check(check_item, input)

            IF result.evidence_found:
                result.status = "✅"
            ELIF result.evidence_missing AND NOT result.hard_constraint:
                result.status = "🟡"
                warnings.append(result.description + "：缺证据为黄灯")
                layer_status = "🟡"
            ELIF result.evidence_missing AND result.hard_constraint:
                result.status = "🔴"
                blockers.append(result)
                layer_status = "🔴"

        report[layer.name] = layer_status

    // === 第三步：角色层MECE三问(阻断性)专项检查 ===
    mece_coverage = CHECK_覆盖性(全链路每个环节是否有至少一个角色负责)
    mece_independence = CHECK_独立性(是否有两个角色核心职责重叠>30%)
    mece_uniqueness = CHECK_责任唯一性(每个终端交付物是否有且仅有一个第一责任人)

    IF NOT mece_coverage.passed:
        report["角色层"] = "🔴"
        blockers.append({layer:"角色层", issue:"MECE覆盖性失败:存在无主环节", fix:"为缺失环节分配责任角色"})
    IF NOT mece_independence.passed:
        report["角色层"] = "🔴"
        blockers.append({layer:"角色层", issue:"MECE独立性失败:角色核心职责重叠>30%", fix:"合并角色或重新划分交付物所有权"})
    IF NOT mece_uniqueness.passed:
        report["角色层"] = "🔴"
        blockers.append({layer:"角色层", issue:"MECE责任唯一性失败:交付物存在多个第一责任人", fix:"明确交付物唯一第一责任人"})

    // === 第四步：跨阶段一致性检查(5.7.5) ===
    IF input.stage >= 5 OR input.previous_stage_outputs IS NOT EMPTY:
        consistency = execute_cross_stage_consistency(input)
        // 检查S1→S2→S3→S4→S5→S6→S7→S8各阶段产出字段引用是否一致
        FOR stage_pair IN consistency.stage_pairs:
            IF NOT stage_pair.field_references_consistent:
                warnings.append("跨阶段不一致: " + stage_pair.description)
            IF NOT stage_pair.data_pass_complete:
                blockers.append({layer:"跨阶段一致性", issue:stage_pair.gap_description, fix:"补充缺失的阶段间数据传递"})
            IF NOT stage_pair.rollback_chain_complete:
                warnings.append("回退影响链不完整: " + stage_pair.rollback_gap)

        IF consistency.has_issues:
            report["跨阶段一致性层"] = "🟡"
        ELSE:
            report["跨阶段一致性层"] = "✅"
    ELSE:
        report["跨阶段一致性层"] = "N/A"

    // === 第五步：阻断逻辑(🔴→HALT→递归修复) ===
    IF blockers IS NOT EMPTY:
        // 🔴阻断输出
        HALT_OUTPUT()
        FOR blocker IN blockers:
            OUTPUT "🔴阻断: " + blocker.issue
            OUTPUT "必须修复行动: " + blocker.fix
        // 递归修复
        fixed_output = FIX_ALL(blockers, input)
        RETURN CALL execute_protocol_quality_gate(fixed_output)

    // === 第六步：生成健康检查报告(§5.8格式) ===
    health_report = {}
    FOR layer_name IN [架构层, 角色层, 合规层, 工作流层, 数据安全层, 用户层, 平台可执行性层, 跨阶段一致性层]:
        IF report[layer_name] == "✅":
            health_report[layer_name] = "✅"
        ELIF report[layer_name] == "🟡":
            health_report[layer_name] = "🟡"
            // 列🟡条目+简要说明(≤3行)
            yellow_items = GET_YELLOW_ITEMS(layer_name, warnings)
            FOR item IN yellow_items:
                APPEND_TO warnings(item.brief_description)
        ELIF report[layer_name] == "🔴":
            health_report[layer_name] = "🔴"

    // === 第七步：最终断言与输出 ===
    ASSERT health_report IS NOT EMPTY
    ASSERT blockers IS EMPTY  // 若非空则已在第五步递归修复

    CALL protocol-quality-gate before final output  // 自检闭环
    RETURN {health_report, warnings, blockers}
```

## 版本

1.4.0

---
*本Skill由全域专家团构建skills体系生成，版本1.4.0，日期2026-06-17*
