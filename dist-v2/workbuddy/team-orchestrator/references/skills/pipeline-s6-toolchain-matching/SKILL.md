---
name: pipeline-s6-toolchain-matching
description: 从角色能力需求匹配工具，评估可用性，为不可用工具设计纯提示词兜底，工具数据安全评估。所有工具必须有纯提示词兜底方案。 Use when: 用户说"S6执行、工具链匹配、MCP配置、提示词兜底、数据安全评估"等触发词。
---

# 阶段六：工具链匹配

> **层级**: L1 | **版本**: 1.1.0 | **ID**: `pipeline-s6-toolchain-matching` | **中文名**: 阶段六：工具链匹配 | **英文名**: Stage 6: Toolchain Matching
# 阶段六：工具链匹配 (Stage 6: Toolchain Matching)

> **层级**: L1 | **版本**: 1.1.0 | **ID**: `pipeline-s6-toolchain-matching`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。承接 `pipeline-s5-architecture-design` 的输出，完成后自动衔接 `pipeline-s7-expert-package-generation`。

## 概述

从角色能力需求匹配工具，评估可用性，为不可用工具设计纯提示词兜底，工具数据安全评估。所有工具必须有纯提示词兜底方案。

## 触发条件

当检测到以下关键词或场景时自动激活：工具, MCP, API, 纯提示词, 兜底, 工具链

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s5_outputs": {
      "type": "object",
      "description": "S5架构设计输出(含roles/sop)"
    },
    "platform": {
      "type": "string",
      "enum": [
        "workbuddy",
        "codex",
        "hermes",
        "feishu",
        "n8n",
        "comfyui",
        "coze",
        "dify"
      ]
    }
  },
  "required": [
    "s5_outputs",
    "platform"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "tool_matrix": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "role_id": {
            "type": "string"
          },
          "tool_name": {
            "type": "string"
          },
          "availability": {
            "type": "string",
            "enum": [
              "installed",
              "installable",
              "unavailable"
            ]
          },
          "fallback_prompt": {
            "type": "string"
          },
          "data_security_level": {
            "type": "string",
            "enum": [
              "low",
              "medium",
              "high"
            ]
          }
        }
      }
    },
    "integration_specs": {
      "type": "object"
    },
    "degradation_plan": {
      "type": "array"
    }
  },
  "required": [
    "tool_matrix",
    "integration_specs",
    "degradation_plan"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)从角色能力需求匹配工具→(2)评估工具可用性(已安装/可安装/不可用)→(3)为不可用工具设计纯提示词兜底→(4)工具数据安全评估(§5.5)→(5)调用protocol-tool-integration生成集成规范→(6)输出工具链方案。优先级：平台内置→MCP→外部API→纯提示词。纯提示词兜底强制：所有工具必须有纯提示词兜底方案。数据安全三原则：(1)高敏感度领域禁止敏感数据→第三方;(2)使用第三方必须注明数据流向;(3)每个工具评估数据安全等级。

## Few-shot 示例

### 示例 1：正常流程（标准通道，A型内容传播，WorkBuddy平台）

**输入**:
```json
{
  "s5_outputs": {
    "roles": [
      {"agent_id": "content-strategist", "deliverables": ["图文笔记", "视频脚本"], "capabilities": ["内容生成", "合规审查"]},
      {"agent_id": "visual-designer", "deliverables": ["封面图", "信息图"], "capabilities": ["图像生成"]}
    ],
    "domain_type": "A",
    "platform": "workbuddy"
  },
  "platform": "workbuddy",
  "data_sensitivity": "低"
}
```

**输出**:
```json
{
  "tool_matrix": [
    {"role_id": "content-strategist", "tool_name": "WorkBuddy内置Markdown编辑", "availability": "installed", "fallback_prompt": "按以下模板撰写：标题(≤20字)+正文(800-1500字)+CTA(1句话)", "data_security_level": "low", "priority": 1},
    {"role_id": "content-strategist", "tool_name": "MCP:web-search", "availability": "installable", "fallback_prompt": "基于你已有的知识回答，标注'⚡未搜索验证'", "data_security_level": "low", "priority": 2},
    {"role_id": "visual-designer", "tool_name": "MCP:image-gen", "availability": "installable", "fallback_prompt": "生成提示词描述：主体+风格+配色+尺寸，由用户手动生成", "data_security_level": "low", "priority": 2}
  ],
  "integration_specs": {"web-search": {"type": "mcp", "config": "mcp.json中添加search服务"}, "image-gen": {"type": "mcp", "config": "需DALL-E/ComfyUI MCP服务"}},
  "degradation_plan": [{"level": "纯提示词", "description": "所有工具退回纯提示词方案，标注⚡符号", "trigger": "无MCP服务可用时"}],
  "status": "completed",
  "stage": 6,
  "next_action": "进入S7专家包生成"
}
```

