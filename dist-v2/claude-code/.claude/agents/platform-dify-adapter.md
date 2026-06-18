---
name: platform-dify-adapter
description: 使用Dify Workflow的Schedule Trigger;独立映射表。 Use when: 用户说"platform-dify-adapter、Dify适配器、L3-Dify"等触发词。
tools: Read, Write
---

# Dify平台适配器

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-dify-adapter` | **中文名**: Dify平台适配器 | **英文名**: Dify Adapter
# Dify平台适配器 (Dify Adapter)

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-dify-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

使用Dify Workflow的Schedule Trigger;独立映射表。

## 触发条件

当检测到以下关键词或场景时自动激活：dify, dify, 平台适配, 输出格式

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
      "description": "Dify Workflow配置 + Schedule Trigger定义"
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

目标平台=Dify平台适配器时激活。输出格式：Dify Workflow配置 + Schedule Trigger定义。平台特定规则：使用Dify Workflow的Schedule Trigger;独立映射表。

## Few-shot 示例

### 示例 1: Dify多Agent工作流编排

**输入**:
```json
{
  "architecture": {
    "domain_type": "D",
    "platform": "dify"
  },
  "roles": [
    {"id": "strategist", "name": "林语", "profession": "策略分析师"},
    {"id": "executor", "name": "知行", "profession": "执行Agent"}
  ],
  "expert_type": "team",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "Dify Workflow配置 + Schedule Trigger定义",
  "platform_specific_config": {
    "workflow": {
      "trigger": {"type": "schedule", "cron": "0 9 * * 1-5"},
      "nodes": [
        {"id": "strategy", "agent": "strategist", "output": "策略方案"},
        {"id": "execute", "agent": "executor", "input": "策略方案", "output": "执行结果"}
      ]
    },
    "schedule_trigger": "每工作日09:00通过Dify Workflow的Schedule Trigger启动",
    "independent_mapping": "使用独立映射表保持Agent间数据流转"
  }
}
```

### 示例 2: 强监管领域(合规审查节点)

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "dify",
    "regulated": true
  },
  "roles": [
    {"id": "medical-writer", "name": "陈济", "profession": "医学撰稿人"}
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
  "blocked_reason": "医疗领域内容须先通过合规引擎审查后才能进入Dify Workflow",
  "workflow_insertion": "在Schedule Trigger后插入人工审查节点(Code节点调用合规API)"
}
```

### 示例 3: 快速通道简单Workflow

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "dify",
    "role_count": 1
  },
  "roles": [
    {"id": "daily-reporter", "name": "简闻", "profession": "日报员"}
  ],
  "expert_type": "agent",
  "track": "fast"
}
```

**输出**:
```json
{
  "status": "simplified",
  "output_format": "Dify Workflow配置(Schedule Trigger单节点)",
  "generated_files": [
    "dify_workflow.yml: Schedule Trigger→LLM节点(日报生成)→HTTP节点(推送到飞书)"
  ],
  "degradation_plan": {
    "strategy": "单节点简化Workflow,省略多Agent编排和映射表"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://platform/platform-dify-adapter/format-spec` — Dify平台适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## 详细执行逻辑

```text
FUNCTION execute_platform_dify_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: 初始化Dify DSL结构
    dify_dsl_version = "1.0.0"
    app_mode = DETERMINE_APP_MODE(input.expert_type, input.roles)
    // app_mode: "workflow"(多Agent编排) 或 "chat"(单Agent对话)

    // 阶段3: 构建Dify Workflow节点
    workflow_nodes = []

    // 3a: Schedule Trigger定义
    IF input.sop.has_schedule_trigger:
        schedule_node = {
            "type": "schedule-trigger",
            "cron": EXTRACT_CRON(input.sop.schedule),
            "timezone": "Asia/Shanghai"
        }
        APPEND workflow_nodes, schedule_node

    // 3b: LLM节点(每个角色对应一个)
    agent_mapping_table = {}  // 独立映射表
    FOR EACH role IN input.roles:
        agent_id = GENERATE_kebab_case(role.profession)
        llm_node = {
            "type": "llm",
            "id": "agent_" + agent_id,
            "model": SELECT_DIFY_MODEL(input.track),
            "prompt": BUILD_AGENT_PROMPT(role, input.sop),
            "memory": {"type": "conversation", "size": 10},
            "tools": SELECT_DIFY_TOOLS(role)
        }
        APPEND workflow_nodes, llm_node
        // 独立映射表:记录Agent间数据流转关系
        agent_mapping_table[agent_id] = {
            "input_from": DETERMINE_INPUT_SOURCE(role, workflow_nodes),
            "output_to": DETERMINE_OUTPUT_TARGET(role, input.roles),
            "data_schema": BUILD_DATA_SCHEMA(role)
        }

    // 3c: 知识库节点
    knowledge_nodes = []
    FOR EACH role IN input.roles:
        IF role.requires_knowledge_base:
            kb_node = {
                "type": "knowledge-retrieval",
                "dataset_id": SELECT_DIFY_DATASET(role.profession),
                "query_variable": "agent_" + agent_id + ".output"
            }
            APPEND workflow_nodes, kb_node
            APPEND knowledge_nodes, kb_node

    // 3d: 工具集成节点
    tool_nodes = []
    IF input.architecture.has_external_tools:
        FOR EACH tool IN input.architecture.tools:
            tool_node = {
                "type": "tool",
                "provider": tool.provider,
                "action": tool.action,
                "credentials": {"type": "dify_credential", "id": tool.credential_id}
            }
            APPEND workflow_nodes, tool_node
            APPEND tool_nodes, tool_node

    // 阶段4: 合规审查节点(强监管插入)
    IF input.architecture.regulated == true:
        // 在Schedule Trigger后插入人工审查节点(Code节点调用合规API)
        compliance_node = {
            "type": "code",
            "id": "compliance_check",
            "code": "CALL compliance_api(input)",
            "position": AFTER_TRIGGER,
            "on_fail": "block_and_notify"
        }
        INSERT_AFTER(workflow_nodes, schedule_node, compliance_node)

    // 阶段5: 构建完整Dify DSL YAML
    dify_dsl = {
        "version": dify_dsl_version,
        "kind": "app",
        "app": {
            "mode": app_mode,
            "name": GENERATE_APP_NAME(input.architecture),
            "description": GENERATE_APP_DESCRIPTION(input.architecture)
        },
        "workflow": {
            "nodes": workflow_nodes,
            "edges": BUILD_WORKFLOW_EDGES(workflow_nodes, agent_mapping_table)
        },
        "agent_mapping": agent_mapping_table
    }

    // 阶段6: 快速通道降级
    IF input.track == "fast":
        // 单节点简化Workflow,省略多Agent编排和映射表
        dify_dsl.workflow.nodes = [schedule_node, workflow_nodes[FIRST_LLM_INDEX]]
        dify_dsl.agent_mapping = NULL

    // 阶段7: 质量门控
    CALL protocol_quality_gate(dify_dsl)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": "Dify Workflow配置 + Schedule Trigger定义",
        "platform_specific_config": {
            "dify_dsl": dify_dsl,
            "schedule_trigger": input.sop.has_schedule_trigger,
            "independent_mapping": agent_mapping_table
        },
        "degradation_plan": {"fast": "单节点简化Workflow,省略多Agent编排和映射表"}
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
