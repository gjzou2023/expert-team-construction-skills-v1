---
name: team-orchestrator
description: 全域专家团构建系统统一入口。Use when: 用户说"帮我建AI专家团""构建团队"等。自动编排8阶段流程。
---

# 全域专家团总编排器

## 概述

全域专家团构建 skills 系统统一入口。根据用户需求动态构建任意领域专家团（角色定义+协作流程+交付标准），自动完成需求深潜→领域消歧→链路拆解→交付物锚定→架构设计→工具链匹配→专家包生成→平台执行的 8 阶段全流程。

## 执行模式

本 skill 分 8 个阶段执行。**每个阶段开始时，必须先读取对应子 skill 完整指引**：

### 阶段检测

根据对话历史判断当前阶段。首次触发从 S1 开始。

### 阶段执行协议

1. 读取 `references/skills/pipeline-s{N}-*/SKILL.md`
2. 按其指引执行本阶段任务
3. 输出阶段结构化摘要（JSON 格式，~500 tokens）
4. 询问用户确认进入下一阶段

### 阶段清单

| 阶段 | 子 skill | 核心任务 |
|------|---------|---------|
| S1 | pipeline-s1-need-diving | 需求深潜 |
| S2 | pipeline-s2-domain-disambiguation | 领域消歧 |
| S3 | pipeline-s3-chain-decomposition | 链路拆解 |
| S4 | pipeline-s4-deliverable-anchoring | 交付物锚定 |
| S5 | pipeline-s5-architecture-design | 架构设计 |
| S6 | pipeline-s6-toolchain-matching | 工具链匹配 |
| S7 | pipeline-s7-expert-package-generation | 专家包生成 |
| S8 | pipeline-s8-platform-execution | 平台执行 |

### 通道路由

S2 输出 domain_type（A/B/C/D/F）和 channel（fast/standard/strict）。后续阶段根据 channel 调整执行深度。

### L0 核心引擎

每阶段读取对应 `references/skills/core-*`，根据任务类型激活对应核心引擎。

### L2 协议激活

读取 `references/knowledge/protocol-activation-map.json` 确定激活子集。S7 阶段调用全部激活的 L2 协议。

### L3 平台适配

S7 阶段根据用户选择的平台，读取 `references/skills/platform-{platform}-adapter/SKILL.md`。

### L4 全局约束（核心规则摘要）

20 条强制规则不可覆盖，11 条灵活规则依情况启用。完整规则见各 `constraint-*` 子 skill。

**核心强制规则**：交付物优先 → MECE 强制 → 合规不可绕过 → 平台可执行 → 分线强制 → 阶段跳转约束 → 字段追踪强制 → 单问规则 → 规范优先级 → 数据安全强制

### 快速通道

当用户角色数 ≤ 2 时，启用快速通道：保留核心交付物与兜底方案，跳过或内联低风险阶段。

### 异常处理

任何阶段失败时，调用 `references/skills/protocol-error-handling/SKILL.md` 执行降级策略。

### 版本迭代触发信号

当用户表达"做不了X"、"想要新能力"、"我想升级"或核心指标低于阈值时，重新触发 S1。

## 注意事项

- **必须**按序执行 S1→S8，不可跳过
- 每阶段**必须**先读取完整子 skill 指引再执行
- 阶段输出必须结构化（JSON 摘要）
- 用户确认后才进入下一阶段

## 完整子 skill 参考

完整的 39 个子 skill 原文见 `references/skills/` 目录。
完整的共享知识资源见 `references/knowledge/` 目录。

## 原始编排逻辑（完整伪代码）

