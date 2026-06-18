---
name: protocol-confirmation-node
id: "protocol-confirmation-node"
layer: "L2"
name_zh: "确认节点管理协议"
name_en: "Confirmation Node Protocol"
version: "1.1.0"
description: 管理强确认/软确认节点，检查阶段跳转5项条件，特别处理Q9平台确认。
agent_created: true
trigger_keywords: ["protocol-confirmation-node", "确认节点协议", "L2确认"]
dependencies: ["core-state-management-engine"]
---

# 确认节点管理协议 (Confirmation Node Protocol)

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-confirmation-node`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

管理强确认/软确认节点，检查阶段跳转5项条件，特别处理Q9平台确认。

## 触发条件

当检测到以下关键词或场景时自动激活：确认, 强确认, 阶段跳转, Q9, 批准

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "node_id": {
      "type": "string"
    },
    "content": {
      "type": "object"
    },
    "current_stage": {
      "type": "string"
    },
    "stage": {
      "type": "string",
      "description": "向后兼容：编排器使用的阶段跳转标识(如S1→S2)，内部映射到node_id"
    }
  },
  "required": [
    "node_id",
    "content"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "confirmed": {
      "type": "boolean"
    },
    "correction_required": {
      "type": "boolean"
    },
    "transition_allowed": {
      "type": "boolean"
    }
  },
  "required": [
    "confirmed",
    "transition_allowed"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

强确认节点必须等待用户明确确认；软确认节点默认继续但允许用户反对；阶段跳转前检查用户确认、必填完整、无歧义、无待修正、平台可行。

## 详细执行逻辑

```text
FUNCTION execute_protocol_confirmation_node(input):
    ASSERT input.node_id IS NOT EMPTY
    ASSERT input.content IS NOT EMPTY

    // === 阶段跳转标识到 node_id 的映射（向后兼容编排器的stage参数） ===
    STAGE_TO_NODE_ID = {
        "S1→S2": "stage_1_end",
        "S2→S3": "stage_2_end",
        "S3→S4": "stage_3_workflow",
        "S4→S5": "stage_4_end",
        "S5→S6": "stage_5_end",
        "S6→S7": "stage_6_tools",
        "S7→S8": "stage_7_end"
    }
    // 如果传入的是阶段跳转标识（如"S1→S2"），映射到node_id
    IF input.node_id IN KEYS(STAGE_TO_NODE_ID):
        input.node_id = STAGE_TO_NODE_ID[input.node_id]

    // === 强确认8个 + 软确认2个（与stage-routing.json的confirmation_required一致） ===
    STRONG_CONFIRM_NODES = [
        "stage_1_end",       // S1需求确认（stage-routing: confirmation_required=true）
        "stage_2_end",       // S2消歧结束：领域类型+用户画像确认
        "stage_4_end",       // S4交付物锚定结束：交付物+通道确认
        "stage_5_end",       // S5角色架构设计结束：角色定义+MECE校验确认
        "stage_6_end",       // S6工具链确认（stage-routing: confirmation_required=true）
        "stage_7_end",       // S7四步确认门结束：最终配置确认
        "Q9_platform",       // Q9平台变更确认(特殊处理)
        "stage_2_ambiguity"  // S2存在歧义时的消歧确认
    ]
    SOFT_CONFIRM_NODES = [
        "stage_3_workflow",  // S3工作流设计（stage-routing: confirmation_required=false）
        "stage_8_deploy"     // S8平台执行（stage-routing: confirmation_required=false）
    ]

    confirmed = false
    correction_required = false
    transition_allowed = false

    // === 第一步：判断确认节点类型 ===
    IF input.node_id IN STRONG_CONFIRM_NODES:
        // 强确认：必须等待用户明确确认
        OUTPUT input.content
        OUTPUT "回复'确认'继续，'修改'调整，'取消'中止。"

        user_response = WAIT_FOR_EXPLICIT_CONFIRMATION()

        IF user_response == "confirmed":
            confirmed = true
            correction_required = false
        ELIF user_response == "modified" OR user_response == "correction":
            confirmed = false
            correction_required = true
            // 回退修正
            CALL core-state-management-engine.rollback(input.current_stage)
            RE_EXECUTE(input.current_stage)
        ELIF user_response == "rejected" OR user_response == "cancelled":
            confirmed = false
            correction_required = false
            HALT_OUTPUT()

    ELIF input.node_id IN SOFT_CONFIRM_NODES:
        // 软确认：默认继续但允许用户反对
        confirmed = true
        correction_required = false
        OUTPUT "软确认：" + SUMMARIZE(input.content) + "。如有异议回复'等等'停止。"

        // 非阻塞等待(限时)
        IF USER_OBJECTS_WITHIN(GRACE_PERIOD):
            confirmed = false
            correction_required = true
            CALL core-state-management-engine.rollback(input.current_stage)
            RE_EXECUTE(input.current_stage)

    ELSE:
        // 未知节点默认软确认
        confirmed = true
        correction_required = false

    // === 第二步：5项跳转条件检查 ===
    transition_checks = {}
    transition_checks.user_confirmed = user_confirmed_output(input.current_stage)
    transition_checks.required_info = all_required_info_collected(input.current_stage)
    transition_checks.no_ambiguity = no_unresolved_ambiguity(input.current_stage)
    transition_checks.no_corrections = no_pending_corrections(input.current_stage)
    transition_checks.platform_feasible = platform_feasibility_verified(input.current_stage)

    IF ALL_VALUES_TRUE(transition_checks):
        transition_allowed = true
    ELSE:
        transition_allowed = false
        // 列出未满足条件
        FOR check_name, check_result IN transition_checks:
            IF check_result == false:
                OUTPUT "跳转条件未满足: " + check_name

    // === 第三步：Q9平台变更特殊处理 ===
    IF input.node_id == "Q9_platform":
        // Q9平台确认：展示平台变更后果
        platform_change_consequence = COMPUTE_PLATFORM_CHANGE_CONSEQUENCE(input.content)
        OUTPUT "⚠️ 平台变更后果："
        OUTPUT platform_change_consequence.impact_description
        OUTPUT platform_change_consequence.data_migration_needed
        OUTPUT platform_change_consequence.feature_diff

        // 强确认：必须等待用户明确确认平台变更
        user_platform_response = WAIT_FOR_EXPLICIT_CONFIRMATION()
        IF user_platform_response == "confirmed":
            confirmed = true
            transition_allowed = true
            // 触发级联更新
            CALL CASCADE_UPDATE_ALL_STAGES(input.content.new_platform)
        ELSE:
            confirmed = false
            transition_allowed = false
            // 保持原平台
            OUTPUT "已保持原平台选择，不进行变更。"

    // === 第四步：快速通道简化确认 ===
    IF input.content.channel == "fast":
        IF input.node_id IN SOFT_CONFIRM_NODES:
            // 快速通道软确认：自动通过
            confirmed = true
            transition_allowed = true
            OUTPUT "快速通道：已自动确认。如有异议回复'等等'停止。"

    // === 第五步：最终断言与输出 ===
    ASSERT confirmed == true OR confirmed == false
    ASSERT correction_required == true OR correction_required == false
    ASSERT transition_allowed == true OR transition_allowed == false

    // 质量门控由编排器在阶段结束后统一调用，skill内部不再自调用quality-gate（避免递归）
    RETURN {confirmed, correction_required, transition_allowed}
