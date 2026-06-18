---
name: protocol-early-termination
id: "protocol-early-termination"
layer: "L2"
name_zh: "紧急终止协议"
name_en: "Early Termination Protocol"
version: "1.1.0"
description: 用户可随时要求跳到输出，收集已完成阶段输出+用快速模式最小输出填充未完成阶段，标记紧急终止。
agent_created: true
trigger_keywords: ["够了", "直接给我", "跳过这些", "我只要结果", "不要了"]
dependencies: ["core-mental-model-engine", "core-state-management-engine"]
---

# 紧急终止协议 (Early Termination Protocol)

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-early-termination`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

用户可随时要求跳到输出，收集已完成阶段输出+用快速模式最小输出填充未完成阶段，标记紧急终止。

## 触发条件

当检测到以下关键词或场景时自动激活：够了, 直接给我, 跳过这些, 我只要结果, 不要了

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "current_stage": {"type": "string", "description": "当前所处阶段"},
    "completed_outputs": {"type": "object", "description": "已完成阶段的所有输出"},
    "termination_signal": {"type": "string", "description": "用户的终止信号原文"}
  },
  "required": ["current_stage", "completed_outputs"]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "early_termination_report": {"type": "object"},
    "filled_outputs": {"type": "object"},
    "compliance_holds": {"type": "array", "description": "仍需人工审批的合规项目列表(4.4人工审批不可跳过)"}
  },
  "required": ["early_termination_report", "filled_outputs", "compliance_holds"]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)检测用户终止信号→(2)收集当前已完成阶段的所有输出→(3)对未完成阶段用"快速模式最小输出"填充→(4)检查合规约束(4.4人工审批不可跳过)→(5)在最终输出中标记"【紧急终止模式】以下内容为AI基于有限信息生成，建议后续补充完善"。

## 快速模式最小输出字段填充表

改进#12修复：明确"快速模式最小输出"具体填充哪些字段。

| 未完成阶段 | 最小输出字段 | 填充策略 | 标注 |
|-----------|------------|---------|------|
| S2(领域消歧) | confirmed_domain, compliance_activation_map | 从S1的Q1答案推导默认A型，合规全设为none | [快速通道自动生成] |
| S3(链路拆解) | chain_nodes | 使用领域默认线性链路：交付物→能力→工具→输出 | [快速通道自动生成] |
| S4(交付物锚定) | deliverables | 从S1的Q4期望成果直接映射 | [快速通道自动生成] |
| S5(架构设计) | roles, sop, data_flow, feedback_loops | 使用领域默认角色集+SOP模板+线性数据流 | [快速通道自动生成] |
| S6(工具链匹配) | tool_matrix, degradation_plan | 纯提示词模式，无外部依赖 | [快速通道自动生成] |
| S7(专家包生成) | expert_package, execution_plan | 精简单Agent提示词版专家包 | [快速通道自动生成] |

## 详细执行逻辑

```text
FUNCTION execute_protocol_early_termination(input):
    # ===== 步骤1: 检测用户终止信号 =====
    TERMINATION_SIGNALS = ["够了", "直接给我", "跳过这些", "我只要结果", "不要了"]
    IF NOT CONTAINS_ANY(input.termination_signal, TERMINATION_SIGNALS):
        RETURN  # 非终止信号，不激活

    # ===== 步骤2: 收集已完成阶段输出 =====
    completed_outputs = input.completed_outputs
    completed_stages = EXTRACT_COMPLETED_STAGES(completed_outputs)
    current_stage = input.current_stage

    # ===== 步骤3: 识别未完成阶段 =====
    ALL_STAGES = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
    skipped_stages = [s FOR s IN ALL_STAGES IF s NOT IN completed_stages AND s != current_stage]

    # ===== 步骤4: 用快速模式最小输出填充未完成阶段 =====
    filled_outputs = {}
    FOR stage IN skipped_stages:
        filled_outputs[stage + "_outputs"] = GENERATE_MINIMAL_OUTPUT(stage, completed_outputs)
        # 每个填充字段标注[快速通道自动生成]

    # ===== 步骤5: 检查合规约束(4.4人工审批不可跳过) =====
    compliance_holds = []
    # 检查S2输出的合规激活映射
    s2_output = completed_outputs.s2_outputs IF EXISTS ELSE filled_outputs.s2_outputs
    IF s2_output.compliance_activation_map["4.4"]["level"] == "mandatory":
        compliance_holds.APPEND({
            "rule": "4.4人工审批",
            "reason": "强监管领域mandatory级别，紧急终止不可跳过",
            "action_required": "输出前必须完成人工审批"
        })

    # ===== 步骤6: 标记紧急终止模式 =====
    early_termination_report = {
        "terminated_at": current_stage,
        "completed_stages": completed_stages,
        "skipped_stages": skipped_stages,
        "reason": "用户主动请求紧急终止",
        "warning": "【紧急终止模式】以下内容为AI基于有限信息生成，建议后续补充完善"
    }

    RETURN {
        "early_termination_report": early_termination_report,
        "filled_outputs": filled_outputs,
        "compliance_holds": compliance_holds
    }
