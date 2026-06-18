---
name: platform-n8n-adapter
id: "platform-n8n-adapter"
layer: "L3"
name_zh: "n8n工作流引擎适配器"
name_en: "n8n Adapter"
version: "1.0.0"
description: 双角色：调度器(定时触发+事件监听)/执行引擎(工作流模板执行)。D型深度集成。
agent_created: true
trigger_keywords: ["platform-n8n-adapter", "n8n适配器", "L3-n8n"]
dependencies: ["pipeline-s7-expert-package-generation"]
---

# n8n工作流引擎适配器 (n8n Adapter)

> **层级**: L3 | **版本**: 1.0.0 | **ID**: `platform-n8n-adapter`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

双角色：调度器(定时触发+事件监听)/执行引擎(工作流模板执行)。D型深度集成。

## 触发条件

当检测到以下关键词或场景时自动激活：n8n, n8n, 平台适配, 输出格式

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
      "description": "工作流模板JSON + 集成接口规范 + D型深度集成配置"
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

目标平台=n8n工作流引擎适配器时激活。输出格式：工作流模板JSON + 集成接口规范 + D型深度集成配置。平台特定规则：n8n双重角色判断：'调度器'定时/事件触发→调用AI Agent;'执行引擎'D型核心管道。无实例降级：纯提示词(用户手动触发)。

## Few-shot 示例

### 示例 1: n8n调度器+D型执行管道

**输入**:
```json
{
  "architecture": {
    "domain_type": "D",
    "platform": "n8n"
  },
  "roles": [
    {"id": "data-processor", "name": "楚恒", "profession": "数据工程师"},
    {"id": "ai-analyst", "name": "知微", "profession": "AI分析师"}
  ],
  "expert_type": "team",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "工作流模板JSON + 集成接口规范 + D型深度集成配置",
  "platform_specific_config": {
    "scheduler_role": "n8n Cron节点:每2小时触发数据拉取→调用AI Agent分析",
    "executor_role": "D型核心管道:数据预处理→AI分析→结果持久化→通知分发",
    "workflow_nodes": [
      "Cron Trigger: 0 */2 * * *",
      "HTTP Request: 拉取原始数据",
      "AI Agent: 调用知微分析",
      "Database: 存储分析结果",
      "HTTP Request: 推送结论到下游"
    ]
  }
}
```

