---
name: core-deliverable-backward-engine
id: "core-deliverable-backward-engine"
layer: "L0"
name_zh: "交付物倒推引擎"
name_en: "Deliverable Backward Engine"
version: "1.1.0"
description: 从用户需求提取终端交付物→分配唯一第一责任人→反推能力→定义角色→定义工具→定义数据流。严格禁止逆向（先角色后交付物）。
agent_created: true
trigger_keywords: ["core-deliverable-backward-engine", "交付物倒推引擎", "L0倒推"]
dependencies: ["core-mental-model-engine"]
---

# 交付物倒推引擎 (Deliverable Backward Engine)

> **层级**: L0 | **版本**: 1.1.0 | **ID**: `core-deliverable-backward-engine`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

从用户需求提取终端交付物→分配唯一第一责任人→反推能力→定义角色→定义工具→定义数据流。严格禁止逆向（先角色后交付物）。

## 触发条件

当检测到以下关键词或场景时自动激活：交付物, 角色设计, 架构设计, 倒推, 从交付物开始, 责任分配

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "user_need": {
      "type": "string",
      "description": "用户需求描述"
    },
    "domain_type": {
      "type": "string",
      "enum": [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F"
      ],
      "description": "领域类型"
    },
    "deliverable_candidates": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "候选交付物列表"
    }
  },
  "required": [
    "user_need",
    "domain_type"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "deliverables": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string"
          },
          "format": {
            "type": "string"
          },
          "owner_role": {
            "type": "string"
          },
          "priority": {
            "type": "string",
            "enum": [
              "core",
              "enhancement"
            ]
          }
        }
      }
    },
    "role_capability_map": {
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "tool_requirement_map": {
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    },
    "data_flow": {
      "type": "string",
      "description": "Mermaid格式的数据流图"
    }
  },
  "required": [
    "deliverables",
    "role_capability_map",
    "tool_requirement_map",
    "data_flow"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

执行6步倒推链：(1)从用户需求提取终端交付物→(2)每个交付物分配唯一第一责任人→(3)从交付物反推所需能力→(4)从能力定义角色→(5)从角色定义工具→(6)从工具定义数据流。
严格禁止逆向（先角色后交付物）。
如检测到"先定义角色再找交付物"的错误倾向，立即纠偏。
分线规则：不同交付形态的渠道不得共用生产线（允许共用上游，下游必须分线）。

## Few-shot 示例

### 示例 1

**输入**:
```json
{
  "user_need": "做小红书美食探店账号",
  "domain_type": "A",
  "deliverable_candidates": [
    "小红书图文笔记",
    "私域引流话术"
  ]
}
```

**输出**:
```json
{
  "deliverables": [
    {
      "name": "小红书图文笔记",
      "format": "图片+文案",
      "owner_role": "content-strategist",
      "priority": "core"
    },
    {
      "name": "私域引流话术",
      "format": "文本模板",
      "owner_role": "content-strategist",
      "priority": "core"
    }
  ],
  "role_capability_map": {
    "content-strategist": [
      "内容选题",
      "文案创作",
      "平台适配"
    ]
  },
  "tool_requirement_map": {
    "content-strategist": [
      "ImageGen",
      "WebSearch"
    ]
  },
  "data_flow": "graph TD\\n  A[选题确定] --> B[素材生产]\\n  B --> C[内容创作]\\n  C --> D[平台适配]\\n  D --> E[发布分发]"
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://domain-defaults/deliverable-templates` — 各领域默认交付物模板
- **[static]** `file://naming-rules/role-naming` — 角色命名三分法规范

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_core_deliverable_backward_engine(input):
    // ========== 输入校验与初始化 ==========
    ASSERT input.user_need IS NOT EMPTY, "用户需求不可为空"
    ASSERT input.domain_type IN ["A","B","C","D","F"], "领域类型必须为A-F之一(E型已改为A-F组合标记)"
    LOAD context_inheritance FROM core-mental-model-engine
    // 质量门控由编排器在阶段结束后统一调用（避免递归）

    // ========== 第1步：从用户需求提取终端交付物 ==========
    raw_deliverables = EXTRACT_DELIVERABLES(input.user_need)
    IF input.deliverable_candidates IS NOT EMPTY:
        raw_deliverables = MERGE_CANDIDATES(raw_deliverables, input.deliverable_candidates)
    ASSERT LENGTH(raw_deliverables) > 0, "至少识别出一个交付物"
    FOR d IN raw_deliverables:
        d.format = INFER_DELIVERABLE_FORMAT(d, input.domain_type)
        d.priority = CLASSIFY_PRIORITY(d, input.user_need)  // core | enhancement
        d.lane_id = ASSIGN_LANE(d.format)  // 按交付形态分配产线

    // ========== 分线规则：不同交付形态不得共用生产线 ==========
    lanes = GROUP_BY(raw_deliverables, "lane_id")
    FOR lane_a IN lanes:
        FOR lane_b IN lanes:
            IF lane_a != lane_b:
                IF lane_a.downstream OVERLAPS lane_b.downstream:
                    RAISE "分线违规：不同交付形态的渠道不得共用下游生产线"
    // 允许共用上游，但下游必须分线
    FOR lane IN lanes:
        lane.upstream_shared = TRUE
        lane.downstream_isolated = TRUE

    // ========== 第2步：每个交付物分配唯一第一责任人 ==========
    FOR d IN raw_deliverables:
        d.owner_role = ASSIGN_UNIQUE_OWNER(d)
        ASSERT d.owner_role IS NOT EMPTY, "每个交付物必须有且仅有一个第一责任人"
        // 禁止逆向检查：不允许先定义角色再找交付物
        IF DETECT_REVERSE_TENDENCY(input.user_need):
            // 检测到"先定义角色再找交付物"的错误倾向
            OUTPUT "⚠️ 纠偏警告：检测到先定义角色再找交付物的逆向倾向，必须从交付物出发倒推"
            REORDER_FROM_DELIVERABLE(raw_deliverables)

    // ========== 第3步：从交付物反推所需能力 ==========
    role_capability_map = {}
    FOR d IN raw_deliverables:
        required_capabilities = REVERSE_ENGINEER_CAPABILITIES(d, input.domain_type)
        IF d.owner_role NOT IN role_capability_map:
            role_capability_map[d.owner_role] = []
        FOR cap IN required_capabilities:
            IF cap NOT IN role_capability_map[d.owner_role]:
                APPEND(role_capability_map[d.owner_role], cap)

    // ========== 第4步：从能力定义角色 ==========
    defined_roles = {}
    FOR role_name IN KEYS(role_capability_map):
        role = DEFINE_ROLE(role_name, role_capability_map[role_name])
        // 角色命名三分法：动词+名词+平台限定
        role.naming = APPLY_NAMING_RULE(role_name, input.domain_type)
        ASSERT role.capabilities == role_capability_map[role_name], "角色能力必须与倒推结果一致"
        defined_roles[role_name] = role

    // ========== 第5步：从角色定义工具 ==========
    tool_requirement_map = {}
    FOR role_name IN KEYS(defined_roles):
        tools = INFER_TOOLS_FROM_CAPABILITIES(role_capability_map[role_name])
        tool_requirement_map[role_name] = tools
        // 验证工具覆盖度
        FOR cap IN role_capability_map[role_name]:
            covered = FALSE
            FOR tool IN tools:
                IF TOOL_COVERS_CAPABILITY(tool, cap):
                    covered = TRUE
                    BREAK
            IF NOT covered:
                APPEND(tools, INFER_FALLBACK_TOOL(cap))

    // ========== 第6步：从工具定义数据流 ==========
    data_flow_edges = []
    FOR role_name IN KEYS(tool_requirement_map):
        FOR tool IN tool_requirement_map[role_name]:
            input_data = TOOL_INPUT_DATA(tool, role_capability_map[role_name])
            output_data = TOOL_OUTPUT_DATA(tool, role_capability_map[role_name])
            APPEND(data_flow_edges, {from: input_data, to: tool, output: output_data})
    // 构建Mermaid格式数据流图
    data_flow_mermaid = BUILD_MERMAID_GRAPH(data_flow_edges, lanes)

    // ========== 禁止逆向最终校验 ==========
    FOR role IN KEYS(defined_roles):
        role_deliverables = FILTER(raw_deliverables, d => d.owner_role == role)
        IF LENGTH(role_deliverables) == 0:
            RAISE "禁止逆向：角色{role}没有对应交付物，不允许先角色后交付物"

    // ========== 组装输出 ==========
    output = {
        deliverables: raw_deliverables,
        role_capability_map: role_capability_map,
        tool_requirement_map: tool_requirement_map,
        data_flow: data_flow_mermaid
    }
    // 质量门控由编排器在阶段结束后统一调用（避免递归）
    RETURN output

FUNCTION DETECT_REVERSE_TENDENCY(user_need):
    // 检测用户输入是否表现出"先定角色再找交付物"的倾向
    reverse_patterns = ["我需要一个XX角色", "帮我设计一个XX岗位", "团队应该有XX职位"]
    FOR pattern IN reverse_patterns:
        IF CONTAINS(user_need, pattern):
            RETURN TRUE
    RETURN FALSE

FUNCTION REVERSE_ENGINEER_CAPABILITIES(deliverable, domain_type):
    // 根据交付物和领域类型反推所需能力
    base_caps = LOAD_FROM_KB("file://domain-defaults/deliverable-templates", deliverable.format)
    domain_caps = LOAD_FROM_KB("file://domain-defaults/deliverable-templates", domain_type)
    RETURN UNION(base_caps, domain_caps)
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