### 示例 2：异常场景（高敏感度领域+外部API数据安全拒绝）

**输入**:
```json
{
  "s5_outputs": {
    "roles": [
      {"agent_id": "financial-advisor", "deliverables": ["投资建议书", "风险评估报告"], "capabilities": ["数据分析", "合规审查"]},
      {"agent_id": "compliance-officer", "deliverables": ["合规审查意见"], "capabilities": ["法规检索", "风险标记"]}
    ],
    "domain_type": "B",
    "platform": "workbuddy",
    "regulated": true
  },
  "platform": "workbuddy",
  "data_sensitivity": "高"
}
```

**输出**:
```json
{
  "tool_matrix": [
    {"role_id": "financial-advisor", "tool_name": "WorkBuddy内置推理", "availability": "installed", "fallback_prompt": "基于公开财报数据分析，标注❓需人工核实", "data_security_level": "high", "priority": 1},
    {"role_id": "financial-advisor", "tool_name": "外部API:金融数据", "availability": "available_but_rejected", "fallback_prompt": "由用户提供脱敏数据，标注🔴禁止外发", "data_security_level": "high", "priority": 4, "rejection_reason": "高敏感度领域禁止将金融数据发送到第三方API"},
    {"role_id": "compliance-officer", "tool_name": "MCP:web-search", "availability": "installable", "fallback_prompt": "基于内置法规清单+⚡标注静态来源", "data_security_level": "high", "priority": 2}
  ],
  "integration_specs": {"web-search": {"type": "mcp", "config": "仅检索公开法规，不传输用户数据"}},
  "degradation_plan": [{"level": "纯提示词+人工介入", "description": "金融数据相关操作退回纯提示词，每次数据操作须人工确认", "trigger": "数据安全等级=高时"}],
  "security_assessment": [{"tool": "外部API:金融数据", "data_flow": "用户金融数据→第三方服务器", "risk": "🔴违反数据安全原则：高敏感度数据禁止外发", "alternative": "用户手动提供脱敏数据，AI基于脱敏数据分析"}],
  "status": "completed_with_warnings",
  "stage": 6,
  "next_action": "进入S7专家包生成(含数据安全协议)"
}
```

### 示例 3：快速通道变体（低复杂度，纯提示词方案为主）

**输入**:
```json
{
  "s5_outputs": {
    "roles": [
      {"agent_id": "lifestyle-assistant", "deliverables": ["每日穿搭建议"], "capabilities": ["生活建议"]}
    ],
    "domain_type": "A",
    "platform": "workbuddy",
    "track": "快速通道"
  },
  "platform": "workbuddy",
  "data_sensitivity": "低"
}
```

**输出**:
```json
{
  "tool_matrix": [
    {"role_id": "lifestyle-assistant", "tool_name": "纯提示词方案", "availability": "always", "fallback_prompt": "你是一个生活方式顾问，根据用户描述的场合、天气、个人偏好，给出3套穿搭建议。每套包含：上装+下装+鞋+配饰，用emoji标注风格(🏖️休闲/💼通勤/🎉聚会)", "data_security_level": "low", "priority": 4}
  ],
  "integration_specs": {},
  "degradation_plan": [{"level": "纯提示词", "description": "快速通道默认纯提示词方案，无需额外工具", "trigger": "快速通道默认策略"}],
  "status": "completed",
  "stage": 6,
  "next_action": "进入S7(快速通道简化版)"
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://pipeline/stage-6-rules` — 阶段6执行规则
- **[dynamic]** `file://pipeline/stage-6-state` — 阶段6运行时状态

## 依赖关系

- `core-mental-model-engine`

## 工具链优先级与5维对比矩阵

| 优先级 | 类别 | 规则 |
| --- | --- | --- |
| 1 | 目标平台内置能力 | 部署成本最低，优先使用 |
| 2 | 目标平台支持的扩展协议(MCP) | 需要扩展能力但仍保留平台内集成 |
| 3 | 通用外部API | 跨平台但要进行数据安全评估 |
| 4 | 纯提示词方案 | 最终兜底，必须提供 |

| 字段 | 维度1 | 维度2 | 维度3 | 维度4 | 维度5 |
| --- | --- | --- | --- | --- | --- |
| 候选工具 | 交付物适配度 | 部署难度 | 稳定性 | 成本 | 推荐度 |

