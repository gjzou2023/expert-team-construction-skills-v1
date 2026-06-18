---
name: pipeline-s5-architecture-design
id: "pipeline-s5-architecture-design"
layer: "L1"
name_zh: "阶段五：架构设计"
name_en: "Stage 5: Architecture Design"
version: "1.3.0"
description: 从交付物倒推角色，MECE三问校验，设计SOP/数据流/反馈回路/冷启动策略，执行5.1-5.7自检。v1.3.0新增角色深度画像与结构化辩论机制。角色数≥4必须Team型。
agent_created: true
trigger_keywords: ["S5执行", "架构设计", "角色倒推", "SOP设计", "MECE校验"]
dependencies: ["core-mental-model-engine", "core-deliverable-backward-engine", "protocol-quality-gate", "protocol-feedback-loop", "protocol-compliance-engine"]
---

# 阶段五：架构设计 (Stage 5: Architecture Design)

> **层级**: L1 | **版本**: 1.3.0 | **ID**: `pipeline-s5-architecture-design`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。承接 `pipeline-s4-deliverable-anchoring` 的输出，完成后自动衔接 `pipeline-s6-toolchain-matching`。快速通道下简化为单人角色。

## 概述

从交付物倒推角色，MECE三问校验，设计SOP/数据流/反馈回路/冷启动策略，执行5.1-5.7自检。v1.3.0新增角色深度画像与结构化辩论机制。角色数≥4必须Team型。

## 触发条件

当检测到以下关键词或场景时自动激活：架构, 角色设计, SOP, 团队, 主理人, MECE

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s4_outputs": {
      "type": "object",
      "description": "S4交付物输出"
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
      ]
    },
    "channel": {
      "type": "string",
      "enum": [
        "fast",
        "standard",
        "strict"
      ]
    }
  },
  "required": [
    "s4_outputs",
    "domain_type",
    "channel"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "roles": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          },
          "profession": {
            "type": "string"
          },
          "capabilities": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "sop_phases": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    },
    "data_flow": {
      "type": "string"
    },
    "feedback_loops": {
      "type": "array"
    },
    "cold_start_strategy": {
      "type": "object"
    },
    "sop": {
      "type": "object"
    },
    "quality_report": {
      "type": "object"
    }
  },
  "required": [
    "roles",
    "data_flow",
    "feedback_loops",
    "cold_start_strategy",
    "sop",
    "quality_report"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)从交付物倒推角色(调用core-deliverable-backward-engine)→(2)MECE三问校验(5.2:覆盖性/独立性/责任唯一性,任一不通过→🔴阻断)→(3)角色深度画像(三要素,v1.3.0新增)→(4)设计SOP(含Phase定义)→(5)设计数据流→(6)设计反馈回路(按领域类型激活必建回路)→(7)设计冷启动策略→(8)结构化辩论与冲突检测(v1.3.0新增)→(9)红队挑战(v1.3.0新增)→(10)调用protocol-quality-gate执行5.1-5.7自检→(11)输出架构方案。角色数≥4→Team型+主理人SOP编排。快速通道：单一最优架构。

## Few-shot 示例

### 示例 1

**输入**:
```json
{
  "user_input": "触发阶段五：架构设计的典型用户消息"
}
```

**输出**:
```json
{
  "status": "执行完成",
  "stage": 5,
  "next_action": "进入S6"
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://pipeline/stage-5-rules` — 阶段5执行规则
- **[dynamic]** `file://pipeline/stage-5-state` — 阶段5运行时状态

## 依赖关系

- `core-mental-model-engine`
- `core-deliverable-backward-engine`

## 角色定义12项模板与架构分支逻辑

