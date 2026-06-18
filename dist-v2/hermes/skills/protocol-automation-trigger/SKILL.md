---
name: protocol-automation-trigger
description: D型/F型/E型(含D/F)强制激活。定义触发类型(定时/事件/条件)，填写触发需求声明表(12必填字段)，触发间依赖编排(DAG)。快速通道跳过，纯提示词降级 Use when: 用户说"protocol-automation-trigger、自动化触发协议、L2自动化"等触发词。
version: 1.1.0
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
# 自动化触发设计

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-automation-trigger` | **中文名**: 自动化触发设计 | **英文名**: Automation Trigger Design
# 自动化触发设计 (Automation Trigger Design)

> **层级**: L2 | **版本**: 1.0.0 | **ID**: `protocol-automation-trigger`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

D型/F型/E型(含D/F)强制激活。定义触发类型(定时/事件/条件)，填写触发需求声明表(12必填字段)，触发间依赖编排(DAG)。快速通道跳过，纯提示词降级。

## 触发条件

当检测到以下关键词或场景时自动激活：定时, 自动化, 触发, 调度, cron, DAG, 5.9

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "domain_type": {
      "type": "string",
      "enum": [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F"
      ]
    },
    "platform": {
      "type": "string"
    },
    "sop_phases": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "domain_type",
    "platform"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "triggers": {
      "type": "array",
      "items": {
        "type": "object"
      }
    },
    "trigger_dag": {
      "type": "string"
    },
    "platform_adaptation": {
      "type": "string"
    },
    "monitoring_metrics": {
      "type": "array",
      "items": {
        "type": "object"
      }
    }
  },
  "required": [
    "triggers",
    "trigger_dag",
    "platform_adaptation"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)定义触发类型(定时/事件/条件)→(2)填写触发需求声明表→(3)触发间依赖编排(DAG)→(4)按平台适配调度能力→(5)无工具时纯提示词降级→(6)纳入调度监控指标。触发需求声明表必填字段(12)：触发名称+类型+条件/周期+执行角色+执行模式+传递数据+输出去向+人工确认+失败策略+超时阈值+幂等性保障+纯提示词降级。依赖失败传播：前置失败→blocked;前置超时→等待1.5×超时;前置跳过→输入缺失兜底。平台调度能力：WorkBuddy:Automation+MCP;Codex:需外部crontab;Hermes:内置定时+消息监听;Coze:定时/Webhook触发器;Dify:Schedule Trigger;飞书:自动化+事件订阅;n8n:Cron+Webhook+IF/Switch;无工具:纯提示词降级。

## Few-shot 示例

### 示例 1：正常流程 — D型数据自动化触发编排

**输入**:
```json
{
  "domain_type": "D",
  "platform": "workbuddy",
  "sop_phases": ["数据采集", "数据清洗", "报告生成"]
}
```

**输出**:
```json
{
  "triggers": [
    {
      "name": "daily_data_collection",
      "type": "scheduled",
      "schedule": "0 9 * * *",
      "executor": "data-collector",
      "execution_mode": "full_auto",
      "approval": "full_auto",
      "failure_strategy": "retry_3_times",
      "timeout": "300s",
      "idempotency": true,
      "depends_on": [],
      "degradation": "手动触发+提醒"
    }
  ],
  "trigger_dag": "A[数据采集@9:00] --> B[数据清洗@9:05] --> C[报告生成@9:15]",
  "platform_adaptation": "WorkBuddy Automation+MCP定时触发",
  "monitoring_metrics": [
    { "name": "执行成功率", "healthy": "≥90%", "alert": "<70%", "action": "暂停+告警" },
    { "name": "调度偏移量", "healthy": "≤30秒", "alert": ">30秒", "action": "校准cron" }
  ]
}
```

### 示例 2：异常流程 — 工具不可用降级为纯提示词

**输入**:
```json
{
  "domain_type": "D",
  "platform": "codex",
  "sop_phases": ["数据采集", "分析", "输出"]
}
```

**输出**:
```json
{
  "triggers": [
    {
      "name": "manual_data_collection",
      "type": "manual",
      "schedule": "纯提示词定时提醒",
      "executor": "用户手动",
      "execution_mode": "manual_with_reminder",
      "approval": "manual",
      "failure_strategy": "用户自行判断",
      "timeout": "无",
      "idempotency": false,
      "depends_on": [],
      "degradation": "L2调度降级：Codex无内置调度→纯提示词定时提醒用户手动触发"
    }
  ],
  "trigger_dag": "A[手动采集] --> B[手动分析] --> C[手动输出]",
  "platform_adaptation": "L2调度降级：Codex需外部crontab，不可用则纯提示词提醒",
  "monitoring_metrics": [
    { "name": "执行成功率", "healthy": "≥90%", "alert": "<70%", "note": "手动执行模式，成功率依赖用户" }
  ]
}
```

### 示例 3：快速通道 — 跳过自动化编排

**输入**:
```json
{
  "domain_type": "A",
  "platform": "workbuddy",
  "sop_phases": ["内容创作"],
  "channel": "fast"
}
```

**输出**:
```json
{
  "triggers": [],
  "trigger_dag": "无自动化触发：A型快速通道跳过自动化编排",
  "platform_adaptation": "快速通道：无需自动化触发，用户按需手动执行",
  "monitoring_metrics": [
    { "name": "执行成功率", "healthy": "N/A", "alert": "N/A", "note": "快速通道不启用自动化监控" }
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://automation/platform-scheduling-map` — 各平台调度能力映射

## 依赖关系

- `core-mental-model-engine`

## 调度监控指标

| 指标 | 健康线 | 告警线 | 处理动作 |
| --- | --- | --- | --- |
| 执行成功率 | ≥90% | <70%告警 | 复查失败策略+暂停连续失败任务 |
| 平均执行时长 | 不高于预估1.2倍 | 超过1.5倍告警 | 调整超时阈值或触发降级 |
| 调度偏移量 | ≤30秒 | 偏移>30秒告警 | 检查平台调度能力+校准触发时间 |
| 连续失败计数 | <3次 | ≥3次暂停任务 | 升级人工审批+排查根因 |
| 依赖阻塞率 | ≤5% | >5%告警 | 检查DAG前置任务+解锁阻塞链路 |

## 详细执行逻辑

```text
FUNCTION execute_protocol_automation_trigger(input):
    ASSERT input.domain_type IN ["A","B","C","D","E","F"]
    ASSERT input.platform IS NOT EMPTY

    // === 第一步：触发类型识别与强制激活判断 ===
    FORCE_ACTIVATE_TYPES = ["D","F"]  // D型/F型强制激活
    IF input.domain_type == "E":
        // E型含D/F子类型时强制激活
        sub_types = IDENTIFY_SUB_TYPES(input)
        IF "D" IN sub_types OR "F" IN sub_types:
            FORCE_ACTIVATE_TYPES = FORCE_ACTIVATE_TYPES + ["E"]

    is_force_activate = input.domain_type IN FORCE_ACTIVATE_TYPES

    // 快速通道跳过
    IF input.channel == "fast" AND NOT is_force_activate:
        RETURN {triggers: [], trigger_dag: "快速通道跳过自动化编排", platform_adaptation: "无需自动化触发", monitoring_metrics: []}

    // === 第二步：触发器设计(§5.9) ===
    // 三种触发类型：定时/事件/条件
    triggers = []
    FOR phase IN input.sop_phases:
        trigger = {}
        trigger.name = GENERATE_TRIGGER_NAME(phase)

        // 识别触发类型
        IF phase CONTAINS "每日" OR phase CONTAINS "定时":
            trigger.type = "scheduled"
            trigger.schedule = EXTRACT_CRON(phase)
        ELIF phase CONTAINS "事件" OR phase CONTAINS "监听":
            trigger.type = "event"
            trigger.event_source = EXTRACT_EVENT_SOURCE(phase)
        ELSE:
            trigger.type = "condition"
            trigger.condition = EXTRACT_CONDITION(phase)

        // === 填写触发需求声明表(12必填字段) ===
        trigger.executor = IDENTIFY_EXECUTOR_ROLE(phase)
        trigger.execution_mode = DETERMINE_EXECUTION_MODE(trigger.type)
        trigger.pass_data = IDENTIFY_PASS_DATA(phase)
        trigger.output_target = IDENTIFY_OUTPUT_TARGET(phase)
        trigger.human_approval = DETERMINE_APPROVAL_NEED(trigger.type, input.domain_type)
        trigger.failure_strategy = "retry_3_times"
        trigger.timeout = ESTIMATE_TIMEOUT(phase)
        trigger.idempotency = true
        trigger.degradation = "手动触发+提醒"  // 纯提示词降级

        APPEND triggers WITH trigger

    // === 第三步：触发间依赖编排(DAG) ===
    trigger_dag = ""
    FOR i FROM 0 TO LENGTH(triggers) - 1:
        IF i == 0:
            trigger_dag = triggers[i].name + "@" + triggers[i].schedule
        ELSE:
            trigger_dag = trigger_dag + " --> " + triggers[i].name + "@" + triggers[i].schedule

        // 依赖失败传播规则
        IF i > 0:
            triggers[i].depends_on = [triggers[i-1].name]
            // 前置失败→blocked; 前置超时→等待1.5×超时; 前置跳过→输入缺失兜底
            triggers[i].on_predecessor_failure = "blocked"
            triggers[i].on_predecessor_timeout = "WAIT_1.5X_TIMEOUT"
            triggers[i].on_predecessor_skip = "USE_FALLBACK_INPUT"

    // === 第四步：WorkBuddy Automation配置适配 ===
    platform_adaptation = ""
    IF input.platform == "workbuddy":
        // WorkBuddy: Automation+MCP
        platform_adaptation = "WorkBuddy Automation+MCP定时触发"
        FOR trigger IN triggers:
            IF trigger.type == "scheduled":
                // 生成WorkBuddy Automation配置
                automation_config = {}
                automation_config.scheduleType = "recurring"
                automation_config.rrule = CONVERT_TO_RRULE(trigger.schedule)
                automation_config.prompt = trigger.executor + ": 执行" + trigger.name
                automation_config.connectorIds = IDENTIFY_MCP_CONNECTORS(trigger)
        // 快速通道降级
        IF input.channel == "fast":
            platform_adaptation = "快速通道：按需手动执行，无需Automation配置"

    ELIF input.platform == "codex":
        platform_adaptation = "L2调度降级：Codex需外部crontab，不可用则纯提示词提醒"
    ELIF input.platform == "hermes":
        platform_adaptation = "Hermes内置定时+消息监听"
    ELIF input.platform == "coze":
        platform_adaptation = "Coze定时/Webhook触发器"
    ELIF input.platform == "dify":
        platform_adaptation = "Dify Schedule Trigger"
    ELIF input.platform == "feishu":
        platform_adaptation = "飞书自动化+事件订阅"
    ELIF input.platform == "n8n":
        platform_adaptation = "n8n Cron+Webhook+IF/Switch"
    ELSE:
        // 无工具时纯提示词降级
        platform_adaptation = "L4纯提示词降级：全部使用提示词实现定时提醒，标注'建议V2部署'"

    // === 第五步：调度监控指标(§5.9.6) ===
    monitoring_metrics = [
        {name: "执行成功率", healthy: "≥90%", alert: "<70%", action: "暂停+告警+复查失败策略"},
        {name: "平均执行时长", healthy: "≤预估1.2倍", alert: ">1.5倍", action: "调整超时阈值或触发降级"},
        {name: "调度偏移量", healthy: "≤30秒", alert: ">30秒", action: "检查平台调度能力+校准触发时间"},
        {name: "连续失败计数", healthy: "<3次", alert: "≥3次", action: "升级人工审批+排查根因"},
        {name: "依赖阻塞率", healthy: "≤5%", alert: ">5%", action: "检查DAG前置任务+解锁阻塞链路"}
    ]

    // === 第六步：最终断言与输出 ===
    ASSERT LENGTH(triggers) > 0 OR input.channel == "fast"
    ASSERT trigger_dag IS NOT EMPTY
    ASSERT platform_adaptation IS NOT EMPTY

    CALL protocol-quality-gate before final output
    RETURN {triggers, trigger_dag, platform_adaptation, monitoring_metrics}
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
