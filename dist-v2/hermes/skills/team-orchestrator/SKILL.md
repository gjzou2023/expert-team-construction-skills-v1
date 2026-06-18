---
name: team-orchestrator
description: 全域专家团构建skills系统统一入口编排器。用户只需触发此skill一次，系统自动按S1需求深潜→S2领域消歧→S3链路拆解→S4交付物锚定→S5架构设计→S Use when: 用户说"开始、帮我建、我想做、专家团、需求、刚开始"等触发词。
version: 1.5.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [orchestrator]
    related_skills:
      - pipeline-s1-need-diving
      - pipeline-s2-domain-disambiguation
      - pipeline-s3-chain-decomposition
      - pipeline-s4-deliverable-anchoring
      - pipeline-s5-architecture-design
      - pipeline-s6-toolchain-matching
      - pipeline-s7-expert-package-generation
      - pipeline-s8-platform-execution
    requires_toolsets: []
---

# 全域专家团总编排器

> **层级**: L-Meta | **版本**: 1.0.0 | **ID**: `team-orchestrator` | **中文名**: 全域专家团总编排器 | **英文名**: Team Orchestrator
# 全域专家团总编排器 (Team Orchestrator)

> **层级**: L-Meta (元编排层) | **版本**: 1.0.0 | **ID**: `team-orchestrator`

## 概述

本skill是全域专家团构建skills系统的**唯一入口**。用户只需说"帮我建个AI专家团"等触发词，系统自动启动完整的8阶段构建流程。所有39个子skill（L0核心引擎×6 + L1流程×8 + L2协议×11 + L3适配器×9 + L4约束×5）由本编排器根据任务上下文自动激活和调用，用户无需感知底层skill的存在，无需手动触发任何子skill。

## 核心原则

1. **单一入口**: 用户只与本编排器交互，不直接调用任何子skill
2. **自动编排**: S1→S2→S3→S4→S5→S6→S7→S8按序自动执行，阶段间自动衔接
3. **按需激活**: L0/L2/L3/L4层skill根据领域类型、通道等级、平台选择条件激活
4. **用户透明**: 用户看到的是"一个完整服务在运作"，而非"要手动调用skill A、再调用skill B"
5. **通道自适应**: 根据复杂度评估结果自动选择fast/standard/strict通道，调整各阶段深度

## 触发条件

