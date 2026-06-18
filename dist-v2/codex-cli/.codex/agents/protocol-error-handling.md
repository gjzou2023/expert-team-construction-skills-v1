
# 异常处理与降级协议 (Error Handling Protocol)

> **层级**: L2 | **版本**: 1.0.0 | **ID**: `protocol-error-handling`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

8类失败模式识别→预设降级策略→决策快照→通知→必要时人工审批。包含状态管理与回滚。

## 触发条件

当检测到以下关键词或场景时自动激活：失败, 异常, 降级, 回滚, 错误, 工具不可用

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "failure_type": {
      "type": "string",
      "enum": [
        "accuracy",
        "upstream_downstream",
        "tool_unavailable",
        "vague_input",
        "quality_fluctuation",
        "compliance_violation",
        "ai_self_error",
        "platform_execution"
      ]
    },
    "context": {
      "type": "string"
    },
    "severity": {
      "type": "string",
      "enum": [
        "low",
        "medium",
        "high",
        "critical"
      ]
    }
  },
  "required": [
    "failure_type",
    "context",
    "severity"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "degradation_action": {
      "type": "string"
    },
    "decision_snapshot": {
      "type": "object"
    },
    "notification_targets": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "human_approval_required": {
      "type": "boolean"
    }
  },
  "required": [
    "degradation_action",
    "decision_snapshot",
    "notification_targets",
    "human_approval_required"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)失败模式识别(8类)→(2)按类型执行预设降级策略→(3)记录决策快照→(4)通知相关角色→(5)必要时触发人工审批。8类失败模式：(1)准确性(2)上下游断裂(3)工具不可用(4)输入模糊(5)质量波动(6)合规违规(7)AI自错(8)平台执行失败。状态管理与回滚：决策快照;回滚触发(数据异常/合规违规/用户主动);平台变更回滚;前置确认线。回退触发词：等等/我想改/不对/重新想想→暂停→识别修改→影响评估→确认→同步更新。上下文压缩：对话>40轮→快照压缩。

## Few-shot 示例

### 示例 1：正常流程 — 工具不可用降级处理

**输入**:
```json
{
  "failure_type": "tool_unavailable",
  "context": "WebSearch API超时，无法获取目标平台最新合规规则",
  "severity": "medium"
}
```

**输出**:
```json
{
  "degradation_action": "L1工具降级：切换为纯提示词方案，使用模型内置知识+静态合规清单",
  "decision_snapshot": {
    "timestamp": "2026-06-15T10:00:00Z",
    "failure_type": "tool_unavailable",
    "action_taken": "L1工具降级→纯提示词兜底",
    "rationale": "WebSearch不可用，降级为本地静态知识库",
    "impact": "合规审查结果标注⚡'知识来源为本地清单非实时规则'"
  },
  "notification_targets": ["主理人"],
  "human_approval_required": false
}
```

### 示例 2：异常流程 — 合规审查全部红灯阻断

**输入**:
```json
{
  "failure_type": "compliance_violation",
  "context": "金融方案中对收益做绝对化承诺+缺少风险提示+未标注资质来源，合规审查全部🔴",
  "severity": "critical"
}
```

**输出**:
```json
{
  "degradation_action": "🔴阻断输出+生成修复行动清单→修复后重新触发protocol-compliance-engine审查",
  "decision_snapshot": {
    "timestamp": "2026-06-15T10:00:00Z",
    "failure_type": "compliance_violation",
    "action_taken": "阻断+修复清单",
    "violations": ["绝对化用语", "风险提示缺失", "资质标注缺失"],
    "fix_checklist": [
      "删除'保本保息'→添加'投资有风险'标准提示",
      "补充产品备案编号和发行机构资质",
      "重新执行10项合规检查后提交"
    ]
  },
  "notification_targets": ["主理人", "合规官"],
  "human_approval_required": true
}
```

### 示例 3：快速通道 — AI自错回退

**输入**:
```json
{
  "failure_type": "ai_self_error",
  "context": "用户在S5阶段说'等等，刚才说的不对，我的团队其实有5个人不是3个人'",
  "severity": "low"
}
```