```

## Few-shot 示例

### 示例1: 正常触发 - S4阶段紧急终止

**输入**:
```json
{
  "current_stage": "S4",
  "completed_outputs": {
    "s1_outputs": {"core_need": "自动化美食探店内容生产"},
    "s2_outputs": {"confirmed_domain": "A"},
    "s3_outputs": {"chain_nodes": ["选题→创作→审核→发布"]}
  },
  "termination_signal": "够了，直接给我结果"
}
```

**输出**:
```json
{
  "early_termination_report": {
    "terminated_at": "S4",
    "completed_stages": ["S1", "S2", "S3"],
    "skipped_stages": ["S4", "S5", "S6", "S7"],
    "reason": "用户主动请求紧急终止"
  },
  "filled_outputs": {
    "s4_outputs": {"deliverables": "[快速通道自动生成]基于S3链路的默认交付物清单"},
    "s5_outputs": {"roles": "[快速通道自动生成]基于A型默认角色集"},
    "s7_outputs": {"expert_package": "[快速通道自动生成]精简专家包"}
  },
  "compliance_holds": []
}
```

### 示例2: 合规hold - 强监管场景紧急终止

**输入**:
```json
{
  "current_stage": "S6",
  "completed_outputs": {
    "s1_outputs": {"core_need": "医疗科普内容自动化"},
    "s2_outputs": {"confirmed_domain": "A", "compliance_activation_map": {"4.4": {"level": "mandatory"}}}
  },
  "termination_signal": "不要了，直接出结果"
}
```

**输出**:
```json
{
  "early_termination_report": {
    "terminated_at": "S6",
    "completed_stages": ["S1", "S2"],
    "skipped_stages": ["S3", "S4", "S5", "S6", "S7"],
    "reason": "用户主动请求紧急终止",
    "compliance_warning": "强监管领域，4.4人工审批不可跳过"
  },
  "filled_outputs": {
    "s7_outputs": {"expert_package": "[快速通道自动生成]精简专家包"}
  },
  "compliance_holds": [
    {"rule": "4.4人工审批", "reason": "强监管领域mandatory级别，紧急终止不可跳过", "action_required": "输出前必须完成人工审批"}
  ]
}
```

### 示例3: 降级填充 - 快速通道场景紧急终止

**输入**:
```json
{
  "current_stage": "S2",
  "completed_outputs": {
    "s1_outputs": {"core_need": "单人财税科普号", "team_size": 1}
  },
  "termination_signal": "跳过这些，我只要结果"
}
```

**输出**:
```json
{
  "early_termination_report": {
    "terminated_at": "S2",
    "completed_stages": ["S1"],
    "skipped_stages": ["S2", "S3", "S4", "S5", "S6", "S7"],
    "reason": "用户主动请求紧急终止",
    "channel": "fast"
  },
  "filled_outputs": {
    "s2_outputs": {"confirmed_domain": "A"},
    "s7_outputs": {"expert_package": "[快速通道自动生成]单Agent提示词版专家包"}
  },
  "compliance_holds": []
}
```

## 紧急终止合规红线

- 4.4人工审批即使在紧急终止模式下仍不可跳过（合规红线）
- 如涉及4.2敏感词，仍须标记但可暂不阻断
- 4.3/4.5数据安全和隐私标记为"待确认"

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://./knowledge/early-termination-rules.md` — 紧急终止规则

## 依赖关系

- `core-mental-model-engine`
- `core-state-management-engine`

## 版本

1.1.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.1.0，日期2026-06-16*