| 字段 | 定义 | 示例 |
| --- | --- | --- |
| name | 2-3字正常人名风格花名 | 墨言 |
| agent_id | kebab-case平台ID | content-strategist |
| one_line_duty | 一句话职责 | 负责把选题转成可发布图文方案 |
| deliverables | 负责交付物清单 | 小红书图文、私域话术 |
| capabilities | 3-5个核心能力标签 | 选题、结构、标题、平台合规 |
| layer | 上游共享/下游专线/末端合流 | 下游专线层 |
| io_schema | 机器可解析输入输出Schema | input: topic; output: draft |
| relationships | 上下游关系 | 接收研究员输出，交给合规员 |
| communication_protocol | 平台协作协议 | WorkBuddy: spawn-SendMessage |
| tools | 工具和兜底 | 搜索API；不可用时纯提示词调研 |
| quality_rules | 至少3条客观验收规则 | 标题<=20字、禁词=0、结构完整 |
| activation_trigger | 触发条件 | 用户要求生成内容方案时触发 |

## 角色画像三要素升级（v1.3.0新增）

在原有12项定义基础上，每位专家角色的`capabilities`字段需扩展为以下三要素结构：

| 要素 | 字段名 | 说明 | 示例 |
|------|--------|------|------|
| 专业背景锚定 | `professional_background` | XX年经验，曾操盘过XX类型项目 | "15年产险精算经验，主导过3款UBI产品定价" |
| 思维工具箱 | `methodology_toolbox` | 该专家惯用的分析框架和方法论（3-5个） | "广义线性模型(GLM)、Tweedie分布、IBNR准备金评估" |
| 认知偏好与盲点 | `cognitive_bias` | 该角色倾向于从什么视角切入，可能忽视什么 | "关注损失率和费率充足性，可能低估用户体验影响" |

### 示例

```
- 身份：保险精算师
- 专业背景：15年产险精算经验，主导过3款UBI产品定价
- 思维工具箱：广义线性模型(GLM)、Tweedie分布、IBNR准备金评估
- 认知偏好与盲点：关注损失率和费率充足性，可能低估用户体验影响
```

### 与12项的对应关系

- `professional_background` 替代原 `capabilities` 中"经验描述"部分，并提供量化锚定
- `methodology_toolbox` 扩展原 `capabilities`，从标签式能力描述升级为具体方法论引用
- `cognitive_bias` 为新增字段，用于后续冲突检测和辩论环节

## 用户角色-专家画像对偶映射（v1.4.0新增）

用户角色识别结果应影响专家画像三要素的呈现方式：

| 用户角色 | professional_background适配 | methodology_toolbox适配 | cognitive_bias适配 |
|---------|---------------------------|------------------------|-------------------|
| 决策者 | 量化ROI锚定："主导XX，带动XX%增长" | 仅列出名称，不展开方法论细节 | 突出"可能忽视什么"，弱化"关注什么" |
| 技术负责人 | 技术栈锚定："精通XX框架，处理过XX级并发" | 展开具体方法论步骤和参数 | 突出"技术偏好"，弱化"业务盲点" |
| 项目经理 | 交付物锚定："交付过XX项目，管理过XX人团队" | 列出管理方法论名称和适用条件 | 突出"进度盲点"，弱化"质量偏好" |
| 探索者 | 通俗化描述："做过XX年的XX工作" | 用一句话解释方法论核心思想 | 简化为"擅长XX方向"和"需注意XX" |

### 适配触发时机
- S5角色定义完成后，根据S1输出的user_role字段自动调整角色画像的呈现粒度
- 仅影响呈现方式，不影响角色的核心能力和判断逻辑

## 结构化辩论与冲突检测机制（v1.3.0新增）

### 强制冲突检测

专家角色定义完成后，系统自动检测是否存在以下冲突类型：

| 冲突类型 | 检测方式 | 示例 |
|---------|---------|------|
| 目标冲突 | 两个角色核心目标不可同时最大化 | 安全性专家 vs 用户体验专家 |
| 资源冲突 | 预算/人力/时间有限 vs 多角色需求 | 预算有限 vs 技术要求高 |
| 时序冲突 | 快速上线 vs 充分测试 | 市场窗口期 vs 质量保证 |
| 价值冲突 | 商业目标 vs 伦理约束 | 增长指标 vs 用户隐私 |

### 冲突深化流程

若检测到冲突，启动专项辩论：
1. **明确矛盾双方的核心诉求**（各1-2句话）
2. **各方给出支撑论据**（数据/案例/逻辑推理）
3. **探索可能的调和方案或必要的取舍**
4. **最终标注"此处需要用户决策"** 并给出决策选项和各自后果

