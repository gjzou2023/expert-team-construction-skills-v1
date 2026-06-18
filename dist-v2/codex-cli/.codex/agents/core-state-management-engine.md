
# 状态管理引擎 (State Management Engine)

> **层级**: L0 | **版本**: 1.0.0 | **ID**: `core-state-management-engine`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

维护阶段决策快照，处理用户回退、平台更换和长对话上下文压缩。

## 触发条件

当检测到以下关键词或场景时自动激活：快照, 回退, 改一下, 换平台, 上下文压缩, 状态

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "action": {
      "type": "string",
      "enum": [
        "update",
        "rollback",
        "platform_change",
        "compress"
      ]
    },
    "stage": {
      "type": "string"
    },
    "user_input": {
      "type": "string"
    },
    "new_platform": {
      "type": "string"
    }
  },
  "required": [
    "action",
    "stage"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "snapshot": {
      "type": "object"
    },
    "impact_list": {
      "type": "array"
    },
    "recovery_path": {
      "type": "string"
    }
  },
  "required": [
    "snapshot"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

每阶段结束更新快照；检测回退触发词时暂停推进并输出影响清单；平台变更时保留设计并重走平台适配；对话超过40轮时压缩上下文。

## 详细执行逻辑

```text
FUNCTION execute_core_state_management_engine(input):
    // ========== 输入校验与初始化 ==========
    ASSERT input.action IN ["update","rollback","platform_change","compress"], "操作类型必须合法"
    ASSERT input.stage IS NOT EMPTY, "阶段标识不可为空"
    LOAD context_inheritance FROM core-mental-model-engine
    snapshot = LOAD_CURRENT_SNAPSHOT()

    // ========== 决策快照维护：每阶段更新 ==========
    IF input.action == "update":
        // 正常阶段推进，更新快照
        snapshot[input.stage] = {
            key_decisions: EXTRACT_KEY_DECISIONS(input.stage),
            dependencies: EXTRACT_DEPENDENCIES(input.stage),
            platform_compat: EVALUATE_PLATFORM_COMPAT(input.stage),
            timestamp: CURRENT_TIMESTAMP()
        }
        // 验证快照完整性
        ASSERT snapshot[input.stage].key_decisions IS NOT EMPTY, "关键决策不可为空"
        ASSERT snapshot[input.stage].dependencies IS NOT NULL, "依赖关系不可为空"
        OUTPUT "✅ 阶段{input.stage}快照已更新"
        CALL protocol-quality-gate("snapshot_check", snapshot)
        RETURN snapshot

    // ========== 回退处理：6个触发词 + 5步流程 ==========
    ROLLBACK_TRIGGERS = ["等等", "我想改一下", "刚才说的不对", "重新想想", "不对", "改个方向"]

    IF input.action == "rollback" OR CONTAINS_ANY(input.user_input, ROLLBACK_TRIGGERS):
        // ---- 步骤1：暂停推进 ----
        PAUSE_FORWARD()
        OUTPUT "⏸️ 已暂停推进，正在处理回退请求..."

        // ---- 步骤2：识别变更目标 ----
        modified_item = IDENTIFY_MODIFICATION(input.user_input)
        IF modified_item IS EMPTY:
            // 用户表述模糊，主动询问
            OUTPUT "请明确您想修改的具体内容（如：角色、交付物、工具、数据流）"
            modified_item = WAIT_FOR_CLARIFICATION()
        ASSERT modified_item IS NOT EMPTY, "必须明确修改目标"

        // ---- 步骤3：标注变更影响范围 ----
        impact_list = CHECK_DOWNSTREAM_IMPACT(modified_item, snapshot)
        // 按影响程度排序
        impact_list = SORT_BY_SEVERITY(impact_list)
        OUTPUT "📋 变更影响清单："
        FOR item IN impact_list:
            severity_symbol = MAP_SEVERITY_SYMBOL(item.severity)
            OUTPUT "  {severity_symbol} {item.stage} - {item.description}（影响程度：{item.severity}）"

        // ---- 步骤4：影响评估与确认 ----
        IF LENGTH(impact_list) > 0:
            high_impact_count = COUNT(impact_list, item => item.severity == "high")
            IF high_impact_count > 3:
                OUTPUT "⚠️ 高影响变更超过3项，建议考虑回退到更早阶段而非局部修改"
                user_choice = WAIT_FOR_CHOICE(["局部修改","回退到更早阶段"])
                IF user_choice == "回退到更早阶段":
                    # 改进#22修复: 调用IDENTIFY_ROOT_CAUSE_STAGE而非旧函数IDENTIFY_ROLLBACK_STAGE
                    failure_point = {"stage": input.stage, "error_type": "high_impact_rollback"}
                    rollback_stage = IDENTIFY_ROOT_CAUSE_STAGE(failure_point, snapshot)
                    snapshot = ROLLBACK_SNAPSHOT_TO(snapshot, rollback_stage)
                    OUTPUT "✅ 已回退到阶段{rollback_stage}"
                    RETURN snapshot
        // 用户确认变更
        WAIT_FOR_CONFIRMATION("确认执行变更？")

        // ---- 步骤5：同步更新受影响项 ----
        FOR affected IN impact_list:
            update_result = UPDATE_SECTION(affected, modified_item)
            IF update_result.success:
                // 同步更新快照
                snapshot[affected.stage] = REBUILD_SNAPSHOT(affected.stage, modified_item)
                ASSERT snapshot[affected.stage].key_decisions IS NOT EMPTY
            ELSE:
                OUTPUT "⚠️ 更新失败：{affected.stage} - {update_result.error}"
                // 记录失败但不中断，继续处理后续项
        // 重新验证快照一致性
        ASSERT VALIDATE_SNAPSHOT_CONSISTENCY(snapshot), "快照一致性验证失败"
        OUTPUT "✅ 回退处理完成，快照已同步更新"
        RETURN snapshot

    // ========== 平台更换回退 ==========
    IF input.action == "platform_change":
        ASSERT input.new_platform IS NOT EMPTY, "新平台标识不可为空"
        confirm_result = CONFIRM_PLATFORM(input.new_platform)
        IF NOT confirm_result.accepted:
            OUTPUT "❌ 平台更换未确认，维持原平台"
            RETURN snapshot

        current_stage = PARSE_STAGE_NUMBER(input.stage)
        IF current_stage >= 5:
            // S5之后更换平台，协作模式可能已定义，需要特殊处理
            // 检查协作模式是否因平台变更而改变
            IF PLATFORM_CHANGES_COLLABORATION_MODEL(input.new_platform, snapshot):
                OUTPUT "⚠️ 当前阶段≥5且平台变更影响协作模式，需回退到S5角色协作模式"
                ROLLBACK_TO_STAGE = "S5角色协作模式"
                snapshot = ROLLBACK_SNAPSHOT_TO(snapshot, ROLLBACK_TO_STAGE)
                // 保留设计部分，仅重走平台适配
                preserved_design = EXTRACT_PRESERVED_DESIGN(snapshot, "before_S5")
                snapshot["S5"] = REBUILD_WITH_NEW_PLATFORM(snapshot["S5"], input.new_platform, preserved_design)
                OUTPUT "✅ 已回退至S5并使用新平台{input.new_platform}重新生成协作模式"
            ELSE:
                // 协作模式不变，仅需重新生成S7平台适配
                REGENERATE_STAGE_7(input.new_platform, snapshot)
                snapshot["S7"] = REBUILD_WITH_NEW_PLATFORM(snapshot["S7"], input.new_platform)
                OUTPUT "✅ 协作模式不变，已使用新平台{input.new_platform}重新生成S7"
        ELSE:
            // 阶段<5，直接重新生成S7
            REGENERATE_STAGE_7(input.new_platform, snapshot)
            OUTPUT "✅ 已使用新平台{input.new_platform}重新生成S7"
        RETURN snapshot

    // ========== 上下文压缩：对话超过40轮 ==========
    IF input.action == "compress" OR GET_TURN_COUNT() > 40:
        // 生成完整快照摘要
        full_snapshot = GENERATE_FULL_SNAPSHOT(snapshot)
        // I-2.7改进：压缩策略升级为两层
        // 第一层：结构化保留层——所有可量化约束、负面约束保留原始值，不摘要
        structured_constraints = EXTRACT_ALL_CONSTRAINTS(full_snapshot)  // 频率/数量/阈值等原始值
        negative_constraints = EXTRACT_ALL_NEGATIVES(full_snapshot)      // "不要X"列表，防止摘要丢失
        // 第二层：语义摘要层——仅对决策理由和推导过程进行摘要
        compressed_snapshot = {
            structured_constraints: structured_constraints,
            negative_constraints: negative_constraints,
            summary: SUMMARIZE_RATIONALES(full_snapshot),  // 仅摘要理由，不摘要原始约束值
            current_stage: input.stage,
            key_decisions: EXTRACT_ALL_KEY_DECISIONS(full_snapshot),
            dependencies: MERGE_ALL_DEPENDENCIES(full_snapshot),
            platform_compat: LATEST_PLATFORM_COMPAT(full_snapshot),
            timestamp: CURRENT_TIMESTAMP(),
            original_turn_count: GET_TURN_COUNT()
        }
        OUTPUT "📦 上下文已压缩，保留结构化约束" + LENGTH(structured_constraints) + "条、负面约束" + LENGTH(negative_constraints) + "条"
        // 用压缩后的快照替换当前上下文
        REPLACE_CONTEXT_WITH(compressed_snapshot)
        RETURN compressed_snapshot

    // ========== 默认兜底 ==========
    OUTPUT "❌ 未知操作类型：{input.action}"
    RETURN snapshot

FUNCTION MAP_SEVERITY_SYMBOL(severity):
    // 将影响程度映射为符号系统标记
    IF severity == "high": RETURN "🔴"
    ELIF severity == "medium": RETURN "🟡"
    ELSE: RETURN "🟢"

FUNCTION IDENTIFY_ROLLBACK_STAGE(impact_list):
    // 根据影响清单确定回退目标阶段（原逻辑：取最早受影响阶段）
    earliest_affected = MIN(impact_list, item => PARSE_STAGE_NUMBER(item.stage))
    RETURN earliest_affected.stage

// I-2.10改进：跨阶段根因定位——支持"S8发现问题→根因在S5→直接回退到S5"
FUNCTION IDENTIFY_ROOT_CAUSE_STAGE(failure_point, snapshot):
    // 从失败点反向追溯依赖链，找到根因阶段而非最近阶段
    current_stage = failure_point.stage
    MAX_DEPTH = 5  // 最多追溯5层，防止无限循环
    depth = 0
    WHILE current_stage HAS dependencies AND depth < MAX_DEPTH:
        dep_chain = GET_DEPENDENCY_CHAIN(current_stage, snapshot)
        root_stage = FIND_ROOT_IN_CHAIN(dep_chain, failure_point.error_type)
        IF root_stage != current_stage:
            RETURN root_stage  // 找到根因阶段
        current_stage = PREV_STAGE(current_stage)
        depth = depth + 1
    RETURN failure_point.stage  // fallback到失败点本身

FUNCTION VALIDATE_SNAPSHOT_CONSISTENCY(snapshot):
    // 验证快照内部一致性
    FOR stage IN KEYS(snapshot):
        IF snapshot[stage].key_decisions IS EMPTY:
            RETURN FALSE
        IF snapshot[stage].dependencies HAS_CONFLICT:
            RETURN FALSE
    RETURN TRUE
```

## Few-shot 示例

### 示例 1：正常流程 - 阶段快照更新

**输入**:
```json
{
  "action": "update",
  "stage": "S2",
  "user_input": "小红书内容团队要从选题到发布形成稳定流程"
}
```

**输出**:
```json
{
  "snapshot": {
    "S2": {
      "key_decisions": {"confirmed_domain": "A", "channel": "standard"},
      "dependencies": ["core-domain-classifier", "core-complexity-channel-selector"],
      "platform_compat": "workbuddy",
      "timestamp": "2026-06-17T13:00:00Z"
    }
  },
  "impact_list": [],
  "recovery_path": "continue_to_S3"
}
```

### 示例 2：回退处理 - 用户要求修改

**输入**:
```json
{
  "action": "rollback",
  "stage": "S5",
  "user_input": "等等，我想改一下角色分工，刚才说的不对"
}
```

**输出**:
```json
{
  "snapshot": {
    "S5": {
      "key_decisions": {"roles": "[待重新确认]", "status": "rollback_pending"},
      "dependencies": ["core-deliverable-backward-engine", "protocol-quality-gate"]
    }
  },
  "impact_list": [
    {"stage": "S5", "description": "角色定义需重新生成", "severity": "high"},
    {"stage": "S7", "description": "专家包生成依赖S5角色，需重跑", "severity": "high"}
  ],
  "recovery_path": "rollback_to_S5_and_regenerate_roles"
}
```

### 示例 3：上下文压缩 - 长对话触发

**输入**:
```json
{
  "action": "compress",
  "stage": "S7",
  "user_input": "继续生成专家包"
}
```

**输出**:
```json
{
  "snapshot": {
    "structured_constraints": {"team_size": 3, "max_roles": 5},
    "negative_constraints": ["不要超过5个角色", "不要用通用title"],
    "summary": "用户构建小红书内容团队，已确认A型领域，标准通道，S1-S6已完成",
    "current_stage": "S7",
    "original_turn_count": 42
  },
  "impact_list": [],
  "recovery_path": "context_compressed_continue_S7"
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://./knowledge/core-state-management-engine-rules.md` — Doc1对应SK原始规则
- **[dynamic]** `file://./knowledge/core-state-management-engine-state.json` — 运行时状态
- **[rag]** `file://./knowledge/core-state-management-engine-references/` — 向量检索参考资料

## 依赖关系

- `core-mental-model-engine`

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系修复生成，版本1.0.0，日期2026-06-15*