当检测到以下关键词或场景时自动激活：开始, 帮我建, 我想做, 专家团, 需求, 刚开始, 构建专家, 建个AI, AI专家, 全域专家团, 构建团队, 帮我构建, 想要构建

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "user_first_message": {
      "type": "string",
      "description": "用户的首次交互消息，表达构建专家团的意图"
    },
    "user_context": {
      "type": "object",
      "properties": {
        "experience_level": {
          "type": "string",
          "enum": ["novice", "intermediate", "advanced"],
          "description": "用户AI经验水平"
        },
        "session_id": {
          "type": "string",
          "description": "会话ID，用于状态隔离"
        }
      }
    }
  },
  "required": ["user_first_message"]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "expert_team_package": {
      "type": "object",
      "description": "最终交付的专家包"
    },
    "platform_deployed": {
      "type": "boolean",
      "description": "是否已部署到目标平台"
    },
    "pipeline_summary": {
      "type": "object",
      "properties": {
        "domain_type": {"type": "string"},
        "channel_used": {"type": "string", "enum": ["fast", "standard", "strict"]},
        "stages_completed": {"type": "array", "items": {"type": "string"}},
        "total_stages": {"type": "integer"},
        "skills_activated": {"type": "array", "items": {"type": "string"}}
      }
    }
  },
  "required": ["expert_team_package", "pipeline_summary"]
}
```

## 工具声明 (tool_declarations)

本skill无外部工具依赖，纯提示词可执行。通过Skill系统自动加载子skill。

## 执行逻辑

### 总体编排流程

```text
FUNCTION execute_team_orchestrator(input):
    """
    全域专家团总编排器 - 唯一入口
    用户触发本skill后，系统自动执行完整的8阶段构建流程。
    所有子skill由本编排器自动激活和调用，用户无需手动触发。
    """

    # ===== 初始化 =====
    expert_team_id = GENERATE_ID()
    shared_memory = INIT_SHARED_MEMORY(expert_team_id)
    pipeline_state = {
        "current_stage": 0,
        "channel": null,
        "domain_type": null,
        "stages_completed": [],
        "skills_activated": [],
        "snapshots": {}
    }

    OUTPUT "[系统] 全域专家团构建skills系统已启动，共8个阶段。" TO user
    OUTPUT "[系统] 您只需回答各阶段的问题，系统将自动完成全部构建。" TO user

    # ===== 阶段1: 需求深潜 =====
    # 自动加载并执行 pipeline-s1-need-diving
    CALL protocol-single-question-guidance("阶段1/8: 需求深潜即将开始")
    OUTPUT "--- 阶段 1/8: 需求深潜 ---" TO user

    LOAD_SKILL "pipeline-s1-need-diving"
    s1_output = EXECUTE pipeline-s1-need-diving(input)
    # S1内部自动调用: core-mental-model-engine, core-complexity-channel-selector, protocol-single-question-guidance

    pipeline_state.channel = s1_output.initial_channel_hint
    pipeline_state.stages_completed.append("S1")
    pipeline_state.skills_activated.extend([
        "core-mental-model-engine",
        "core-complexity-channel-selector",
        "protocol-single-question-guidance",
        "pipeline-s1-need-diving"
    ])

    # 确认节点: S1→S2
    CALL protocol-confirmation-node(stage="S1→S2", output=s1_output)
    CALL protocol-quality-gate(stage=1, output=s1_output)
    SNAPSHOT pipeline_state.snapshots["S1"] = s1_output

    # ===== 阶段2: 领域分类与消歧 =====
    OUTPUT "--- 阶段 2/8: 领域分类与消歧 ---" TO user

    LOAD_SKILL "pipeline-s2-domain-disambiguation"
    s2_input = {s1_output: s1_output}
    s2_output = EXECUTE pipeline-s2-domain-disambiguation(s2_input)
    # S2内部自动调用: core-domain-classifier, protocol-confirmation-node

    pipeline_state.domain_type = s2_output.domain_profile.primary_domain
    pipeline_state.stages_completed.append("S2")
    pipeline_state.skills_activated.extend([
        "core-domain-classifier",
        "protocol-confirmation-node",
        "pipeline-s2-domain-disambiguation"
    ])

    # 确认节点: S2→S3
    CALL protocol-confirmation-node(stage="S2→S3", output=s2_output)
    CALL protocol-quality-gate(stage=2, output=s2_output)
    SNAPSHOT pipeline_state.snapshots["S2"] = s2_output

    # ===== 通道路由判定 =====
    # 根据S1+S2的输出确定最终通道
    channel = RESOLVE_CHANNEL(s1_output.initial_channel_hint, s2_output.domain_profile)
    pipeline_state.channel = channel
    OUTPUT "[系统] 通道选择: " + channel TO user

    # ===== 阶段3: 链路拆解 =====
    # 快速通道: S3简化为单链路直通
    OUTPUT "--- 阶段 3/8: 链路拆解 ---" TO user

    LOAD_SKILL "pipeline-s3-chain-decomposition"
    s3_input = {s2_output: s2_output, channel: channel}
    s3_output = EXECUTE pipeline-s3-chain-decomposition(s3_input)
    # S3内部自动调用: core-deliverable-backward-engine

    pipeline_state.stages_completed.append("S3")
    pipeline_state.skills_activated.extend([
        "core-deliverable-backward-engine",
        "pipeline-s3-chain-decomposition"
    ])

    # 快速通道跳过S3→S4确认节点，直接衔接
    IF channel != "fast":
        CALL protocol-confirmation-node(stage="S3→S4", output=s3_output)
    CALL protocol-quality-gate(stage=3, output=s3_output)
    SNAPSHOT pipeline_state.snapshots["S3"] = s3_output

    # ===== 阶段4: 交付物锚定 =====
    OUTPUT "--- 阶段 4/8: 交付物锚定 ---" TO user

    LOAD_SKILL "pipeline-s4-deliverable-anchoring"
    s4_input = {s3_output: s3_output, channel: channel}
    s4_output = EXECUTE pipeline-s4-deliverable-anchoring(s4_input)
    # S4内部自动调用: core-deliverable-backward-engine

    pipeline_state.stages_completed.append("S4")
    pipeline_state.skills_activated.extend(["pipeline-s4-deliverable-anchoring"])

    CALL protocol-confirmation-node(stage="S4→S5", output=s4_output)
    CALL protocol-quality-gate(stage=4, output=s4_output)
    SNAPSHOT pipeline_state.snapshots["S4"] = s4_output

    # ===== 阶段5: 架构设计 =====
    # 快速通道: S5简化为单人角色
    OUTPUT "--- 阶段 5/8: 架构设计 ---" TO user

    LOAD_SKILL "pipeline-s5-architecture-design"
    s5_input = {s4_output: s4_output, channel: channel, domain_type: pipeline_state.domain_type}
    s5_output = EXECUTE pipeline-s5-architecture-design(s5_input)
    # S5内部自动调用: core-deliverable-backward-engine, protocol-quality-gate,
    #                  protocol-feedback-loop, protocol-compliance-engine

    pipeline_state.stages_completed.append("S5")
    pipeline_state.skills_activated.extend([
        "protocol-feedback-loop",
        "protocol-compliance-engine",
        "pipeline-s5-architecture-design"
    ])

    # 角色数>=4时触发Team型
    IF s5_output.roles != null AND LENGTH(s5_output.roles) >= 4:
        OUTPUT "[系统] 检测到角色数>=4，启用团队协作模式" TO user
        pipeline_state.team_required = true

    CALL protocol-confirmation-node(stage="S5→S6", output=s5_output)
    CALL protocol-quality-gate(stage=5, output=s5_output)
    SNAPSHOT pipeline_state.snapshots["S5"] = s5_output

    # ===== 阶段6: 工具链匹配 =====
    OUTPUT "--- 阶段 6/8: 工具链匹配 ---" TO user

    LOAD_SKILL "pipeline-s6-toolchain-matching"
    s6_input = {s5_output: s5_output}
    s6_output = EXECUTE pipeline-s6-toolchain-matching(s6_input)
    # S6内部自动调用: core-mental-model-engine
    # S6对每个工具调用 protocol-data-security 进行安全评估

    pipeline_state.stages_completed.append("S6")
    pipeline_state.skills_activated.extend([
        "protocol-data-security",
        "pipeline-s6-toolchain-matching"
    ])

    CALL protocol-confirmation-node(stage="S6→S7", output=s6_output)
    CALL protocol-quality-gate(stage=6, output=s6_output)
    SNAPSHOT pipeline_state.snapshots["S6"] = s6_output

    # ===== 阶段7: 专家包生成 =====
    # 此阶段根据领域类型和通道条件激活L2协议子集和L3适配器
    OUTPUT "--- 阶段 7/8: 专家包生成 ---" TO user

    LOAD_SKILL "pipeline-s7-expert-package-generation"

    # 解析激活矩阵: 根据domain_type × channel确定需要激活的L2协议
    activation_key = pipeline_state.domain_type + "_" + channel + "_S7"
    LOAD activation_map FROM "knowledge/protocol-activation-map.json"
    active_protocols = activation_map.protocol_activation_matrix[activation_key]
    IF active_protocols == null:
        active_protocols = activation_map.protocol_activation_matrix["_fallback"]

    # 确定目标平台，仅激活对应的L3适配器
    target_platform = s1_output.need_portrait._context.目标平台
    platform_adapter = "platform-" + target_platform + "-adapter"
    IF target_platform == "其他" OR target_platform == null:
        platform_adapter = "platform-universal-adapter"

    s7_input = {
        s6_output: s6_output,
        s5_output: s5_output,
        channel: channel,
        domain_type: pipeline_state.domain_type,
        target_platform: target_platform,
        active_protocols: active_protocols,
        platform_adapter: platform_adapter
    }
    s7_output = EXECUTE pipeline-s7-expert-package-generation(s7_input)
    # S7内部按active_protocols自动激活对应L2协议
    # S7内部自动调用platform_adapter生成平台配置

    pipeline_state.stages_completed.append("S7")
    pipeline_state.skills_activated.extend(active_protocols)
    pipeline_state.skills_activated.append(platform_adapter)
    pipeline_state.skills_activated.append("pipeline-s7-expert-package-generation")

    # 知识沉淀
    CALL protocol-knowledge-persistence(stage=7, output=s7_output)

    CALL protocol-confirmation-node(stage="S7→S8", output=s7_output)
    CALL protocol-quality-gate(stage=7, output=s7_output)
    SNAPSHOT pipeline_state.snapshots["S7"] = s7_output

    # ===== 阶段8: 平台执行 =====
    OUTPUT "--- 阶段 8/8: 平台执行 ---" TO user

    LOAD_SKILL "pipeline-s8-platform-execution"
    s8_input = {
        s7_output: s7_output,
        platform_adapter: platform_adapter,
        expert_team_id: expert_team_id
    }
    s8_output = EXECUTE pipeline-s8-platform-execution(s8_input)
    # S8内部自动调用: protocol-error-handling (部署失败时)

    pipeline_state.stages_completed.append("S8")
    pipeline_state.skills_activated.extend([
        "pipeline-s8-platform-execution"
    ])
    IF s8_output.deploy_success == false:
        pipeline_state.skills_activated.append("protocol-error-handling")

    CALL protocol-quality-gate(stage=8, output=s8_output)
    SNAPSHOT pipeline_state.snapshots["S8"] = s8_output

    # ===== 最终交付 =====
    OUTPUT "=== 全域专家团构建完成 ===" TO user
    OUTPUT "共完成 " + LENGTH(pipeline_state.stages_completed) + " 个阶段" TO user
    OUTPUT "共激活 " + LENGTH(pipeline_state.skills_activated) + " 个子skill" TO user
    OUTPUT "使用通道: " + pipeline_state.channel TO user
    OUTPUT "领域类型: " + pipeline_state.domain_type TO user
    OUTPUT "目标平台: " + target_platform TO user

    # 知识沉淀
    CALL protocol-knowledge-persistence(stage="final", output=pipeline_state)

    final_output = {
        expert_team_package: s7_output.expert_package,
        platform_deployed: s8_output.deploy_success,
        pipeline_summary: {
            domain_type: pipeline_state.domain_type,
            channel_used: pipeline_state.channel,
            stages_completed: pipeline_state.stages_completed,
            total_stages: 8,
            skills_activated: DEDUPLICATE(pipeline_state.skills_activated)
        }
    }
    RETURN final_output
