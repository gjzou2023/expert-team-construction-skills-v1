---
name: platform-feishu-adapter
description: 三种集成形态：消息型/交互型/深度集成。生成manifest.yaml+消息卡片模板+审批模板+多维表格Schema+定时触发配置 Use when: 用户说"platform-feishu-adapter、飞书适配器、L3-飞书"等触发词。
---

# 飞书平台适配器

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-feishu-adapter` | **中文名**: 飞书平台适配器 | **英文名**: Feishu Adapter
# 飞书平台适配器 (Feishu Adapter)

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-feishu-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

三种集成形态：消息型/交互型/深度集成。生成manifest.yaml+消息卡片模板+审批模板+多维表格Schema+定时触发配置。

## 触发条件

当检测到以下关键词或场景时自动激活：feishu, feishu, 平台适配, 输出格式

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "architecture": {
      "type": "object",
      "description": "S5架构输出"
    },
    "roles": {
      "type": "array",
      "description": "角色定义列表"
    },
    "sop": {
      "type": "object",
      "description": "SOP定义"
    },
    "expert_type": {
      "type": "string",
      "enum": [
        "team",
        "agent"
      ]
    },
    "track": {
      "type": "string",
      "enum": [
        "fast",
        "standard",
        "strict"
      ]
    }
  },
  "required": [
    "architecture",
    "roles",
    "expert_type"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "output_format": {
      "type": "string",
      "description": "manifest.yaml + 消息卡片模板 + 审批模板 + 多维表格Schema + 定时触发配置"
    },
    "platform_specific_config": {
      "type": "object"
    },
    "degradation_plan": {
      "type": "object"
    }
  },
  "required": [
    "output_format",
    "platform_specific_config"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

目标平台=飞书平台适配器时激活。输出格式：manifest.yaml + 消息卡片模板 + 审批模板 + 多维表格Schema + 定时触发配置。平台特定规则：形态确认(强制确认节点)：仅A→消息通道型;A+B或仅B→交互入口型;含C/D/E/F任一→深度集成型。

## Few-shot 示例

### 示例 1: A型消息通道集成

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "feishu"
  },
  "roles": [
    {"id": "content-publisher", "name": "苏砚", "profession": "内容发布员"}
  ],
  "expert_type": "agent",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "manifest.yaml + 消息卡片模板 + 定时触发配置",
  "platform_specific_config": {
    "integration_type": "消息通道型",
    "decision": "仅含A→消息通道型，生成manifest.yaml定义飞书应用基础信息，生成消息卡片模板用于内容推送"
  },
  "generated_files": [
    "manifest.yaml: app名称=内容助手,描述=定时推送内容摘要到飞书群",
    "message_card_template.json: 内容卡片含标题/摘要/链接/封面图",
    "schedule_trigger.yaml: 每工作日09:00触发内容推送"
  ]
}
```

### 示例 2: 深度集成型(含审批+多维表格)

**输入**:
```json
{
  "architecture": {
    "domain_type": "F",
    "platform": "feishu"
  },
  "roles": [
    {"id": "project-manager", "name": "方策", "profession": "项目经理"},
    {"id": "quality-inspector", "name": "严谨", "profession": "质检员"}
  ],
  "expert_type": "team",
  "track": "strict"
}
```

**输出**:
```json
{
  "output_format": "manifest.yaml + 消息卡片模板 + 审批模板 + 多维表格Schema + 定时触发配置",
  "platform_specific_config": {
    "integration_type": "深度集成型",
    "decision": "含F→深度集成型，生成审批模板(质检流)+多维表格Schema(项目跟踪)",
    "approval_template": "质检审批流程:提交→质检员审核→项目经理终批",
    "bitable_schema": "项目表字段:项目名/负责人/状态/截止日期/质检结果"
  }
}
```