### 红队角色机制

在最终方案形成后，增设一位「批判者」角色（不纳入常规团队编制），专门：
- 寻找方案漏洞
- 挑战隐含假设
- 提出最坏情况 scenario
- 对每项关键结论给出至少一个反例或质疑

红队输出不纳入最终方案，但必须被响应——每一项质疑需要主方案给出解释或修正。

### 与现有失败模式预演的关系

红队机制是8类失败模式预演的补充：
- 失败模式预演解决已知风险类型
- 红队机制挑战隐含假设和盲点

```text
FUNCTION design_architecture(deliverables, workflow, platform, channel, domain_type):
    role_count = estimate_role_count(deliverables)
    IF role_count >= 4:
        expert_type = "team"
    ELIF role_count == 3:
        expert_type = ask_user_team_or_agent()
    ELSE:
        expert_type = "agent"
    roles = map_roles_from_deliverables(deliverables)
    ensure_mandatory_roles(roles, domain_type)
    FOR role IN roles:
        define_12_fields(role)
        ASSERT schema_compatible_with_upstream(role)
    IF channel IN ["standard", "strict"]:
        scheme_A = design_variant("lean")
        scheme_B = design_variant("robust")
        comparison = compare_schemes([scheme_A, scheme_B], dimensions=[交付速度, 质量稳定性, 合规风险, 工具依赖, 维护成本])
        selected = recommend_with_cot(comparison)
    ELSE:
        selected = design_single_best_architecture(roles)
    CALL protocol-feedback-loop(domain_type)
    CALL protocol-compliance-engine(domain_type)
    CALL protocol-quality-gate(stage=5, output=selected)
    RETURN architecture_blueprint
```

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s5_architecture_design(input):
    # ===== 阶段五：架构设计 - 入口校验 =====
    ASSERT input.s4_outputs EXISTS
    ASSERT input.domain_type IN ["A", "B", "C", "D", "F"]  # E型已改为A-F组合标记
    ASSERT input.channel IN ["fast", "standard", "strict"]
    LOAD context_inheritance FROM s4

    s4_data = input.s4_outputs
    domain_type = input.domain_type
    channel = input.channel
    deliverables = s4_data.deliverables

    # ===== 步骤1: 协作模型决策 =====
    role_count = ESTIMATE_role_count(deliverables, domain_type)
    IF role_count >= 4:
        expert_type = "team"           # 必须Team型
    ELIF role_count == 3:
        expert_type = ASK_USER("3个角色，你希望组建成团队(Team)还是单Agent？")
    ELIF role_count <= 2:
        IF channel == "fast":
            expert_type = "agent"       # 快速通道默认Agent
        ELSE:
            expert_type = ASK_USER("建议使用单Agent模式，是否确认？")
            IF expert_type != "agent":
                expert_type = "team"

    # ===== 步骤2: 角色映射(领域必设角色) =====
    MANDATORY_ROLES = {
        "A": ["content-strategist", "compliance-reviewer"],
        "B": ["project-manager", "quality-reviewer"],
        "C": ["growth-strategist", "conversion-optimizer"],
        "D": ["data-analyst", "insight-narrator"],
        "F": ["triage-agent", "senior-service-agent", "compliance-guardian"],
        "E": ["content-strategist", "senior-service-agent", "compliance-guardian"]
    }
    roles = MAP_ROLES_FROM_DELIVERABLES(deliverables, domain_type)
    # 确保必设角色存在
    FOR mandatory_role IN MANDATORY_ROLES[domain_type]:
        IF mandatory_role NOT IN roles:
            APPEND CREATE_ROLE(mandatory_role, domain_type) TO roles

    # ===== 步骤3: 12项定义(每个角色) =====
    TWELVE_FIELDS = ["name", "agent_id", "one_line_duty", "deliverables", "capabilities",
                     "layer", "io_schema", "relationships", "communication_protocol",
                     "tools", "quality_rules", "activation_trigger"]
    FOR role IN roles:
        FOR field IN TWELVE_FIELDS:
            IF role[field] IS_EMPTY:
                role[field] = GENERATE_field_value(field, role, domain_type)
        # 特殊校验
        ASSERT LENGTH(role.name) <= 3              # 2-3字花名
        ASSERT role.agent_id MATCHES kebab_case    # kebab-case格式
        ASSERT LENGTH(role.quality_rules) >= 3      # 至少3条验收规则
        ASSERT role.io_schema IS_MACHINE_PARSEABLE  # 机器可解析Schema

    # ===== 步骤4: 失败模式预演(8类) =====
    FAILURE_MODES = [
        "上游产出缺失",    # 上游角色未按时交付
        "工具不可用",      # 依赖工具/MCP服务宕机
        "合规拦截",        # 合规审查未通过
        "用户需求变更",    # 用户中途修改需求
        "质量不达标",      # 产出质量低于验收标准
        "角色冲突",        # 多角色职责重叠或遗漏
        "数据安全违规",    # 敏感数据流向不合规
        "平台能力限制"     # 目标平台不支持某功能
    ]
    failure_handling_plan = {}
    FOR mode IN FAILURE_MODES:
        affected_roles = IDENTIFY_AFFECTED_ROLES(mode, roles)
        mitigation = DESIGN_MITIGATION(mode, affected_roles, domain_type)
        failure_handling_plan[mode] = {
            "affected_roles": affected_roles,
            "mitigation": mitigation,
            "escalation_path": DEFINE_ESCALATION(mode, expert_type)
        }

    # ===== 步骤5: 反馈闭环(按领域类型) =====
    FEEDBACK_LOOPS_BY_DOMAIN = {
        "A": ["内容效果反馈", "用户互动数据", "平台算法适应"],
        "B": ["项目里程碑反馈", "客户满意度", "质量审查反馈"],
        "C": ["获客转化反馈", "渠道ROI反馈", "用户行为数据"],
        "D": ["分析准确度反馈", "决策采纳反馈", "数据源质量反馈"],
        "F": ["满意度追踪", "响应时间监控", "升级率监控", "合规命中率"],
        "E": ["内容效果反馈", "满意度追踪", "合规命中率", "跨域协同反馈"]
    }
    feedback_loops = FEEDBACK_LOOPS_BY_DOMAIN[domain_type]
    FOR loop IN feedback_loops:
        loop_config = DESIGN_FEEDBACK_LOOP(loop, roles, domain_type)
        loop.trigger = DEFINE_TRIGGER(loop)
        loop.frequency = DEFINE_FREQUENCY(loop, domain_type)
        loop.action_on_signal = DEFINE_ACTION(loop)

    # ===== 步骤6: 知识资产沉淀 =====
    knowledge_assets = []
    # 混合型场景通过domain_profile.secondary_domains判断
    has_secondary = input.domain_profile EXISTS AND LENGTH(input.domain_profile.secondary_domains) > 0
    secondary_contains = {{"A":false, "B":false, "C":false, "D":false, "F":false}}
    IF has_secondary:
        FOR sd IN input.domain_profile.secondary_domains:
            secondary_contains[sd] = true

    IF domain_type == "A" OR (has_secondary AND secondary_contains["A"]):
        APPEND {"type": "内容模板库", "update_frequency": "月度"} TO knowledge_assets
        APPEND {"type": "爆款素材库", "update_frequency": "周度"} TO knowledge_assets
    IF domain_type IN ["B", "D"]:
        APPEND {"type": "案例知识库", "update_frequency": "项目结案时"} TO knowledge_assets
    IF domain_type == "F" OR (has_secondary AND secondary_contains["F"]):
        APPEND {"type": "FAQ知识库", "update_frequency": "周度"} TO knowledge_assets
        APPEND {"type": "话术模板库", "update_frequency": "月度"} TO knowledge_assets

    # ===== 步骤7: 合规保障 =====
    compliance_config = CALL protocol-compliance-engine(domain_type, roles)
    # 确保每个需要合规审查的角色都有审查机制
    FOR role IN roles:
        IF role.deliverables CONTAINS_REGULATED_CONTENT(domain_type):
            role.compliance_check = "pre_output"
            ASSERT compliance_config.has_reviewer_for(role)

    # ===== 步骤8: 架构方案分支(ToT比较+CoT推荐) =====
    IF channel IN ["standard", "strict"]:
        # 设计两个方案
        scheme_A = DESIGN_VARIANT("lean", roles, domain_type)
        scheme_B = DESIGN_VARIANT("robust", roles, domain_type)

        # 5维对比矩阵
        COMPARISON_DIMS = ["交付速度", "质量稳定性", "合规风险", "工具依赖", "维护成本"]
        comparison = {}
        FOR dim IN COMPARISON_DIMS:
            comparison[dim] = {
                "scheme_A": EVALUATE(scheme_A, dim),
                "scheme_B": EVALUATE(scheme_B, dim)
            }

        # ToT(思维树)比较 + CoT(思维链)推荐
        reasoning = GENERATE_COT_RECOMMENDATION(comparison, domain_type)
        selected = reasoning.recommendation
        OUTPUT "方案比较：" + comparison + "推荐：" + reasoning TO user
        user_choice = WAIT_FOR_USER()
        IF user_choice != selected:
            selected = user_choice
    ELSE:
        # 快速通道：单一最优架构
        selected = DESIGN_SINGLE_BEST_ARCHITECTURE(roles, domain_type)

    # ===== 步骤9: SOP编排(Team型必须) =====
    sop = {}
    IF expert_type == "team":
        sop.team_type = "team"
        sop.phases = DEFINE_SOP_PHASES(roles, domain_type)
        # 主理人SOP编排
        sop.coordinator_role = FIND_COORDINATOR_ROLE(roles)
        sop.standup_frequency = "daily" IF domain_type IN ["A", "C", "F"] ELSE "weekly"
        # 数据流设计
        sop.data_flow = DESIGN_DATA_FLOW(roles, deliverables)
    ELSE:
        sop.team_type = "agent"
        sop.phases = DEFINE_AGENT_PHASES(roles[0], domain_type)
        sop.data_flow = "输入→处理→输出(单线)"

    # ===== 步骤10: 跨阶段自检 =====
    self_check_result = {}
    self_check_result.coverage = VERIFY_ALL_DELIVERABLES_COVERED(roles, deliverables)
    self_check_result.independence = VERIFY_ROLE_INDEPENDENCE(roles)
    self_check_result.responsibility = VERIFY_SINGLE_RESPONSIBILITY(roles)
    self_check_result.schema_compatibility = VERIFY_SCHEMA_COMPATIBILITY(roles)
    IF ANY(self_check_result) == FALSE:
        RAISE "架构自检失败: " + FAILED_ITEMS(self_check_result)

    # ===== 步骤11: 健康检查 =====
    health_check = {}
    health_check.role_count = LENGTH(roles)
    health_check.compliance_activated = compliance_config.all_activated
    health_check.feedback_loops_count = LENGTH(feedback_loops)
    health_check.failure_modes_covered = LENGTH(failure_handling_plan)
    health_check.knowledge_assets_count = LENGTH(knowledge_assets)
    CALL protocol-quality-gate(stage=5, output=selected)

    # ===== 产出输出 =====
    output = BUILD_output_according_to_output_schema({
        "roles": roles,
        "data_flow": sop.data_flow,
        "feedback_loops": feedback_loops,
        "cold_start_strategy": DESIGN_COLD_START(roles, domain_type),
        "sop": sop,
        "quality_report": health_check
    })
    RETURN output
```

## 下一阶段路由

> 本阶段完成后，由 `team-orchestrator` 自动衔接至 `pipeline-s6-toolchain-matching`（阶段六：工具链匹配）。
> 衔接条件：角色清单已生成 + MECE校验通过 + SOP已设计。
> 角色数>=4时自动启用Team型协作模式。用户无需手动触发下一阶段。

## 版本

1.3.0

---
*本Skill由全域专家团构建skills体系生成，版本1.3.0，日期2026-06-16*
