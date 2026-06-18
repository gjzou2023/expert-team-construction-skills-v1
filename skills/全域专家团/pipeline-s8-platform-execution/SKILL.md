---
name: pipeline-s8-platform-execution
id: "pipeline-s8-platform-execution"
layer: "L1"
name_zh: "阶段八：平台执行"
name_en: "Stage 8: Platform Execution"
version: "1.1.0"
description: 平台注册/部署指导、验证测试(含合规测试词库+分级失效判定)、交付确认(含迭代路径说明)。
agent_created: true
trigger_keywords: ["S8执行", "平台部署", "验证测试", "上线交付", "迭代路径"]
dependencies: ["core-mental-model-engine"]
---

# 阶段八：平台执行 (Stage 8: Platform Execution)

> **层级**: L1 | **版本**: 1.1.0 | **ID**: `pipeline-s8-platform-execution`
> **编排关系**: 本skill由 `team-orchestrator` 自动加载执行，用户不应直接触发。承接 `pipeline-s7-expert-package-generation` 的输出，完成后整个8阶段流程结束，交付最终专家包。

## 概述

平台注册/部署指导、验证测试(含合规测试词库+分级失效判定)、交付确认(含迭代路径说明)。

## 触发条件

当检测到以下关键词或场景时自动激活：部署, 注册, 上线, 执行, 验证, 测试

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s7_outputs": {
      "type": "object",
      "description": "S7专家包输出"
    },
    "platform": {
      "type": "string"
    }
  },
  "required": [
    "s7_outputs",
    "platform"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "execution_result": {
      "type": "object"
    },
    "delivery_confirmation": {
      "type": "object"
    },
    "rollback_snapshot": {
      "type": "object"
    }
  },
  "required": [
    "execution_result",
    "delivery_confirmation",
    "rollback_snapshot"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)平台注册/部署指导(8.1)→(2)验证测试(8.2-8.5,含合规测试词库)→(3)交付确认(8.6,含迭代路径说明)→(4)输出交付确认单。验证测试分级失效判定：完全通过→正常使用;部分失效(非核心功能)→标注+提供修复方案;核心功能失效→阻断,返回S7修复。版本迭代触发信号：用户主动可感知事件(用户说'做不了X'/'想要新能力'/'我想升级')。

## Few-shot 示例

### 示例1: 正常流程 - WorkBuddy部署A型内容团队

**输入**:
```json
{
  "s7_outputs": {
    "expert_package": {
      "overview": "ExpertTeam_小食光内容团队_v1.0.0",
      "platform_config": {
        "workbuddy": {
          "roles": ["content-strategist", "compliance-reviewer"],
          "global_mechanisms": {"quality_gate": "pre_publish_review"}
        }
      }
    }
  },
  "platform": "workbuddy"
}
```

**输出**:
```json
{
  "execution_result": {
    "platform": "workbuddy",
    "status": "🟦 创建成功",
    "deployed_roles": ["content-strategist", "compliance-reviewer"],
    "deployed_mechanisms": ["quality_gate", "compliance"],
    "test_results": {
      "content_generation": "✅ 通过",
      "compliance_check": "✅ 通过",
      "publishing_pipeline": "✅ 通过"
    },
    "issues": []
  },
  "delivery_confirmation": {
    "delivery_status": "ready_for_use",
    "iteration_path": "v1.0.0→v1.1.0(月度优化)→v2.0.0(功能扩展)",
    "user_handbook": "每天09:00自动触发晨会，内容生成后自动合规审查，通过后发布"
  },
  "rollback_snapshot": {
    "snapshot_id": "snap_20260616_v1.0.0",
    "rollback_to": "s7_expert_package_generation",
    "trigger": "用户发现角色分工不合理时可以回退"
  }
}
```

### 示例2: 异常流程 - Dify部署F型客服(部分失效)

**输入**:
```json
{
  "s7_outputs": {
    "expert_package": {
      "overview": "ExpertTeam_智能客服_v1.0.0",
      "platform_config": {
        "dify": {
          "roles": ["triage-agent", "senior-service-agent", "compliance-guardian"],
          "global_mechanisms": {"compliance": "4.1_4.2_4.3_4.4_4.5_full"}
        }
      }
    }
  },
  "platform": "dify"
}
```

**输出**:
```json
{
  "execution_result": {
    "platform": "dify",
    "status": "🟧 部分成功（需手动配置）",
    "deployed_roles": ["triage-agent", "senior-service-agent"],
    "failed_roles": ["compliance-guardian"],
    "test_results": {
      "triage_flow": "✅ 通过",
      "senior_response": "✅ 通过",
      "compliance_check": "❌ Dify工作流不支持自动合规审查节点"
    },
    "issues": [
      "compliance-guardian: Dify无内置合规引擎，需采用webhook回调或改用纯提示词兜底"
    ],
    "remediation": "采用纯提示词兜底：在senior-service-agent的提示词中嵌入合规检查规则，降级为手工合规"
  },
  "delivery_confirmation": {
    "delivery_status": "needs_manual_setup",
    "iteration_path": "当前版本用纯提示词合规→v1.1.0对接外部合规API",
    "user_handbook": "客服回复前请确认合规规则已加载，高级问题升级时需人工审核"
  },
  "rollback_snapshot": {
    "snapshot_id": "snap_20260616_dify_v1.0.0",
    "rollback_to": "s7_expert_package_generation",
    "trigger": "合规能力不足时可返回S7重新设计"
  }
}
```