```

## Few-shot 示例

### 示例 1：正常流程 — 阶段结束强确认通过

**输入**:
```json
{
  "node_id": "stage_5_end",
  "content": {
    "stage": "S5_角色架构设计",
    "output_summary": "已设计3个角色：内容策略师(选题+日历)、文案师(文案+标题)、视觉设计师(配图+封面)。MECE三问全部通过。",
    "deliverables": ["角色定义文档", "MECE校验报告", "交付物-角色映射表"]
  },
  "current_stage": "5"
}
```

**输出**:
```json
{
  "confirmed": true,
  "correction_required": false,
  "transition_allowed": true,
  "message": "S5阶段架构设计已确认。3个角色定义+MECE校验通过。回复'确认'进入S6工具配置阶段，或回复'修改'调整角色方案。"
}
```

### 示例 2：异常流程 — 用户要求修改触发修正流程

**输入**:
```json
{
  "node_id": "stage_5_end",
  "content": {
    "stage": "S5_角色架构设计",
    "user_feedback": "我觉得文案师和视觉设计师可以合并成一个人",
    "correction_requested": true,
    "original_output": "3角色方案：内容策略师+文案师+视觉设计师"
  },
  "current_stage": "5"
}
```

**输出**:
```json
{
  "confirmed": false,
  "correction_required": true,
  "transition_allowed": false,
  "correction_detail": {
    "trigger": "用户要求合并角色",
    "action": "回退到S5开始，重新评估角色拆分方案",
    "impact": "合并文案师和视觉设计师→需重新检查MECE独立性(合并后职责范围扩大，独立性可能受影响)",
    "rollback_target": "S5_角色架构设计(保留S2-S4产出)",
    "re_execute": ["角色职责定义", "MECE三问(需重新走覆盖性/独立性/唯一性)"]
  }
}
```

### 示例 3：快速通道 — 软确认节点默认继续

**输入**:
```json
{
  "node_id": "stage_3_workflow",
  "content": {
    "stage": "S3_复杂度判定",
    "result": "低复杂度(单人+2个交付物)",
    "next_stage": "S4_快速通道",
    "channel": "fast"
  },
  "current_stage": "3"
}
```

**输出**:
```json
{
  "confirmed": true,
  "correction_required": false,
  "transition_allowed": true,
  "message": "S3软确认：已自动判定为低复杂度快速通道。将直接跳至S7三步门。如有异议回复'等等'停止。"
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://doc1/protocol-confirmation-node/rules` — Doc1对应SK原始规则
- **[dynamic]** `file://runtime/protocol-confirmation-node/state` — 运行时状态
- **[rag]** `file://rag/protocol-confirmation-node/references` — 向量检索参考资料

## 依赖关系

- `core-state-management-engine`

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系修复生成，版本1.0.0，日期2026-06-15*