```

### 通道路由逻辑

```text
FUNCTION RESOLVE_CHANNEL(initial_hint, domain_profile):
    """
    根据S1初评和S2领域分类的联合结果确定最终通道
    """
    # 用户可升级通道但不可降级（除非明确声明理解风险）
    IF domain_profile.is_regulated == true:
        RETURN "strict"  # 强监管领域强制strict

    IF initial_hint == "fast" AND domain_profile.complexity == "low":
        RETURN "fast"
    ELIF initial_hint == "strict" OR domain_profile.complexity == "high":
        RETURN "strict"
    ELSE:
        RETURN "standard"
```

### L2协议条件激活规则

本编排器在S7阶段根据 `knowledge/protocol-activation-map.json` 中的 `protocol_activation_matrix` 自动激活对应协议子集：

| 领域类型 | 通道 | 激活的L2协议 |
|---------|------|-------------|
| A (内容创作) | fast | quality-gate, output-format |
| A | standard | + compliance-engine, naming-convention |
| A | strict | + data-security, tool-integration |
| B (数据分析) | fast | quality-gate, output-format |
| B | standard | + compliance-engine, naming-convention, tool-integration |
| B | strict | + data-security, error-handling, human-approval |
| C (知识管理) | standard | + automation-trigger |
| C | strict | + data-security, human-approval |
| D (流程自动化) | standard | + automation-trigger, tool-integration |
| D | strict | + data-security, human-approval |
| F (客户服务) | standard | + error-handling, feedback-loop |
| F | strict | + data-security, knowledge-persistence, human-approval |
| _fallback | any | quality-gate, output-format |

### L3适配器激活规则

仅激活目标平台对应的**单个**L3适配器：

| 用户选择的平台 | 激活的适配器 |
|--------------|-------------|
| WorkBuddy | platform-workbuddy-adapter |
| Codex CLI | platform-codex-adapter |
| Hermes Agent | platform-hermes-adapter |
| 飞书 | platform-feishu-adapter |
| n8n | platform-n8n-adapter |
| ComfyUI | platform-comfyui-adapter |
| Coze | platform-coze-adapter |
| Dify | platform-dify-adapter |
| 其他/未确定 | platform-universal-adapter |

### L0/L4全程横贯规则

以下skill在**全程**自动激活，不需要条件判断：

- **L0核心引擎** (6个): 全程内化运行，为所有阶段提供推理基础
  - core-mental-model-engine: 每个阶段都调用
  - core-deliverable-backward-engine: S3/S4/S5/S7调用
  - core-domain-classifier: S2调用
  - core-complexity-channel-selector: S1调用
  - core-state-management-engine: 跨阶段状态管理
  - core-symbol-system: 全程符号一致性

- **L4全局约束** (5个): 全程横贯，任何skill均受约束
  - constraint-mandatory-rules: 21条强制规则不可覆盖
  - constraint-flexible-rules: 11条灵活规则按领域调整
  - constraint-output-format: 14必含章节规范
  - constraint-naming-convention: Agent ID/花名/profession规范
  - constraint-tool-integration: MCP配置/健康检查/降级决策树

### 快速通道简化规则

当channel为"fast"时，以下阶段自动简化：

| 阶段 | 标准模式 | 快速模式 |
|------|---------|---------|
| S3 链路拆解 | 多链路+子链路拆解 | 单链路直通 |
| S5 架构设计 | 多角色+SOP+反馈回路 | 单人角色，跳过SOP |
| S7 协议激活 | 全量协议矩阵 | 仅quality-gate + output-format |
| 确认节点 | 每阶段强确认 | S3→S4跳过确认 |

### 异常处理

```text
FUNCTION HANDLE_PIPELINE_ERROR(error, current_stage):
    """
    任何阶段失败时的异常处理
    """
    LOAD_SKILL "protocol-error-handling"

    error_type = CLASSIFY_ERROR(error)
    SWITCH error_type:
        CASE "validation_error":
            # 回退到当前阶段重试
            RETRY current_stage
        CASE "dependency_missing":
            # 降级到纯提示词模式
            DEGRADE_TO_PROMPT_ONLY(current_stage)
        CASE "platform_deploy_failed":
            # 调用error-handling进行回退
            CALL protocol-error-handling(stage=current_stage, error=error)
            IF RETRYABLE:
                RETRY current_stage
            ELSE:
                OUTPUT "[系统] 平台部署失败，专家包已生成但未部署。您可以手动导入。" TO user
        CASE "user_early_termination":
            # 用户要求紧急终止
            LOAD_SKILL "protocol-early-termination"
            COLLECT_COMPLETED_OUTPUTS()
            FILL_UNCOMPLETED_WITH_MINIMAL()
            OUTPUT "[系统] 已按要求紧急终止，已完成阶段的输出已保存。" TO user
        DEFAULT:
            CALL protocol-error-handling(stage=current_stage, error=error)