**输出**:
```json
{
  "degradation_action": "暂停→回到S2误判源头→重新消歧(团队规模)→级联更新S3-S5→更新快照",
  "decision_snapshot": {
    "timestamp": "2026-06-15T10:05:00Z",
    "failure_type": "ai_self_error",
    "action_taken": "回退到S2修正用户画像",
    "trigger_word": "刚才说的不对",
    "rollback_scope": "S2消歧→S3复杂度→S4通道→S5角色架构",
    "reusable_outputs": ["领域类型判定结果", "目标平台信息"]
  },
  "notification_targets": [],
  "human_approval_required": false
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://error-handling/eight-failure-modes` — 8类失败模式定义与降级策略

## 依赖关系

- `core-mental-model-engine`

## 回退触发词与极端场景降级矩阵

回退触发词：等等、我想改一下、刚才说的不对、重新想想、不对、改个方向。

## 极端场景应对矩阵(10类)

| # | 极端场景 | 应对策略 | 恢复路径 |
|---|---------|---------|---------|
| 1 | 用户全程"不确定" | 使用默认值+标注"默认选择,可后续修改" | 后续阶段可修改 |
| 2 | 目标平台无任何工具能力 | 全部降级为纯提示词 | 标注"建议V2部署" |
| 3 | 合规审查全部🔴 | 阻断输出+修复行动清单 | 修复后重新审查 |
| 4 | 工具全部不可用 | 纯提示词兜底+标注"建议V2部署" | 人工选择替代方案 |
| 5 | 用户中途更换领域类型 | 回退到S2重新消歧+级联更新 | 保留部分可复用产出 |
| 6 | S7三步门用户要求大量修改 | 修改后重走三步门 | 增量修改不重做 |
| 7 | 自动化触发连续失败≥3 | 暂停任务+升级告警 | 人工介入排查 |
| 8 | 高敏感度用户坚持用第三方 | 🔴阻断+风险告知+人工确认 | 确认后记录风险 |
| 9 | AI自身出错 | 暂停→回到误判源头→重新执行→更新快照 | 快照回退机制 |
| 10 | 平台执行失败 | 定位缺失字段→修复→重新注册 | 错误详情输出 |

## 降级策略矩阵(L0-L4)

| 降级层级 | 条件 | 表现 |
|---------|------|------|
| L0完整功能 | 所有工具可用+平台完整支持 | 全部功能正常 |
| L1工具降级 | 部分工具不可用 | 不可用工具→纯提示词兜底 |
| L2调度降级 | 无外部调度能力 | Automation→纯提示词定时提醒 |
| L3平台降级 | 平台无Team型支持 | Team型→Agent型+scenario branches |
| L4纯提示词 | 无任何平台能力 | 全部功能用提示词实现,标注"建议V2部署" |

```text
FUNCTION handle_change_request(user_input):
    IF contains_any(user_input, TRIGGER_WORDS):
        PAUSE()
        modification = IDENTIFY_OR_ASK(user_input)
        impact = assess_downstream_impact(modification)
        OUTPUT impact_list
        WAIT_FOR_CONFIRMATION()
        FOR affected IN impact:
            update_section(affected)
        CALL core-state-management-engine.update_snapshot()
```

## 详细执行逻辑