### 示例3: 快速通道 - 财税科普单人Agent交付

**输入**:
```json
{
  "s7_outputs": {
    "expert_package": {
      "overview": "Expert_财税科普号_v1.0.0(fast)",
      "platform_config": {
        "workbuddy": {
          "single_agent_prompt": "你是一个财税科普内容创作者..."
        }
      }
    }
  },
  "platform": "workbuddy"
}
```

**输出**:
```json
{
  "execution_result": {
    "platform": "workbuddy",
    "status": "🟦 创建成功（快速通道）",
    "deployed_roles": ["solo-operator"],
    "test_results": {
      "content_generation": "✅ 通过",
      "compliance_self_check": "✅ 通过（内置规则）"
    },
    "issues": []
  },
  "delivery_confirmation": {
    "delivery_status": "ready_for_use",
    "iteration_path": "v1.0.0→v1.1.0(新增图表生成能力)→v2.0.0(多平台分发)",
    "user_handbook": "直接输入选题，AI自动生成财税科普内容；每日1篇，确保数据准确"
  },
  "rollback_snapshot": {
    "snapshot_id": "snap_20260616_tax_fast_v1.0.0",
    "rollback_to": "s1_need_diving",
    "trigger": "内容质量不满意可回到需求阶段重来"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://pipeline/stage-8-rules` — 阶段8执行规则