```

### 版本迭代触发

当用户在使用已构建的专家团后提出以下信号时，本编排器自动重新启动流程：

- "做不了X" → 回退到S5补充角色能力
- "想要新能力" → 从S1重新开始（需求变更）
- "我想升级" → 从S2开始（通道升级）
- 核心指标低于阈值 → 从S5开始（架构优化）

## Few-shot 示例

### 示例1: 标准流程 - 内容创作团队

**用户**: "我想建个AI专家团帮我运营小红书美食号"

**编排器内部流程**:
1. [S1 需求深潜] 自动加载pipeline-s1-need-diving → 采集9个问题 → 生成需求画像卡
2. [S2 领域消歧] 自动加载pipeline-s2-domain-disambiguation → 确认A型(内容创作) → standard通道
3. [S3 链路拆解] 自动加载pipeline-s3-chain-decomposition → 拆解内容生产链路
4. [S4 交付物锚定] 自动加载pipeline-s4-deliverable-anchoring → 锚定"可发布图文成品"
5. [S5 架构设计] 自动加载pipeline-s5-architecture-design → 设计3角色(选题/创作/发布)
6. [S6 工具链匹配] 自动加载pipeline-s6-toolchain-matching → 匹配WorkBuddy+搜索API
7. [S7 专家包生成] 自动加载pipeline-s7-expert-package-generation → 激活quality-gate+compliance-engine+output-format → 生成WorkBuddy配置
8. [S8 平台执行] 自动加载pipeline-s8-platform-execution → 部署到WorkBuddy

**用户感知**: "我回答了几个问题，然后系统自动帮我建好了专家团"

### 示例2: 快速通道 - 个人财税科普

**用户**: "帮我建个AI专家团，我是做个人财税科普的"

**编排器内部流程**:
1. [S1] 需求深潜 → 3个核心问题 → 快速判定fast通道
2. [S2] 领域消歧 → A型，fast通道确认
3. [S3] 链路拆解 → 简化: 单链路直通
4. [S4] 交付物锚定 → 锚定"可发布文章"
5. [S5] 架构设计 → 简化: 单人角色
6. [S6] 工具链匹配 → WorkBuddy纯提示词
7. [S7] 专家包生成 → 仅quality-gate+output-format → 生成配置
8. [S8] 平台执行 → 部署

**用户感知**: "很快，几个问题就搞定了"

### 示例3: 严格通道 - 医疗知识库

**用户**: "我们医院想建AI专家团帮医生查诊疗指南"

**编排器内部流程**:
1. [S1] 需求深潜 → 完整9问+5-Why → 初评strict
2. [S2] 领域消歧 → C型(知识管理)+强监管 → 强制strict通道
3. [S3] 链路拆解 → 多链路: 检索链+生成链+审核链
4. [S4] 交付物锚定 → 锚定"诊疗建议+风险提示+人工审核"
5. [S5] 架构设计 → 5角色(检索/生成/审核/合规/知识管理) → Team型
6. [S6] 工具链匹配 → RAG+知识库+人工审批接口
7. [S7] 专家包生成 → 激活全部协议: quality-gate+compliance-engine+data-security+human-approval+... → 生成WorkBuddy配置
8. [S8] 平台执行 → 部署+合规验证

**用户感知**: "系统问得很详细，最终帮我们建了一个带审核机制的医疗AI团队"

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://./knowledge/protocol-activation-map.json` — L2协议激活矩阵
- **[static]** `file://./knowledge/stage-routing.json` — 阶段路由配置
- **[dynamic]** `file://./knowledge/orchestrator-state.json` — 编排器运行时状态

