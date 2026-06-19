---
name: protocol-human-approval
description: 定义审批链模板(请求→审核→批准/驳回)，超时升级机制，条件审批处理，纯提示词降级，数据契约。 Use when: 用户说"protocol-human-approval、人工审批协议、L2审批"等触发词。
---

# 人机协作审批协议

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-human-approval` | **中文名**: 人机协作审批协议 | **英文名**: Human Approval Protocol
# 人机协作审批协议 (Human Approval Protocol)

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-human-approval`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

定义审批链模板(请求→审核→批准/驳回)，超时升级机制，条件审批处理，纯提示词降级，数据契约。

## 触发条件

当检测到以下关键词或场景时自动激活：审批, 人工确认, 批准, 驳回, 确认

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "approval_type": {
      "type": "string",
      "enum": [
        "must_approve",
        "conditional",
        "auto"
      ]
    },
    "content": {
      "type": "string"
    },
    "timeout_hours": {
      "type": "number"
    },
    "escalation_chain": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "approval_type",
    "content"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "approval_result": {
      "type": "string",
      "enum": [
        "approved",
        "rejected",
        "timeout_escalated",
        "conditional"
      ]
    },
    "conditions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "data_contract": {
      "type": "object"
    }
  },
  "required": [
    "approval_result"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

(1)定义审批链模板(请求→审核→批准/驳回)→(2)超时升级机制(默认24h→48h→人工接管)→(3)条件审批处理(条件满足时自动通过)→(4)纯提示词降级(无审批工具时SOP中嵌入确认步骤:'以下操作需要你的确认：{操作描述}。回复确认继续，修改调整，取消中止。')→(5)数据契约(审批通过后不可单方面修改)。超时升级：T+0:提交审批;T+24h:首次提醒;T+48h:升级至上级;T+72h:人工接管。

## Few-shot 示例

### 示例 1：正常流程 — 标准审批通过

**输入**:
```json
{
  "approval_type": "must_approve",
  "content": "最终专家包配置(含7个Agent角色定义+12条SOP流程+完整Schema)已生成，请确认后进入部署阶段",
  "timeout_hours": 24
}
```

**输出**:
```json
{
  "approval_result": "approved",
  "conditions": [],
  "data_contract": {
    "hash": "sha256:7a3f8c...",
    "timestamp": "2026-06-15T10:00:00Z",
    "content_snapshot": "最终专家包配置V1.0.0，7角色12流程",
    "immutable_fields": ["角色定义", "SOP流程", "Schema"],
    "modifiable_fields": ["提示词措辞", "工具配置参数"]
  }
}
```

### 示例 2：异常流程 — 超时升级

**输入**:
```json
{
  "approval_type": "must_approve",
  "content": "涉及金融合规的最终方案，需要法务审批",
  "timeout_hours": 48,
  "escalation_chain": ["主理人", "法务负责人", "合规总监"]
}
```

**输出**:
```json
{
  "approval_result": "timeout_escalated",
  "conditions": [
    "T+0: 提交审批至主理人",
    "T+24h: 主理人未响应，首次提醒",
    "T+48h: 升级至法务负责人",
    "当前状态：等待法务负责人批复"
  ],
  "data_contract": {
    "hash": "sha256:b9e2d1...",
    "timestamp": "2026-06-15T10:00:00Z",
    "escalation_level": 2,
    "next_escalation": "合规总监(T+72h)"
  }
}
```

### 示例 3：快速通道 — 纯提示词降级审批

**输入**:
```json
{
  "approval_type": "auto",
  "content": "单人快速通道的简化方案，无需多角色审批",
  "channel": "fast"
}
```

**输出**:
```json
{
  "approval_result": "conditional",
  "conditions": [
    "自动通过条件：单人项目+非监管行业+方案复杂度为低",
    "以下操作需要你的确认：最终方案将直接部署到WorkBuddy单Agent模式。回复'确认继续'，'修改调整'，或'取消中止'。"
  ],
  "data_contract": {
    "hash": "sha256:c3f7a2...",
    "timestamp": "2026-06-15T10:00:00Z",
    "note": "纯提示词降级审批：无审批工具时使用SOP嵌入确认步骤"
  }
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://approval/escalation-rules` — 超时升级规则

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_protocol_human_approval(input):
    ASSERT input.approval_type IN ["must_approve","conditional","auto"]
    ASSERT input.content IS NOT EMPTY

    // === 第一步：识别强制审批场景 ===
    MANDATORY_APPROVAL_SCENARIOS = [
        "强监管行业最终方案发布",
        "高敏感度数据第三方使用",
        "合规审查红灯修复后重审",
        "平台变更(Q9平台确认)",
        "S7四步确认门关键节点",
        "涉及金融/医疗/法律合规决策",
        // A型内容创作运行时审批节点
        "A型内容创作的选题审批（选题确定后、内容创作前）",
        "A型内容创作的终稿审核（内容创作完成、平台发布前）",
        // 其他业务类型关键审批节点
        "B型服务交付的里程碑验收（每个交付物里程碑完成时）",
        "F型客服的SLA异常升级（连续3次未达标或客户投诉升级时）",
        "C型知识管理的专家审校（知识入库前需领域专家审校）",
        "D型流程自动化的异常暂停恢复（自动化流程暂停后恢复执行前）"
    ]

    IF MATCHES_ANY(input.content, MANDATORY_APPROVAL_SCENARIOS):
        input.approval_type = "must_approve"  // 强制升级为必须审批

    // === 第二步：审批流程(请求→审核→批准/驳回) ===
    approval_chain = []
    IF input.approval_type == "must_approve":
        // 必须审批：严格审批链
        approval_request = FORMAT_APPROVAL_REQUEST(input.content)
        OUTPUT "以下操作需要你的确认：{操作描述}"
        OUTPUT "回复'确认继续'，'修改调整'，或'取消中止'。"

        // 等待用户明确确认
        user_response = WAIT_FOR_EXPLICIT_RESPONSE()

        IF user_response == "confirmed":
            approval_result = "approved"
        ELIF user_response == "rejected":
            approval_result = "rejected"
        ELIF user_response == "modified":
            approval_result = "conditional"
            conditions = PARSE_MODIFICATION_REQUEST(user_response)

    ELIF input.approval_type == "conditional":
        // 条件审批：条件满足时自动通过
        conditions_met = EVALUATE_CONDITIONS(input.content)
        IF conditions_met.all_passed:
            approval_result = "conditional"
            conditions = conditions_met.conditions
        ELSE:
            // 条件不满足，升级为必须审批
            approval_result = WAIT_FOR_EXPLICIT_RESPONSE()

    ELIF input.approval_type == "auto":
        // 自动审批：低风险场景自动通过
        approval_result = "approved"
        conditions = []

    // === 第三步：超时处理机制 ===
    // T+0: 提交审批; T+24h: 首次提醒; T+48h: 升级至上级; T+72h: 人工接管
    timeout_hours = input.timeout_hours OR 24
    escalation_chain = input.escalation_chain OR ["主理人"]

    IF approval_result IS PENDING:
        elapsed = TIME_SINCE_SUBMITTED()
        IF elapsed > timeout_hours * 3:  // T+72h
            approval_result = "timeout_escalated"
            escalation_level = 3
            APPEND conditions WITH "T+72h: 人工接管"
            NOTIFY escalation_chain[LAST] WITH "审批超时72h，需人工接管"
        ELIF elapsed > timeout_hours * 2:  // T+48h
            approval_result = "timeout_escalated"
            escalation_level = 2
            APPEND conditions WITH "T+48h: 升级至" + escalation_chain[1]
            NOTIFY escalation_chain[1] WITH "审批超时48h，升级处理"
        ELIF elapsed > timeout_hours:  // T+24h
            NOTIFY escalation_chain[0] WITH "审批超时24h，首次提醒"

    // === 第四步：审批日志与数据契约 ===
    data_contract = {}
    data_contract.hash = COMPUTE_HASH(input.content)
    data_contract.timestamp = CURRENT_TIMESTAMP()
    data_contract.content_snapshot = SUMMARIZE(input.content)

    IF approval_result == "approved":
        // 审批通过后不可单方面修改(数据契约)
        data_contract.immutable_fields = EXTRACT_IMMUTABLE_FIELDS(input.content)
        data_contract.modifiable_fields = EXTRACT_MODIFIABLE_FIELDS(input.content)
        LOG "审批通过: " + data_contract.hash + " @ " + data_contract.timestamp
    ELIF approval_result == "rejected":
        LOG "审批驳回: " + data_contract.hash + " 原因: " + user_response.reason
    ELIF approval_result == "timeout_escalated":
        data_contract.escalation_level = escalation_level
        data_contract.next_escalation = escalation_chain[escalation_level]
        LOG "审批超时升级: level=" + escalation_level

    // === 第五步：纯提示词降级(无审批工具时) ===
    IF NOT HAS_APPROVAL_TOOL():
        // SOP中嵌入确认步骤
        OUTPUT "以下操作需要你的确认：{操作描述}。回复确认继续，修改调整，取消中止。"
        approval_result = "conditional"
        APPEND conditions WITH "纯提示词降级审批：无审批工具时使用SOP嵌入确认步骤"
        data_contract.note = "纯提示词降级审批"

    // === 第六步：最终断言与输出 ===
    ASSERT approval_result IN ["approved","rejected","timeout_escalated","conditional"]
    ASSERT data_contract.hash IS NOT EMPTY

    // 质量门控由编排器在阶段结束后统一调用，skill内部不再自调用quality-gate（避免递归）
    RETURN {approval_result, conditions, data_contract}
```

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系自动生成，版本1.0.0，日期2026-06-15*
