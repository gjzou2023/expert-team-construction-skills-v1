---
name: core-complexity-channel-selector
description: 基于7维度统一评估确定执行通道(快速/标准/严格)和响应模式(标准/增强/深度)，输出通道确认卡。v1.4.0将两套独立评估体系整合为统一框架。用户可升级通道但不可降级（除非明确声明理解风险） Use when: 用户说"core-complexity-channel-selector、复杂度通道选择器、L0通道"等触发词。
---

# 复杂度通道选择器

> **层级**: L0 | **版本**: 1.4.0 | **ID**: `core-complexity-channel-selector` | **中文名**: 复杂度通道选择器 | **英文名**: Complexity Channel Selector
# 复杂度通道选择器 (Complexity Channel Selector)

> **层级**: L0 | **版本**: 1.4.0 | **ID**: `core-complexity-channel-selector`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

基于5维度评估确定执行通道(快速/标准/严格)，输出通道确认卡。用户可升级通道但不可降级（除非明确声明理解风险）。

## 触发条件

当检测到以下关键词或场景时自动激活：通道选择, 快速通道, 严格通道, 复杂度评估, 跳过阶段, 精简流程

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "s1_outputs": {
      "type": "object",
      "properties": {
        "domain_type": {
          "type": "string"
        },
        "deliverable_count": {
          "type": "integer"
        },
        "role_count": {
          "type": "integer"
        },
        "compliance_level": {
          "type": "string",
          "enum": [
            "none",
            "light",
            "heavy"
          ]
        },
        "automation_complexity": {
          "type": "string",
          "enum": [
            "none",
            "simple",
            "complex"
          ]
        }
      }
    }
  },
  "required": [
    "s1_outputs"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "channel": {
      "type": "string",
      "enum": [
        "fast",
        "standard",
        "strict"
      ]
    },
    "skipped_stages": {
      "type": "array",
      "items": {
        "type": "integer"
      }
    },
    "stage_simplification": {
      "type": "object",
      "additionalProperties": {
        "type": "string"
      }
    },
    "confirmation_card": {
      "type": "string"
    }
  },
  "required": [
    "channel",
    "skipped_stages",
    "stage_simplification",
    "confirmation_card"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

5维度评估：知识深度(低/中/高)、监管强度(低/中/高)、错误代价(低/中/高)、更新频率(低/中/高)、数据敏感度(低/中/高)。
通道规则：
- 快速通道：角色数≤2,交付物≤3,无强监管,无D/F型自动化→跳过S3/S5,简化S2/S4,S7内联输出
- 标准通道：默认,完整8阶段
- 严格通道：强监管行业/角色≥4/涉及医疗金融法律→增加合规审查节点+人工审批+双重确认
约束：用户可升级通道但不可降级(除非明确声明理解风险)；快速通道跳过5.9自动化触发设计，使用纯提示词降级。

## 统一复杂度评估框架（v1.4.0升级）

收到用户需求后，执行7维度统一评估，同时输出通道选择和响应模式：

| # | 维度 | 1分（低） | 3分（中） | 5分（高） | 关联通道维度 |
|---|------|---------|----------|----------|------------|
| 1 | 知识深度/学科数量 | 单一领域 | 2-3个领域 | 4+跨学科 | 对应原"知识深度" |
| 2 | 监管/合规密度 | 无监管要求 | 弱监管（内容合规） | 强监管（金融/医疗/法律） | 对应原"监管强度" |
| 3 | 错误代价/利益相关者 | 1-2人 | 3-5人 | 6+人或跨部门 | 对应原"错误代价" |
| 4 | 更新频率/时间跨度 | 短期（<1月） | 中期（1-6月） | 长期（>6月） | 对应原"更新频率" |
| 5 | 数据敏感度 | 公开数据 | 内部数据 | 敏感/出境数据 | 对应原"数据敏感度" |
| 6 | 技术成熟度 | 成熟技术 | 有一定创新性 | 前沿探索 | 新增维度 |
| 7 | 交付物复杂度 | ≤3个交付物 | 4-6个交付物 | 7+个交付物 | 新增维度 |

### 统一评估流程

1. 7维度各1-5分，总分7-35
2. 通道选择：7-14→fast, 15-24→standard, 25-35→strict
3. 响应模式：7-14→标准模式(3-4位专家), 15-24→增强模式(5-6位专家), 25-35→深度模式(6-8位专家)
4. 通道与模式独立输出，允许组合（如strict通道+增强模式）

### ASSESS_UNIFIED函数（替代原5个ASSESS函数）

FUNCTION ASSESS_UNIFIED(s1_outputs):
    dimensions = {}
    FOR i IN 1..7:
        dimensions[dimension_name[i]] = SCORE_1_TO_5(s1_outputs, dimension_rules[i])
    total = SUM(dimensions.values())
    channel = DETERMINE_CHANNEL(total, dimensions)
    mode = DETERMINE_RESPONSE_MODE(total, dimensions)
    RETURN {dimensions, total, channel, mode}

## Few-shot 示例

### 示例 1

**输入**:
```json
{
  "s1_outputs": {
    "domain_type": "A",
    "deliverable_count": 2,
    "role_count": 2,
    "compliance_level": "none",
    "automation_complexity": "none"
  }
}
```

**输出**:
```json
{
  "channel": "fast",
  "skipped_stages": [
    3,
    5
  ],
  "stage_simplification": {
    "s2": "简化消歧，直接确认",
    "s4": "精简交付物规格(5核心字段)",
    "s7": "内联输出，无分步确认"
  },
  "confirmation_card": "📌 通道确认卡\\n通道：快速通道\\n跳过：S3链路拆解、S5架构设计\\n精简：S2消歧简化、S4规格精简、S7内联输出\\n⚠️ 快速通道跳过5.9自动化触发设计，使用纯提示词降级"
}
```

## 知识库挂载点 (knowledge_base_mount_points)


> **⚠️ 挂载点说明**：以下 `file://` 路径为概念性挂载点（conceptual mount points），用于声明本 skill 的知识库依赖结构。它们不是物理文件路径，不需要实际加载文件。执行时请直接依据本 SKILL.md 正文中的规则定义和伪代码逻辑工作。
- **[static]** `file://channel-rules/thresholds` — 三通道判定阈值与跳过规则
- **[static]** `file://channel-rules/fast-track-simplifications` — 快速通道各阶段精简规则

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_core_complexity_channel_selector(input):
    // ========== 输入校验与初始化 ==========
    ASSERT input.s1_outputs IS NOT EMPTY, "S1输出不可为空"
    ASSERT input.s1_outputs.domain_type IN ["A","B","C","D","F"], "领域类型必须合法(E型已改为A-F组合标记)"
    // 混合型场景通过domain_profile.secondary_domains判断，不再使用E型枚举
    LOAD context_inheritance FROM core-mental-model-engine
    // channel_thresholds和fast_simplifications已内联在本SKILL.md正文中

    // ========== 第1步：5维度评估 ==========
    dimensions = {
        "knowledge_depth": ASSESS_KNOWLEDGE_DEPTH(input.s1_outputs),
        "regulatory_intensity": ASSESS_REGULATORY_INTENSITY(input.s1_outputs),
        "error_cost": ASSESS_ERROR_COST(input.s1_outputs),
        "update_frequency": ASSESS_UPDATE_FREQUENCY(input.s1_outputs),
        "data_sensitivity": ASSESS_DATA_SENSITIVITY(input.s1_outputs)
    }
    // 每个维度返回 low / medium / high
    FOR dim_name IN KEYS(dimensions):
        ASSERT dimensions[dim_name] IN ["low","medium","high"], "维度评分必须为低/中/高"

    // 计算高维度数量
    high_count = 0
    medium_count = 0
    FOR dim_name IN KEYS(dimensions):
        IF dimensions[dim_name] == "high":
            high_count += 1
        ELIF dimensions[dim_name] == "medium":
            medium_count += 1

    // ========== 第2步：通道选择规则 ==========
    channel = "standard"  // 默认标准通道
    skipped_stages = []
    stage_simplification = {}

    // 快速通道条件：所有维度均为低 且 无强监管 且 无D/F型自动化
    IF high_count == 0 AND medium_count == 0 AND dimensions.regulatory_intensity == "low":
        IF input.s1_outputs.role_count <= 2 AND input.s1_outputs.deliverable_count <= 3:
            IF input.s1_outputs.domain_type NOT IN ["D","F"]:
                channel = "fast"
                skipped_stages = [3, 5]  // 跳过S3链路拆解、S5架构设计
                stage_simplification = {
                    "s2": "简化消歧，直接确认",
                    "s4": "精简交付物规格(5核心字段)",
                    "s7": "内联输出，无分步确认"
                }
                OUTPUT "✅ 快速通道条件满足：低复杂度、无强监管、角色≤2、交付物≤3"

    // 严格通道条件：任一维度为高 或 强监管行业
    ELIF high_count >= 1 OR dimensions.regulatory_intensity == "high":
        IF input.s1_outputs.domain_type IN ["A"] AND HAS_REGULATED_KEYWORDS(input.s1_outputs):
            // A型但涉及医疗金融法律等强监管
            channel = "strict"
        ELIF input.s1_outputs.role_count >= 4:
            channel = "strict"
        ELIF dimensions.error_cost == "high" AND dimensions.data_sensitivity == "high":
            channel = "strict"
        IF channel == "strict":
            skipped_stages = []
            stage_simplification = {
                "additional_review": "增加合规审查节点",
                "human_approval": "人工审批环节",
                "dual_confirmation": "双重确认机制"
            }
            OUTPUT "🔴 严格通道条件满足：高复杂度或强监管领域"

    // 标准通道（默认）
    ELSE:
        channel = "standard"
        skipped_stages = []
        stage_simplification = {}
        OUTPUT "🟡 标准通道：中等复杂度，完整8阶段"

    // ========== 第3步：通道确认三步流程 ==========
    // 步骤3.1：领域解读卡确认
    domain_card = GENERATE_DOMAIN_CARD(input.s1_outputs, channel)
    OUTPUT "📋 领域解读卡：{domain_card}"
    WAIT_FOR_USER_ACKNOWLEDGE("请确认领域解读卡内容")

    // 步骤3.2：通道推荐 + 理由
    recommendation = {
        channel: channel,
        reason: EXPLAIN_CHANNEL_REASON(channel, dimensions, input.s1_outputs),
        dimensions_summary: dimensions,
        skipped_stages: skipped_stages,
        simplification: stage_simplification
    }
    IF channel == "fast":
        APPEND(recommendation.reason, "⚠️ 快速通道跳过5.9自动化触发设计，使用纯提示词降级")
    OUTPUT "📋 通道推荐：{recommendation}"

    // 步骤3.3：强制确认
    OUTPUT "⚠️ 通道确认卡（必须确认）"
    confirmation_card = BUILD_CONFIRMATION_CARD(channel, skipped_stages, stage_simplification)
    user_confirmed = WAIT_FOR_EXPLICIT_CONFIRMATION()
    ASSERT user_confirmed == TRUE, "通道选择必须经用户确认"

    // ========== 第4步：升级/降级规则 ==========
    // 用户可自由升级通道
    IF user_requests_upgrade(channel):
        new_channel = UPGRADE_CHANNEL(channel)
        ASSERT COMPARE_LEVEL(new_channel) > COMPARE_LEVEL(channel), "必须是升级"
        channel = new_channel
        OUTPUT "✅ 通道已升级至{channel}"

    // 用户降级需声明风险
    IF user_requests_downgrade(channel):
        IF channel == "strict" AND new_channel == "standard":
            OUTPUT "⚠️ 降级警告：从严格通道降级至标准通道可能遗漏合规审查，请明确声明理解风险"
            risk_declaration = WAIT_FOR_RISK_ACKNOWLEDGEMENT()
            IF risk_declaration.acknowledged:
                channel = new_channel
                OUTPUT "⚠️ 通道已降级，风险已声明"
            ELSE:
                OUTPUT "❌ 降级取消，维持原通道"
        ELIF channel == "standard" AND new_channel == "fast":
            OUTPUT "⚠️ 降级警告：从标准通道降级至快速通道将跳过关键阶段，请明确声明理解风险"
            risk_declaration = WAIT_FOR_RISK_ACKNOWLEDGEMENT()
            IF risk_declaration.acknowledged:
                channel = new_channel
                skipped_stages = [3, 5]
            ELSE:
                OUTPUT "❌ 降级取消，维持原通道"

    // ========== 组装输出 ==========
    output = {
        channel: channel,
        skipped_stages: skipped_stages,
        stage_simplification: stage_simplification,
        confirmation_card: confirmation_card
    }
    // 质量门控由编排器在阶段结束后统一调用（避免递归）
    RETURN output

FUNCTION ASSESS_KNOWLEDGE_DEPTH(s1_outputs):
    // 评估知识深度维度
    IF s1_outputs.domain_type IN ["C","D"]:
        RETURN "high"  // 知识管理/流程自动化通常知识深度高
    ELIF s1_outputs.domain_type IN ["A"]:
        RETURN "low"   // 内容传播型知识深度相对低
    ELSE:
        RETURN "medium"

FUNCTION ASSESS_REGULATORY_INTENSITY(s1_outputs):
    // 评估监管强度维度
    IF s1_outputs.compliance_level == "heavy":
        RETURN "high"
    ELIF s1_outputs.compliance_level == "light":
        RETURN "medium"
    ELSE:
        RETURN "low"

FUNCTION ASSESS_ERROR_COST(s1_outputs):
    // 评估错误代价维度
    // 混合型场景（原E型）通过secondary_domains判断：含B型+强监管=错误代价高
    is_mixed_with_b = s1_outputs.domain_profile EXISTS AND "B" IN s1_outputs.domain_profile.secondary_domains
    IF (s1_outputs.domain_type == "B" OR is_mixed_with_b) AND s1_outputs.compliance_level == "heavy":
        RETURN "high"  // 服务交付+强监管=错误代价高
    ELIF s1_outputs.domain_type IN ["A","C"]:
        RETURN "low"
    ELSE:
        RETURN "medium"

FUNCTION ASSESS_UPDATE_FREQUENCY(s1_outputs):
    // 评估更新频率维度
    IF s1_outputs.automation_complexity == "complex":
        RETURN "high"
    ELIF s1_outputs.automation_complexity == "simple":
        RETURN "medium"
    ELSE:
        RETURN "low"

FUNCTION ASSESS_DATA_SENSITIVITY(s1_outputs):
    // 评估数据敏感度维度
    IF s1_outputs.compliance_level == "heavy":
        RETURN "high"
    ELIF s1_outputs.compliance_level == "light":
        RETURN "medium"
    ELSE:
        RETURN "low"

FUNCTION COMPARE_LEVEL(channel):
    // 通道等级比较
    IF channel == "fast": RETURN 1
    ELIF channel == "standard": RETURN 2
    ELIF channel == "strict": RETURN 3
```

## 版本

1.4.0

---
*本Skill由全域专家团构建skills体系生成，版本1.4.0，日期2026-06-17*