### 示例 3: 快速通道消息型

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "feishu",
    "role_count": 1
  },
  "roles": [
    {"id": "daily-summary", "name": "简闻", "profession": "摘要生成员"}
  ],
  "expert_type": "agent",
  "track": "fast"
}
```

**输出**:
```json
{
  "status": "simplified",
  "output_format": "manifest.yaml + 消息卡片模板",
  "integration_type": "消息通道型(简化版)",
  "generated_files": [
    "manifest.yaml: 仅定义app基础信息",
    "message_card_template.json: 简化卡片仅含标题+正文"
  ],
  "degradation_plan": {
    "strategy": "省略审批模板和多维表格Schema,仅保留消息推送能力"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://platform/platform-feishu-adapter/format-spec` — 飞书平台适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## 详细执行逻辑

```text
FUNCTION execute_platform_feishu_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: 形态确认(强制确认节点)
    domain_type = input.architecture.domain_type
    // E型已改为A-F组合标记，此处检查features中不再含E
    IF domain_type == "A" AND NOT CONTAINS_ANY(input.architecture.features, ["B","C","D","F"]):
        integration_type = "消息通道型"
    ELIF CONTAINS_ANY(input.architecture.features, ["B"]) OR (domain_type == "A" AND CONTAINS(input.architecture.features, "B")):
        integration_type = "交互入口型"
    ELIF CONTAINS_ANY(input.architecture.features, ["C","D","E","F"]):
        integration_type = "深度集成型"
    ASSERT integration_type IN ["消息通道型", "交互入口型", "深度集成型"]

    // 阶段3: 生成manifest.yaml(飞书应用基础配置)
    manifest = {
        "app_name": GENERATE_APP_NAME(input.architecture),
        "description": GENERATE_APP_DESCRIPTION(input.architecture),
        "permissions": SELECT_PERMISSIONS(integration_type),
        "event_subscriptions": []
    }
    // 事件订阅配置
    IF integration_type IN ["交互入口型", "深度集成型"]:
        APPEND manifest.event_subscriptions, "im.message.receive_v1"
        APPEND manifest.event_subscriptions, "bot.join_chat_v1"
    IF integration_type == "深度集成型":
        APPEND manifest.event_subscriptions, "approval_instance.created_v1"
        APPEND manifest.event_subscriptions, "bitable.record.changed_v1"

    // 阶段4: 生成消息卡片模板
    card_templates = []
    FOR EACH role IN input.roles:
        card = BUILD_MESSAGE_CARD(role, input.architecture)
        IF integration_type == "消息通道型" AND input.track == "fast":
            // 简化卡片仅含标题+正文
            card = SIMPLIFY_CARD(card, fields=["title", "content"])
        ELIF integration_type == "深度集成型":
            // 完整卡片含标题/摘要/链接/封面图/操作按钮
            card = ENRICH_CARD(card, additional_fields=["actions", "images", "links"])
        APPEND card_templates, card

    // 阶段5: 深度集成型专属组件
    approval_templates = []
    bitable_schemas = []
    IF integration_type == "深度集成型":
        // 5a: 生成审批模板
        IF CONTAINS_ANY(input.architecture.features, ["F"]):
            approval_flow = BUILD_APPROVAL_TEMPLATE(input.roles, domain_type)
            // 审批流程:提交→质检员审核→项目经理终批
            ASSERT LEN(approval_flow.steps) >= 2
            APPEND approval_templates, approval_flow

        // 5b: 生成多维表格Schema
        IF CONTAINS_ANY(input.architecture.features, ["D", "F"]):
            bitable_schema = BUILD_BITABLE_SCHEMA(input.architecture, input.roles)
            // 项目表字段:项目名/负责人/状态/截止日期/质检结果
            ASSERT LEN(bitable_schema.fields) >= 5
            APPEND bitable_schemas, bitable_schema

    // 阶段6: 定时触发配置
    schedule_config = NULL
    IF input.sop.has_schedule_trigger:
        schedule_config = {
            "type": "cron",
            "expression": EXTRACT_CRON(input.sop.schedule),
            "action": "trigger_bot_message"
        }

    // 阶段7: 机器人指令注册
    bot_commands = []
    FOR EACH role IN input.roles:
        cmd = GENERATE_BOT_COMMAND(role)
        APPEND bot_commands, cmd

    // 阶段8: 快速通道降级
    IF input.track == "fast":
        // 省略审批模板和多维表格Schema,仅保留消息推送能力
        approval_templates = []
        bitable_schemas = []

    // 阶段9: 质量门控
    CALL protocol_quality_gate(manifest, card_templates, approval_templates, bitable_schemas)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": "manifest.yaml + 消息卡片模板 + " +
            (LEN(approval_templates) > 0 ? "审批模板 + " : "") +
            (LEN(bitable_schemas) > 0 ? "多维表格Schema + " : "") +
            "定时触发配置",
        "platform_specific_config": {
            "integration_type": integration_type,
            "manifest": manifest,
            "approval_templates": approval_templates,
            "bitable_schemas": bitable_schemas,
            "bot_commands": bot_commands
        }
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