```text
FUNCTION execute_protocol_error_handling(input):
    ASSERT input.failure_type IN ["accuracy","upstream_downstream","tool_unavailable","vague_input",
        "quality_fluctuation","compliance_violation","ai_self_error","platform_execution"]
    ASSERT input.context IS NOT EMPTY
    ASSERT input.severity IN ["low","medium","high","critical"]

    // === 第一步：6个回退触发词检测 ===
    TRIGGER_WORDS = ["等等", "我想改一下", "刚才说的不对", "重新想想", "不对", "改个方向"]
    IF CONTAINS_ANY(input.context, TRIGGER_WORDS):
        // 触发回退5步流程
        PAUSE()
        modification = IDENTIFY_OR_ASK(input.context)
        impact = assess_downstream_impact(modification)
        OUTPUT impact_list
        WAIT_FOR_CONFIRMATION()
        FOR affected IN impact:
            update_section(affected)
        CALL core-state-management-engine.update_snapshot()
        RETURN {degradation_action: "回退修改完成", decision_snapshot: SNAPSHOT(input), notification_targets: [], human_approval_required: false}

    // === 第二步：8类失败模式识别 ===
    failure_map = {
        "accuracy": "准确性失败 — 输出内容与事实不符",
        "upstream_downstream": "上下游断裂 — 阶段间数据传递断点",
        "tool_unavailable": "工具不可用 — 外部工具/API超时或失败",
        "vague_input": "输入模糊 — 用户信息不足以继续",
        "quality_fluctuation": "质量波动 — 输出质量不稳定",
        "compliance_violation": "合规违规 — 内容违反合规规则",
        "ai_self_error": "AI自错 — AI自身判断失误",
        "platform_execution": "平台执行失败 — 注册/部署阶段出错"
    }
    identified_failure = failure_map[input.failure_type]

    // === 第三步：4种回退场景与预设降级策略 ===
    degradation_action = ""
    human_approval_required = false
    notification_targets = []

    IF input.failure_type == "tool_unavailable":
        // 场景1: 工具不可用 → L1工具降级为纯提示词兜底
        degradation_action = "L1工具降级：切换为纯提示词方案，使用模型内置知识+静态清单"
        notification_targets = ["主理人"]
        human_approval_required = false

    ELIF input.failure_type == "compliance_violation":
        // 场景2: 合规违规 → 🔴阻断+修复清单+重审
        degradation_action = "🔴阻断输出+生成修复行动清单→修复后重新触发protocol-compliance-engine审查"
        notification_targets = ["主理人", "合规官"]
        human_approval_required = true

    ELIF input.failure_type == "ai_self_error":
        // 场景3: AI自错 → 暂停→回到误判源头→重新执行→更新快照
        degradation_action = "暂停→回到误判源头→重新执行→级联更新→更新快照"
        notification_targets = []
        human_approval_required = false

    ELIF input.failure_type == "platform_execution":
        // 场景4: 平台执行失败 → 定位缺失字段→修复→重新注册
        degradation_action = "定位缺失字段→修复→重新注册"
        notification_targets = ["主理人"]
        human_approval_required = input.severity == "critical"

    ELIF input.failure_type == "upstream_downstream":
        degradation_action = "回退到上游断裂点→重新执行下游阶段→更新快照"
        notification_targets = ["主理人"]
        human_approval_required = input.severity == "high" OR input.severity == "critical"

    ELIF input.failure_type == "vague_input":
        degradation_action = "使用默认值+标注'默认选择,可后续修改'→继续执行"
        notification_targets = []
        human_approval_required = false

    ELIF input.failure_type == "accuracy" OR input.failure_type == "quality_fluctuation":
        degradation_action = "暂停→标注质量风险→重新生成→对比后选择较优结果"
        notification_targets = ["主理人"]
        human_approval_required = input.severity == "critical"

    // === 第四步：记录决策快照 ===
    decision_snapshot = {
        timestamp: CURRENT_TIMESTAMP(),
        failure_type: input.failure_type,
        severity: input.severity,
        action_taken: degradation_action,
        context: input.context,
        reusable_outputs: IDENTIFY_REUSABLE_OUTPUTS(input.failure_type)
    }
    CALL core-state-management-engine.update_snapshot(decision_snapshot)

    // === 第五步：降级策略矩阵检查(L0-L4) ===
    // 检查当前处于哪一级降级
    IF ALL_TOOLS_AVAILABLE() AND PLATFORM_FULL_SUPPORT():
        degradation_level = "L0完整功能"
    ELIF SOME_TOOLS_UNAVAILABLE():
        degradation_level = "L1工具降级"
    ELIF NO_EXTERNAL_SCHEDULING():
        degradation_level = "L2调度降级→纯提示词定时提醒"
    ELIF NO_TEAM_SUPPORT():
        degradation_level = "L3平台降级→Agent型+scenario branches"
    ELSE:
        degradation_level = "L4纯提示词→标注'建议V2部署'"

    // === 第六步：极端场景应对(10类) ===
    IF input.failure_type == "vague_input" AND input.context CONTAINS "全程不确定":
        degradation_action = "使用默认值+标注'默认选择,可后续修改'"
    IF ALL_TOOLS_FAILED():
        degradation_action = "纯提示词兜底+标注'建议V2部署'"
    IF CONSECUTIVE_FAILURES() >= 3:
        PAUSE_TASK()
        UPGRADE_ALERT("连续失败≥3，暂停任务+升级人工审批")
        human_approval_required = true

    // === 第七步：最终断言与输出 ===
    ASSERT degradation_action IS NOT EMPTY
    ASSERT decision_snapshot IS NOT EMPTY

    CALL protocol-quality-gate before final output
    RETURN {degradation_action, decision_snapshot, notification_targets, human_approval_required}
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