```text
FUNCTION match_toolchain(deliverables, roles, platform, data_sensitivity):
    FOR deliverable IN deliverables:
        candidates = find_tool_candidates(deliverable, platform)
        sorted_candidates = sort_by_priority([平台内置, MCP, 外部API, 纯提示词])
        comparison = compare_matrix(sorted_candidates, [交付物适配度, 部署难度, 稳定性, 成本, 推荐度])
        recommended = select_best_with_reasoning(comparison)
        ASSERT recommended has fallback_prompt
    FOR tool IN recommended_tools:
        security = evaluate_data_security(tool, data_sensitivity)
        IF data_sensitivity == "高" AND tool.sends_data_externally:
            REJECT(tool)
            USE(tool.safe_alternative)
    RETURN tool_matrix
```

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s6_toolchain_matching(input):
    # ===== 阶段六：工具链匹配 - 入口校验 =====
    ASSERT input.s5_outputs EXISTS
    ASSERT input.platform IN ["workbuddy", "codex", "hermes", "feishu", "n8n", "comfyui", "coze", "dify"]
    LOAD context_inheritance FROM s5

    s5_data = input.s5_outputs
    platform = input.platform
    roles = s5_data.roles
    domain_type = s5_data.domain_type IF EXISTS ELSE "A"

    # ===== 步骤1: 4级优先级框架 =====
    PRIORITY_LEVELS = {
        1: "目标平台内置能力",       # 部署成本最低，优先使用
        2: "目标平台支持的MCP扩展",  # 需扩展但仍保留平台内集成
        3: "通用外部API",            # 跨平台但需数据安全评估
        4: "纯提示词方案"            # 最终兜底，必须提供
    }

    # ===== 步骤2: 从角色能力需求匹配工具 =====
    tool_matrix = []
    FOR role IN roles:
        FOR capability IN role.capabilities:
            # 查找候选工具
            candidates = FIND_TOOL_CANDIDATES(capability, platform)
            # 按优先级排序
            sorted_candidates = SORT_BY_PRIORITY(candidates, PRIORITY_LEVELS)
            # 选择最高优先级可用工具
            selected_tool = sorted_candidates[0]

            tool_entry = {}
            tool_entry.role_id = role.agent_id
            tool_entry.tool_name = selected_tool.name
            tool_entry.availability = CHECK_AVAILABILITY(selected_tool, platform)
            tool_entry.priority = selected_tool.priority_level

            # 纯提示词兜底方案(强制)
            tool_entry.fallback_prompt = GENERATE_FALLBACK_PROMPT(capability, selected_tool)
            ASSERT tool_entry.fallback_prompt IS NOT EMPTY

            APPEND tool_entry TO tool_matrix

    # ===== 步骤3: 5维度对比矩阵 =====
    COMPARISON_DIMS = ["交付物适配度", "部署难度", "稳定性", "成本", "推荐度"]
    FOR tool_entry IN tool_matrix:
        # 查找同功能候选工具(可能有多个选择)
        alternatives = FIND_ALTERNATIVES(tool_entry.tool_name, platform)
        IF LENGTH(alternatives) > 1:
            comparison = {}
            FOR dim IN COMPARISON_DIMS:
                scores = {}
                FOR alt IN alternatives:
                    scores[alt.name] = EVALUATE_ON_DIMENSION(alt, dim)
                comparison[dim] = scores
            # 推荐最高综合得分
            recommended = SELECT_BEST_WITH_REASONING(comparison)
            IF recommended.name != tool_entry.tool_name:
                tool_entry.tool_name = recommended.name
                tool_entry.fallback_prompt = GENERATE_FALLBACK_PROMPT(tool_entry.role_id, recommended)

    # ===== 步骤4: 数据安全审查(高敏感度禁止外发) =====
    DATA_SENSITIVITY = EVALUATE_DATA_SENSITIVITY(domain_type, roles)
    security_assessment = []

    FOR tool_entry IN tool_matrix:
        tool_entry.data_security_level = ASSESS_DATA_SECURITY(tool_entry, domain_type)

        # 数据安全三原则
        # 原则1: 高敏感度领域禁止敏感数据→第三方
        IF DATA_SENSITIVITY == "高" AND tool_entry.tool_name CONTAINS "外部API":
            IF tool_entry.sends_data_externally == TRUE:
                # 拒绝该工具，使用安全替代
                APPEND {
                    "tool": tool_entry.tool_name,
                    "risk": "🔴违反数据安全原则：高敏感度数据禁止外发",
                    "alternative": tool_entry.fallback_prompt
                } TO security_assessment
                tool_entry.availability = "available_but_rejected"
                tool_entry.rejection_reason = "高敏感度领域禁止将数据发送到第三方API"

        # 原则2: 使用第三方必须注明数据流向
        IF tool_entry.tool_name CONTAINS "外部API" OR tool_entry.tool_name CONTAINS "MCP":
            tool_entry.data_flow_note = "数据流向：" + DESCRIBE_DATA_FLOW(tool_entry)
            IF tool_entry.availability != "available_but_rejected":
                APPEND {
                    "tool": tool_entry.tool_name,
                    "data_flow": tool_entry.data_flow_note,
                    "risk_level": tool_entry.data_security_level
                } TO security_assessment

        # 原则3: 每个工具评估数据安全等级
        ASSERT tool_entry.data_security_level IN ["low", "medium", "high"]

    # ===== 步骤5: 成本预估 =====
    cost_estimate = {}
    cost_estimate.setup_time = 0
    cost_estimate.monthly_cost = 0
    FOR tool_entry IN tool_matrix:
        IF tool_entry.availability == "installed":
            cost_estimate.setup_time = cost_estimate.setup_time + 0
        ELIF tool_entry.availability == "installable":
            cost_estimate.setup_time = cost_estimate.setup_time + ESTIMATE_SETUP_TIME(tool_entry)
        IF tool_entry.tool_name CONTAINS "外部API":
            cost_estimate.monthly_cost = cost_estimate.monthly_cost + ESTIMATE_API_COST(tool_entry)

    # ===== 步骤6: 分级启动方案 =====
    DEPLOYMENT_TIERS = {
        "纯提示词版": {
            "description": "仅使用纯提示词方案，无外部依赖",
            "setup_time": "5分钟",
            "quality": "基础可用",
            "trigger": "用户想立即体验或工具均不可用"
        },
        "基础工具版": {
            "description": "平台内置能力 + MCP扩展",
            "setup_time": "30分钟",
            "quality": "标准质量",
            "trigger": "用户追求效率和质量平衡"
        },
        "完整版": {
            "description": "全部推荐工具 + 外部API(通过安全审查)",
            "setup_time": "1-2小时",
            "quality": "最佳效果",
            "trigger": "用户追求极致效果且通过数据安全审查"
        }
    }

    # 根据数据安全等级调整
    IF DATA_SENSITIVITY == "高":
        DEPLOYMENT_TIERS["完整版"].description = "全部推荐工具(外部API已替换为安全替代)"
        DEPLOYMENT_TIERS["完整版"].setup_time = "2-3小时(含安全审查)"

    # 根据通道调整
    IF input.channel == "fast":
        recommended_tier = "纯提示词版"
    ELIF input.channel == "standard":
        recommended_tier = "基础工具版"
    ELSE:
        recommended_tier = "完整版"

    # ===== 步骤7: 降级计划生成 =====
    degradation_plan = []
    FOR tool_entry IN tool_matrix:
        IF tool_entry.availability == "unavailable":
            APPEND {
                "level": "纯提示词",
                "description": tool_entry.fallback_prompt,
                "trigger": tool_entry.tool_name + "不可用时"
            } TO degradation_plan
    IF LENGTH(degradation_plan) == 0:
        APPEND {
            "level": "全功能可用",
            "description": "所有工具均已就绪，无需降级",
            "trigger": "正常状态"
        } TO degradation_plan

    # ===== 步骤8: 集成规范生成 =====
    integration_specs = {}
    FOR tool_entry IN tool_matrix:
        IF tool_entry.availability != "unavailable" AND tool_entry.availability != "available_but_rejected":
            IF tool_entry.tool_name CONTAINS "MCP":
                integration_specs[tool_entry.tool_name] = {
                    "type": "mcp",
                    "config": GENERATE_MCP_CONFIG(tool_entry, platform)
                }
            ELIF tool_entry.tool_name CONTAINS "外部API":
                integration_specs[tool_entry.tool_name] = {
                    "type": "external_api",
                    "config": GENERATE_API_CONFIG(tool_entry),
                    "security_note": tool_entry.data_flow_note
                }

    # ===== 质量门控 =====
    CALL protocol-quality-gate(stage=6, output={
        "tool_matrix": tool_matrix,
        "security_assessment": security_assessment
    })
    ASSERT EVERY tool_entry IN tool_matrix HAS fallback_prompt
    ASSERT EVERY tool_entry IN tool_matrix HAS data_security_level

    # ===== 产出输出 =====
    output = BUILD_output_according_to_output_schema({
        "tool_matrix": tool_matrix,
        "integration_specs": integration_specs,
        "degradation_plan": degradation_plan
    })
    RETURN output
```

## 下一阶段路由

> 本阶段完成后，由 `team-orchestrator` 自动衔接至 `pipeline-s7-expert-package-generation`（阶段七：专家包生成）。
> 衔接条件：工具链已匹配 + 每个工具均有纯提示词兜底方案 + 数据安全评估完成。
> 用户无需手动触发下一阶段。

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