### 示例 2: 纯调度器模式(A型内容推送)

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "n8n"
  },
  "roles": [
    {"id": "content-scheduler", "name": "苏砚", "profession": "内容调度员"}
  ],
  "expert_type": "agent",
  "track": "standard"
}
```

**输出**:
```json
{
  "output_format": "工作流模板JSON + 集成接口规范",
  "platform_specific_config": {
    "scheduler_role": "n8n定时触发+Cron触发器→调用内容生成AI→飞书推送",
    "workflow_nodes": [
      "Schedule Trigger: 每日09:00",
      "Webhook: 调用AI内容生成接口",
      "HTTP Request: 推送到飞书"
    ]
  }
}
```

### 示例 3: 无实例降级(纯提示词)

**输入**:
```json
{
  "architecture": {
    "domain_type": "A",
    "platform": "n8n",
    "no_n8n_instance": true
  },
  "roles": [
    {"id": "manual-executor", "name": "安之", "profession": "手动执行员"}
  ],
  "expert_type": "agent",
  "track": "fast"
}
```

**输出**:
```json
{
  "status": "degraded",
  "output_format": "纯提示词工作流描述(用户手动触发)",
  "degradation_plan": {
    "strategy": "输出工作流伪代码+步骤说明，用户须自行在n8n中手动搭建"
  },
  "generated_files": [
    "workflow_pseudocode.md: 详细步骤+节点配置参数",
    "manual_setup_guide.md: n8n手动搭建操作指南"
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://platform/platform-n8n-adapter/format-spec` — n8n工作流引擎适配器格式规范

## 依赖关系

- `pipeline-s7-expert-package-generation`

## 详细执行逻辑

```text
FUNCTION execute_platform_n8n_adapter(input):
    ASSERT input matches input_schema
    ASSERT input.architecture != NULL
    ASSERT input.roles != NULL AND LEN(input.roles) >= 1

    // 阶段1: 合规前置检查
    CALL protocol_compliance_engine(input.architecture.domain_type, input.track)
    IF compliance_result.status == "blocked":
        RETURN {"status": "blocked_or_review", "required_call": "protocol-compliance-engine"}

    // 阶段2: 双角色判断(调度器/执行引擎)
    domain_type = input.architecture.domain_type
    IF domain_type == "D":
        role_mode = "executor"  // D型核心管道:执行引擎
    ELIF domain_type == "A" AND NOT input.architecture.has_deep_integration:
        role_mode = "scheduler"  // A型内容推送:调度器
    ELSE:
        role_mode = "both"  // 双角色兼具

    // 阶段3: n8n实例可用性检查
    n8n_available = CHECK_N8N_INSTANCE(input.architecture)
    IF NOT n8n_available:
        // 无实例降级:纯提示词(用户手动触发)
        pseudocode = GENERATE_WORKFLOW_PSEUDOCODE(input.roles, input.sop)
        setup_guide = GENERATE_MANUAL_SETUP_GUIDE(input.roles)
        RETURN {
            "status": "degraded",
            "output_format": "纯提示词工作流描述(用户手动触发)",
            "generated_files": ["workflow_pseudocode.md", "manual_setup_guide.md"],
            "degradation_plan": {"strategy": "输出工作流伪代码+步骤说明,用户须自行在n8n中手动搭建"}
        }

    // 阶段4: 构建工作流节点
    workflow_nodes = []

    // 4a: 触发器节点
    IF role_mode == "scheduler" OR role_mode == "both":
        // 定时触发:Cron节点
        cron_expression = EXTRACT_CRON(input.sop.schedule)
        trigger_node = BUILD_CRON_NODE(cron_expression)
        APPEND workflow_nodes, trigger_node

        // 事件监听:Webhook节点
        IF input.architecture.has_webhook_trigger:
            webhook_node = BUILD_WEBHOOK_NODE(input.architecture.webhook_path)
            APPEND workflow_nodes, webhook_node

    // 4b: AI Agent调用节点
    IF role_mode == "scheduler":
        // 调度器模式:调用AI Agent分析
        FOR EACH role IN input.roles:
            agent_node = BUILD_AI_AGENT_NODE(role, "call_external")
            APPEND workflow_nodes, agent_node
    ELIF role_mode == "executor":
        // 执行引擎模式:D型核心管道
        pipeline_nodes = BUILD_EXECUTION_PIPELINE(input.roles, input.sop)
        // 管道:数据预处理→AI分析→结果持久化→通知分发
        ASSERT LEN(pipeline_nodes) >= 3
        APPEND workflow_nodes, pipeline_nodes

    // 4c: 数据处理节点
    IF domain_type == "D":
        // D型:数据拉取→处理→存储
        data_node = BUILD_HTTP_REQUEST_NODE("fetch_data", input.architecture.data_source)
        db_node = BUILD_DATABASE_NODE("store_results", input.architecture.database)
        APPEND workflow_nodes, data_node
        APPEND workflow_nodes, db_node

    // 4d: 通知分发节点
    notify_node = BUILD_HTTP_REQUEST_NODE("push_notification", input.architecture.notification_endpoint)
    APPEND workflow_nodes, notify_node

    // 阶段5: 凭证管理
    credentials = []
    FOR EACH node IN workflow_nodes:
        IF node.requires_credentials:
            cred = BUILD_CREDENTIAL_CONFIG(node.credential_type, node.id)
            APPEND credentials, cred
    // 凭证不内嵌到工作流JSON,使用n8n凭证管理器引用

    // 阶段6: 构建完整工作流JSON
    workflow_json = {
        "name": GENERATE_WORKFLOW_NAME(input.architecture),
        "nodes": workflow_nodes,
        "connections": BUILD_NODE_CONNECTIONS(workflow_nodes),
        "credentials": MAP(credentials, c => {"id": c.id, "name": c.name}),
        "settings": {"executionOrder": "v1"}
    }
    ASSERT VALIDATE_WORKFLOW_JSON(workflow_json)

    // 阶段7: 质量门控
    CALL protocol_quality_gate(workflow_json, credentials)
    IF quality_gate_result.violations:
        FIX_VIOLATIONS(quality_gate_result.violations)

    output = {
        "output_format": "工作流模板JSON + 集成接口规范" +
            (role_mode == "executor" ? " + D型深度集成配置" : ""),
        "platform_specific_config": {
            "role_mode": role_mode,
            "workflow_nodes": MAP(workflow_nodes, n => n.name + ": " + n.type),
            "credentials_required": LEN(credentials)
        },
        "generated_files": [{"path": "workflow.json", "content": workflow_json}]
    }
    RETURN output
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