- **[dynamic]** `file://pipeline/stage-8-state` — 阶段8运行时状态

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_pipeline_s8_platform_execution(input):
    # ===== 阶段八：平台执行 - 入口校验 =====
    ASSERT input.s7_outputs EXISTS
    ASSERT input.platform IS NOT EMPTY
    LOAD context_inheritance FROM s7

    s7_data = input.s7_outputs
    platform = input.platform
    expert_package = s7_data.expert_package
    execution_plan = s7_data.execution_plan

    # ===== 步骤1: 目标平台注册/部署执行 =====
    deployment_result = {}
    IF platform == "workbuddy":
        # WorkBuddy: 创建Agent/Team配置
        FOR role IN expert_package["02_角色定义"]:
            deploy_status = CALL workbuddy_create_agent(role.platform_config)
            IF deploy_status == "success":
                APPEND {"role": role.agent_id, "status": "🟦 创建成功"} TO deployment_result.roles
            ELSE:
                APPEND {"role": role.agent_id, "status": "🟥 创建失败", "error": deploy_status.error} TO deployment_result.roles
        # 部署全局机制
        FOR mechanism IN expert_package["07_质量门控"].mechanisms:
            mechanism_status = CALL workbuddy_deploy_mechanism(mechanism)
            APPEND {"mechanism": mechanism.name, "status": mechanism_status} TO deployment_result.mechanisms

    ELIF platform == "dify":
        # Dify: 创建工作流+知识库
        workflow_status = CALL dify_create_workflow(expert_package["04_SOP编排"])
        IF workflow_status == "success":
            APPEND {"component": "workflow", "status": "🟦 创建成功"} TO deployment_result.components
        # 导入知识库
        FOR knowledge IN expert_package["11_知识资产沉淀"]:
            kb_status = CALL dify_import_knowledge(knowledge)
            APPEND {"knowledge": knowledge.name, "status": kb_status} TO deployment_result.knowledge

    ELIF platform == "coze":
        # Coze: 创建Bot+插件+知识库
        bot_status = CALL coze_create_bot(expert_package)
        APPEND {"component": "bot", "status": bot_status} TO deployment_result.components
        FOR plugin IN expert_package["12_工具链配置"].integration_specs:
            plugin_status = CALL coze_install_plugin(plugin)
            APPEND {"plugin": plugin.name, "status": plugin_status} TO deployment_result.plugins

    ELIF platform IN ["feishu", "n8n", "comfyui", "codex", "hermes"]:
        # 其他平台: 生成对应格式的配置文件
        config_file = CALL generate_platform_config(platform, expert_package)
        deployment_result.config_file = config_file
        deployment_result.instructions = GENERATE_DEPLOYMENT_INSTRUCTIONS(platform)

    # ===== 步骤2: 执行结果验证5项检查 =====
    VERIFICATION_CHECKS = [
        "功能完整性检查",    # 所有核心功能是否可执行
        "合规性检查",        # 合规协议是否正确激活
        "数据安全检查",      # 数据流向是否符合安全规则
        "角色协作检查",      # 角色间数据流是否通畅
        "降级方案检查"       # 工具降级时是否能正常工作
    ]
    verification_results = {}
    FOR check IN VERIFICATION_CHECKS:
        result = EXECUTE_VERIFICATION_CHECK(check, expert_package, platform)
        verification_results[check] = result

    # ===== 步骤3: 失败修复流程 =====
    failed_checks = FILTER(verification_results, result -> result.status == "FAILED")
    IF LENGTH(failed_checks) > 0:
        FOR failed IN failed_checks:
            IF failed.check == "功能完整性检查" AND failed.is_core_function:
                # 核心功能失效→阻断，返回S7修复
                RAISE "🔴 核心功能验证失败: " + failed.details + " → 返回S7修复"
            ELIF failed.check == "功能完整性检查" AND NOT failed.is_core_function:
                # 非核心功能失效→标注+提供修复方案
                APPEND {
                    "check": failed.check,
                    "status": "🟧 部分失效(非核心)",
                    "remediation": failed.suggested_fix
                } TO deployment_result.issues
            ELIF failed.check == "合规性检查":
                # 合规失败→阻断，必须修复
                FIX = CALL protocol-compliance-engine.remediate(failed, expert_package)
                IF FIX.success:
                    RE_RUN_VERIFICATION(failed.check)
                ELSE:
                    RAISE "🔴 合规修复失败: " + failed.details
            ELIF failed.check == "数据安全检查":
                # 数据安全失败→阻断，必须修复
                FIX = CALL DATA_SECURITY_FIX(failed, expert_package)
                ASSERT FIX.success
            ELIF failed.check IN ["角色协作检查", "降级方案检查"]:
                # 可降级处理
                APPEND {
                    "check": failed.check,
                    "status": "🟧 需手动配置",
                    "workaround": failed.suggested_workaround
                } TO deployment_result.issues

    # ===== 步骤4: ReAct循环修复 =====
    max_react_rounds = 3
    react_round = 0
    WHILE LENGTH(failed_checks) > 0 AND react_round < max_react_rounds:
        react_round = react_round + 1
        # Reason: 分析失败原因
        root_cause = ANALYZE_ROOT_CAUSE(failed_checks)
        # Action: 执行修复
        fix_result = EXECUTE_FIX(root_cause, expert_package, platform)
        # Observe: 重新验证
        FOR failed IN failed_checks:
            recheck_result = EXECUTE_VERIFICATION_CHECK(failed.check, expert_package, platform)
            IF recheck_result.status == "PASSED":
                REMOVE failed FROM failed_checks
            ELSE:
                UPDATE failed WITH recheck_result
        IF LENGTH(failed_checks) == 0:
            BREAK
    IF react_round >= max_react_rounds AND LENGTH(failed_checks) > 0:
        # 超过最大修复轮次，转为人工处理
        APPEND {
            "status": "🟥 自动修复超限",
            "remaining_issues": failed_checks,
            "action": "请人工介入修复以上问题"
        } TO deployment_result.issues

    # ===== 步骤5: 交付确认 =====
    delivery_confirmation = {}
    IF LENGTH(deployment_result.issues) == 0:
        delivery_confirmation.delivery_status = "ready_for_use"
    ELIF ANY(deployment_result.issues, i -> i.status CONTAINS "🔴"):
        delivery_confirmation.delivery_status = "blocked"
    ELSE:
        delivery_confirmation.delivery_status = "needs_manual_setup"

    # ===== 步骤6: 版本迭代管理 =====
    delivery_confirmation.iteration_path = GENERATE_ITERATION_PATH(domain_type, platform)
    # 版本迭代触发信号：用户主动可感知事件
    ITERATION_TRIGGERS = [
        "用户说'做不了X'",
        "用户说'想要新能力'",
        "用户说'我想升级'",
        "核心指标持续低于阈值"
    ]
    delivery_confirmation.iteration_triggers = ITERATION_TRIGGERS
    delivery_confirmation.user_handbook = GENERATE_USER_HANDBOOK(expert_package, platform)

    # ===== 步骤7: 回滚快照 =====
    rollback_snapshot = {}
    rollback_snapshot.snapshot_id = "snap_" + CURRENT_DATE + "_" + platform + "_v1.0.0"
    rollback_snapshot.rollback_to = "s7_expert_package_generation"
    rollback_snapshot.trigger = "用户发现角色分工不合理/核心功能异常时可回退"
    rollback_snapshot.expert_package_snapshot = CLONE(expert_package)

    # ===== 质量门控 =====
    CALL protocol-quality-gate(stage=8, output={
        "execution_result": deployment_result,
        "delivery_confirmation": delivery_confirmation
    })
    ASSERT deployment_result IS_NOT_EMPTY
    ASSERT delivery_confirmation.delivery_status IN ["ready_for_use", "needs_manual_setup", "blocked"]

    # ===== 产出输出 =====
    output = BUILD_output_according_to_output_schema({
        "execution_result": deployment_result,
        "delivery_confirmation": delivery_confirmation,
        "rollback_snapshot": rollback_snapshot
    })
    RETURN output
```

## 流程终结

> 本阶段为8阶段流程的最后一环。完成后，`team-orchestrator` 输出最终交付总结（领域类型/通道/已完成阶段/已激活skill列表）。
> 如部署失败，自动调用 `protocol-error-handling` 进行回退处理。
> 用户可随时通过"跳到输出"触发 `protocol-early-termination` 紧急终止流程。

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
