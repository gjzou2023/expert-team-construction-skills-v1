---
name: platform-coze-adapter
description: Token限制;使用Coze工作流的定时/Webhook触发器。 Use when: 用户说"platform-coze-adapter、Coze适配器、L3-Coze"等触发词。
---

# Coze平台适配器

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-coze-adapter` | **中文名**: Coze平台适配器 | **英文名**: Coze Adapter
# Coze平台适配器 (Coze Adapter)

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-coze-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

Token限制;使用Coze工作流的定时/Webhook触发器。

## 触发条件

当检测到以下关键词或场景时自动激活：coze, coze, 平台适配, 输出格式

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
      "description": "Coze Bot配置 + 工作流定义"
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

目标平台=Coze平台适配器时激活。输出格式：Coze Bot配置 + 工作流定义。平台特定规则：Token限制;使用Coze工作流的定时/Webhook触发器。

## Few-shot 示例

### 示例 1: Token感知的Coze Bot生成

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "coze"
  },
  "roles": [
    {"id": "content-bot", "name": "苏砚", "profession": "内容Bot"},
    {"id": "publisher-bot", "name": "知言", "profession": "发布Bot"}
  ],
  "expert_type": "team",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "Coze Bot配置 + 工作流定义",
  "platform_specific_config": {
    "bot_configs": [
      "content-bot: Prompt限制在Coze Token上限内,分段输出长内容",
      "publisher-bot: 使用Coze工作流的定时/Webhook触发器自动发布"
    ],
    "workflow_definition": {
      "trigger": "Schedule Trigger:每工作日09:00",
      "nodes": [
        "Bot(content-bot)→内容生成",
        "Bot(publisher-bot)→格式化→定时发布"
      ]
    }
  }
}
```

### 示例 2: 强监管领域(合规+Token约束)

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "coze",
    "regulated": true
  },
  "roles": [
    {"id": "health-bot", "name": "陈济", "profession": "健康Bot"}
  ],
  "expert_type": "agent",
  "track": "strict"
}
```

**输出**:
```json
{
  "status": "blocked_or_review",
  "required_call": "protocol-compliance-engine",
  "blocked_reason": "医疗领域触发合规引擎审查+Coze Token限制需分段输出",
  "next_action": "审查通过后生成Coze Bot配置,每段输出添加免责声明"
}
```

### 示例 3: 快速通道简单Bot

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "coze",
    "role_count": 1
  },
  "roles": [
    {"id": "daily-bot", "name": "简闻", "profession": "日报Bot"}
  ],
  "expert_type": "agent",
  "track": "fast"
}
```

**输出**:
```json
{
  "status": "simplified",
  "output_format": "Coze Bot配置",
  "generated_files": [
    "daily-bot-config.json: Prompt在Token限制内,使用Webhook触发器每日推送"
  ],
  "degradation_plan": {
    "strategy": "省略复杂工作流定义,单Bot+Webhook触发即可"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://platform/platform-coze-adapter/format-spec` — Coze平台适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## 详细执行逻辑

```text
FUNCTION execute_platform_coze_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: Token限制感知
    COZE_TOKEN_LIMIT = GET_COZE_TOKEN_LIMIT(input.architecture)
    // Coze平台Token上限,需分段输出长内容

    // 阶段3: 为每个角色生成Coze Bot配置
    bot_configs = []
    FOR EACH role IN input.roles:
        bot_id = GENERATE_kebab_case(role.profession)
        ASSERT MATCH(bot_id, /^[a-z][a-z0-9-]*$/)

        // 3a: 构建Bot Prompt(Token限制内)
        full_prompt = BUILD_FULL_PROMPT(role, input.sop, input.architecture)
        IF LEN(full_prompt) > COZE_TOKEN_LIMIT:
            // Prompt超限→分段输出
            segmented_prompts = SEGMENT_PROMPT(full_prompt, COZE_TOKEN_LIMIT)
            prompt_config = {
                "type": "segmented",
                "segments": segmented_prompts,
                "total_segments": LEN(segmented_prompts)
            }
        ELSE:
            prompt_config = {"type": "single", "prompt": full_prompt}

        // 3b: 知识库挂载
        knowledge_bases = []
        IF role.requires_knowledge_base:
            kb_config = {
                "type": "coze_knowledge_base",
                "dataset_id": SELECT_KNOWLEDGE_BASE(role.profession),
                "retrieval_strategy": "hybrid"
            }
            APPEND knowledge_bases, kb_config

        // 3c: 构建完整Bot配置JSON
        bot_config = {
            "bot_id": bot_id,
            "bot_name": role.name,
            "prompt_config": prompt_config,
            "knowledge_bases": knowledge_bases,
            "model": SELECT_COZE_MODEL(input.track)
        }

        // 3d: 强监管领域:每段输出添加免责声明
        IF input.architecture.regulated == true:
            bot_config.disclaimer = BUILD_DISCLAIMER(input.architecture.domain_type)
            bot_config.compliance_check = true

        APPEND bot_configs, bot_config

    // 阶段4: 工作流定义(多Bot编排)
    IF input.expert_type == "team":
        // 使用Coze工作流编排多Bot协作
        workflow_definition = {
            "type": "coze_workflow",
            "nodes": [],
            "connections": []
        }

        // 4a: 触发器配置(定时/Webhook)
        IF input.sop.has_schedule_trigger:
            trigger = {
                "type": "Schedule Trigger",
                "cron": EXTRACT_CRON(input.sop.schedule),
                "description": "每工作日定时触发"
            }
        ELIF input.architecture.has_webhook:
            trigger = {
                "type": "Webhook Trigger",
                "url": input.architecture.webhook_url,
                "method": "POST"
            }
        APPEND workflow_definition.nodes, {"id": "trigger", "config": trigger}

        // 4b: Bot调用节点链
        FOR i FROM 0 TO LEN(bot_configs) - 1:
            node = {
                "id": "bot_" + bot_configs[i].bot_id,
                "type": "Bot",
                "config": {"bot_id": bot_configs[i].bot_id},
                "input_from": (i == 0) ? "trigger" : "bot_" + bot_configs[i-1].bot_id
            }
            APPEND workflow_definition.nodes, node
            APPEND workflow_definition.connections, {
                "from": node.input_from, "to": node.id
            }

    // 阶段5: 快速通道降级
    IF input.track == "fast":
        // 省略复杂工作流定义,单Bot+Webhook触发即可
        workflow_definition = NULL
        bot_configs = [bot_configs[0]]  // 仅保留第一个Bot

    // 阶段6: 质量门控
    CALL protocol_quality_gate(bot_configs, workflow_definition)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": "Coze Bot配置" +
            (workflow_definition != NULL ? " + 工作流定义" : ""),
        "platform_specific_config": {
            "bot_configs": bot_configs,
            "workflow_definition": workflow_definition,
            "token_limit": COZE_TOKEN_LIMIT
        },
        "degradation_plan": {"fast": "省略复杂工作流定义,单Bot+Webhook触发即可"}
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