## 依赖关系

### L1流程层 (8个，按序执行)
- pipeline-s1-need-diving
- pipeline-s2-domain-disambiguation
- pipeline-s3-chain-decomposition
- pipeline-s4-deliverable-anchoring
- pipeline-s5-architecture-design
- pipeline-s6-toolchain-matching
- pipeline-s7-expert-package-generation
- pipeline-s8-platform-execution

### L0核心引擎 (6个，全程内化)
- core-mental-model-engine
- core-deliverable-backward-engine
- core-domain-classifier
- core-complexity-channel-selector
- core-state-management-engine
- core-symbol-system

### L2协议层 (11个，条件激活)
- protocol-quality-gate (全程)
- protocol-confirmation-node (阶段跳转时)
- protocol-single-question-guidance (S1信息采集)
- protocol-compliance-engine (A/F型+强监管)
- protocol-data-security (strict通道)
- protocol-error-handling (异常时)
- protocol-feedback-loop (B/F型)
- protocol-human-approval (strict通道+强监管)
- protocol-knowledge-persistence (C型+最终沉淀)
- protocol-automation-trigger (D/F型)
- protocol-early-termination (用户终止时)

### L3平台适配层 (9个，仅激活1个)
- platform-workbuddy-adapter / platform-codex-adapter / ... (按用户选择)

### L4全局约束层 (5个，全程横贯)
- constraint-mandatory-rules
- constraint-flexible-rules
- constraint-output-format
- constraint-naming-convention
- constraint-tool-integration

## 重要说明

1. **本skill是唯一入口**: 用户不应直接触发pipeline-s1~s8中的任何一个。所有pipeline skill的trigger_keywords已被弱化，仅本编排器保留全量触发词。
2. **子skill自动加载**: 本编排器通过 `LOAD_SKILL` 指令告诉AI agent在何时加载哪个子skill，子skill加载后按其自身SKILL.md执行。
3. **状态传递**: 编排器通过 `shared_memory` 在阶段间传递上下文，使用 `{expert_team_id}_` 前缀实现命名空间隔离。
4. **用户可中断**: 用户可随时说"跳到输出"触发protocol-early-termination，编排器会收集已完成阶段的输出并用最小输出填充未完成阶段。
5. **通道不可降级**: 用户可升级通道(fast→standard→strict)但不可降级，除非明确声明理解风险。

## 版本

1.0.0

---
*本skill是全域专家团构建skills系统的统一入口编排器，版本1.0.0，日期2026-06-17*