以下为本 skill 的完整编排伪代码，执行时严格遵循：

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
    CALL protocol-single-question-guidance(stage="S1", question={"type":"announcement","text":"阶段1/8: 需求深潜即将开始","options":null})
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

    # 确认节点: S1→S2 (node_id对齐protocol-confirmation-node的STRONG_CONFIRM_NODES)
    CALL protocol-confirmation-node(node_id="stage_1_end", content=s1_output, current_stage="S1")
    CALL protocol-quality-gate(stage=1, output=s1_output)
    SNAPSHOT pipeline_state.snapshots["S1"] = s1_output

    # ===== 提取target_platform（S6/S7/S8都需要，提前定义避免使用先于定义） =====
    target_platform = s1_output.need_portrait._context.目标平台 IF EXISTS ELSE "workbuddy"
    platform_adapter = "platform-" + target_platform + "-adapter"
    IF target_platform == "其他" OR target_platform == null:
        platform_adapter = "platform-universal-adapter"

    # ===== 阶段2: 领域分类与消歧 =====
    OUTPUT "--- 阶段 2/8: 领域分类与消歧 ---" TO user

    LOAD_SKILL "pipeline-s2-domain-disambiguation"
    # 字段名对齐S2 input_schema: s1_outputs(复数) + domain_suggestion(可选,S2内部生成)
    s2_input = {"s1_outputs": s1_output, "domain_suggestion": null}
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
    CALL protocol-confirmation-node(node_id="stage_2_end", content=s2_output, current_stage="S2")
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
    # 字段名对齐S3 input_schema: s2_outputs(复数) + deliverable_candidates + channel + s1_context
    # deliverable_candidates从S1需求画像和S2领域画像推导
    deliverable_candidates = []
    expected_outcome = s1_output.need_portrait._context.期望成果 IF EXISTS ELSE ""
    DOMAIN_DEFAULT_DELIVERABLES = {
        "A": ["图文笔记", "深度文章", "用户互动话术"],
        "B": ["服务交付物", "进度报告", "验收文档"],
        "C": ["知识条目", "检索索引", "知识更新日志"],
        "D": ["自动化流程配置", "执行日志", "异常报告"],
        "F": ["客服回复模板", "FAQ更新", "满意度报告"]
    }
    IF expected_outcome CONTAINS "图文" OR expected_outcome CONTAINS "笔记":
        APPEND "图文笔记" TO deliverable_candidates
    IF expected_outcome CONTAINS "文章":
        APPEND "深度文章" TO deliverable_candidates
    IF expected_outcome CONTAINS "视频":
        APPEND "视频脚本" TO deliverable_candidates
    IF expected_outcome CONTAINS "报表" OR expected_outcome CONTAINS "报告":
        APPEND "数据报表" TO deliverable_candidates
    IF LENGTH(deliverable_candidates) == 0:
        deliverable_candidates = DOMAIN_DEFAULT_DELIVERABLES[pipeline_state.domain_type]

    s3_input = {
        "s2_outputs": s2_output,
        "deliverable_candidates": deliverable_candidates,
        "channel": channel,
        "s1_context": {
            "team_size": s1_output.need_portrait._context.团队规模,
            "ai_experience": s1_output.need_portrait._context.AI经验,
            "target_platform": s1_output.need_portrait._context.目标平台
        }
    }
    s3_output = EXECUTE pipeline-s3-chain-decomposition(s3_input)
    # S3内部自动调用: core-deliverable-backward-engine

    pipeline_state.stages_completed.append("S3")
    pipeline_state.skills_activated.extend([
        "core-deliverable-backward-engine",
        "pipeline-s3-chain-decomposition"
    ])

    # 快速通道跳过S3→S4确认节点，直接衔接
    IF channel != "fast":
        CALL protocol-confirmation-node(node_id="stage_3_workflow", content=s3_output, current_stage="S3")
    CALL protocol-quality-gate(stage=3, output=s3_output)
    SNAPSHOT pipeline_state.snapshots["S3"] = s3_output

    # ===== 阶段4: 交付物锚定 =====
    OUTPUT "--- 阶段 4/8: 交付物锚定 ---" TO user

    LOAD_SKILL "pipeline-s4-deliverable-anchoring"
    # 字段名对齐S4 input_schema: s3_outputs(复数) + s2_outputs(复数)
    s4_input = {
        "s3_outputs": s3_output,
        "s2_outputs": s2_output,
        "channel": channel
    }
    s4_output = EXECUTE pipeline-s4-deliverable-anchoring(s4_input)
    # S4内部自动调用: core-deliverable-backward-engine

    pipeline_state.stages_completed.append("S4")
    pipeline_state.skills_activated.extend(["pipeline-s4-deliverable-anchoring"])

    CALL protocol-confirmation-node(node_id="stage_4_end", content=s4_output, current_stage="S4")
    CALL protocol-quality-gate(stage=4, output=s4_output)
    SNAPSHOT pipeline_state.snapshots["S4"] = s4_output

    # ===== 阶段5: 架构设计 =====
    # 快速通道: S5简化为单人角色
    OUTPUT "--- 阶段 5/8: 架构设计 ---" TO user

    LOAD_SKILL "pipeline-s5-architecture-design"
    # 字段名对齐S5 input_schema: s4_outputs(复数) + domain_type + channel
    s5_input = {
        "s4_outputs": s4_output,
        "channel": channel,
        "domain_type": pipeline_state.domain_type
    }
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

    CALL protocol-confirmation-node(node_id="stage_5_end", content=s5_output, current_stage="S5")
    CALL protocol-quality-gate(stage=5, output=s5_output)
    SNAPSHOT pipeline_state.snapshots["S5"] = s5_output

    # ===== 阶段6: 工具链匹配 =====
    OUTPUT "--- 阶段 6/8: 工具链匹配 ---" TO user

    LOAD_SKILL "pipeline-s6-toolchain-matching"
    # 字段名对齐S6 input_schema: s5_outputs(复数) + platform
    s6_input = {
        "s5_outputs": s5_output,
        "platform": target_platform
    }
    s6_output = EXECUTE pipeline-s6-toolchain-matching(s6_input)
    # S6内部自动调用: core-mental-model-engine
    # S6对每个工具调用 protocol-data-security 进行安全评估

    pipeline_state.stages_completed.append("S6")
    pipeline_state.skills_activated.extend([
        "protocol-data-security",
        "pipeline-s6-toolchain-matching"
    ])

    CALL protocol-confirmation-node(node_id="stage_6_end", content=s6_output, current_stage="S6")
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

    # 确定目标平台，仅激活对应的L3适配器（target_platform和platform_adapter已在S1后提前定义）
    # target_platform = s1_output.need_portrait._context.目标平台  ← 已提前到S1之后定义
    # platform_adapter = "platform-" + target_platform + "-adapter"  ← 已提前到S1之后定义
    # IF target_platform == "其他" OR target_platform == null:       ← 已提前到S1之后处理
    #     platform_adapter = "platform-universal-adapter"

    # 字段名对齐S7 input_schema: s5_outputs + s6_outputs + platform + team_type + activation_context
    team_type = "team" IF LENGTH(s5_output.roles) >= 4 ELSE "agent"
    s7_input = {
        "s5_outputs": s5_output,
        "s6_outputs": s6_output,
        "platform": target_platform,
        "team_type": team_type,
        "activation_context": {
            "domain_type": pipeline_state.domain_type,
            "secondary_domains": s2_output.domain_profile.secondary_domains IF EXISTS ELSE [],
            "market": s1_output.need_portrait._context.目标市场,
            "platform": target_platform,
            "is_regulated": s2_output.domain_profile.is_regulated IF EXISTS ELSE false,
            "compliance_requirements": s2_output.compliance_activation_map
        }
    }
    s7_output = EXECUTE pipeline-s7-expert-package-generation(s7_input)
    # S7内部按active_protocols自动激活对应L2协议
    # S7内部自动调用platform_adapter生成平台配置

    pipeline_state.stages_completed.append("S7")
    pipeline_state.skills_activated.extend(active_protocols)
    pipeline_state.skills_activated.append(platform_adapter)
    pipeline_state.skills_activated.append("pipeline-s7-expert-package-generation")

    # 知识沉淀 (对齐knowledge-persistence input_schema: decision_type + content + metadata)
    CALL protocol-knowledge-persistence(decision_type="design", content=s7_output, metadata={"stage":7, "expert_team_id":expert_team_id})

    CALL protocol-confirmation-node(node_id="stage_7_end", content=s7_output, current_stage="S7")
    CALL protocol-quality-gate(stage=7, output=s7_output)
    SNAPSHOT pipeline_state.snapshots["S7"] = s7_output

    # ===== 阶段8: 平台执行 =====
    OUTPUT "--- 阶段 8/8: 平台执行 ---" TO user

    LOAD_SKILL "pipeline-s8-platform-execution"
    # 字段名对齐S8 input_schema: s7_outputs(复数) + platform
    s8_input = {
        "s7_outputs": s7_output,
        "platform": target_platform,
        "platform_adapter": platform_adapter,
        "expert_team_id": expert_team_id
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

    # 知识沉淀 (对齐knowledge-persistence input_schema)
    CALL protocol-knowledge-persistence(decision_type="execution", content=pipeline_state, metadata={"stage":"final", "expert_team_id":expert_team_id})

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
    字段路径与stage-routing.json的channel_resolution.rules一致
    """
    # 从domain_profile提取顶层变量（与stage-routing.json字段路径一致）
    is_regulated = domain_profile.is_regulated IF EXISTS ELSE false
    complexity = domain_profile.complexity IF EXISTS ELSE "medium"

    # 用户可升级通道但不可降级（除非明确声明理解风险）
    IF is_regulated == true:
        RETURN "strict"  # 强监管领域强制strict

    IF initial_hint == "fast" AND complexity == "low":
        RETURN "fast"
    ELIF initial_hint == "strict" OR complexity == "high":
        RETURN "strict"
    ELSE:
        RETURN "standard"
```

### L2协议条件激活规则

本编排器在S7阶段根据 `knowledge/protocol-activation-map.json` 中的 `protocol_activation_matrix` 自动激活对应协议子集：

| 领域类型 | 通道 | 激活的L2协议（完整Skill ID，与activation-map.json一致） |
|---------|------|-------------|
| A | fast | protocol-quality-gate, constraint-output-format |
| A | standard | protocol-quality-gate, protocol-compliance-engine, constraint-output-format, constraint-naming-convention |
| A | strict | protocol-quality-gate, protocol-compliance-engine, protocol-data-security, constraint-output-format, constraint-naming-convention, constraint-tool-integration |
| B | fast | protocol-quality-gate, constraint-output-format |
| B | standard | protocol-quality-gate, protocol-compliance-engine, constraint-output-format, constraint-naming-convention, constraint-tool-integration |
| B | strict | protocol-quality-gate, protocol-compliance-engine, protocol-data-security, protocol-error-handling, constraint-output-format, constraint-naming-convention, constraint-tool-integration, protocol-human-approval |
| C | fast | protocol-quality-gate, constraint-output-format |
| C | standard | protocol-quality-gate, protocol-compliance-engine, constraint-output-format, constraint-naming-convention, constraint-tool-integration, protocol-automation-trigger |
| C | strict | protocol-quality-gate, protocol-compliance-engine, protocol-data-security, constraint-output-format, constraint-naming-convention, constraint-tool-integration, protocol-human-approval |
| D | fast | protocol-quality-gate, constraint-output-format |
| D | standard | protocol-quality-gate, constraint-output-format, constraint-naming-convention, protocol-automation-trigger, constraint-tool-integration |
| D | strict | protocol-quality-gate, protocol-compliance-engine, protocol-data-security, constraint-output-format, constraint-naming-convention, constraint-tool-integration, protocol-human-approval |
| F | fast | protocol-quality-gate, constraint-output-format, constraint-naming-convention |
| F | standard | protocol-quality-gate, protocol-compliance-engine, constraint-output-format, constraint-naming-convention, protocol-error-handling, protocol-feedback-loop |
| F | strict | protocol-quality-gate, protocol-compliance-engine, protocol-data-security, protocol-error-handling, protocol-feedback-loop, constraint-output-format, constraint-naming-convention, constraint-tool-integration, protocol-human-approval, protocol-knowledge-persistence |
| _fallback | any | protocol-quality-gate, constraint-output-format |

> 注：此表与 knowledge/protocol-activation-map.json 完全一致，修改时须同步更新两处。

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

### L0/L4按需横贯规则

以下skill**按需激活**（非全程内化），根据阶段任务条件激活：

- **L0核心引擎** (6个): 按需激活，避免token爆炸
  - core-mental-model-engine: 仅在S1/S5/S7阶段需要复杂推理时激活
  - core-deliverable-backward-engine: 仅在S3/S4/S5阶段激活
  - core-domain-classifier: 仅在S2阶段激活
  - core-complexity-channel-selector: 仅在S1/S2阶段激活
  - core-state-management-engine: 在阶段跳转和回退时激活
  - core-symbol-system: 仅在输出格式校验时激活

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
        CASE "user_requirement_change":
            # 用户中途修改需求
            OUTPUT "[系统] 检测到需求变更，正在评估影响范围..." TO user
            change_scope = ANALYZE_CHANGE_SCOPE(error.new_requirement, pipeline_state)
            IF change_scope.affects_domain_type:
                OUTPUT "[系统] 需求变更影响领域分类，回退到S2重新执行" TO user
                ROLLBACK_TO("S2")
                RE_EXECUTE_FROM("S2")
            ELIF change_scope.affects_deliverables:
                OUTPUT "[系统] 需求变更影响交付物定义，回退到S4重新执行" TO user
                ROLLBACK_TO("S4")
                RE_EXECUTE_FROM("S4")
            ELSE:
                OUTPUT "[系统] 需求变更较小，在当前阶段内调整" TO user
                RETRY current_stage WITH error.new_requirement
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
