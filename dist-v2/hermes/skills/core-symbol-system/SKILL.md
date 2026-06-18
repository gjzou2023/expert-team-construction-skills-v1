---
name: core-symbol-system
description: 统一信息准确性、合规风险、质量等级和平台执行状态的符号，禁止跨层级混用。 Use when: 用户说"core-symbol-system、符号系统、L0符号"等触发词。
version: 1.1.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [l0]
    related_skills: []
    requires_toolsets: []
---

> **注意**：本 skill 的核心规则已内联至 `team-orchestrator/SKILL.md` 的 `L0` 章节。
> 执行时优先读取 team-orchestrator 的内联指引，仅在需要完整逻辑时再读取本文件。
>
# 符号系统

> **层级**: L0 | **版本**: 1.1.0 | **ID**: `core-symbol-system` | **中文名**: 符号系统 | **英文名**: Symbol System
# 符号系统 (Symbol System)

> **层级**: L0 | **版本**: 1.0.0 | **ID**: `core-symbol-system`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

统一信息准确性、合规风险、质量等级和平台执行状态的符号，禁止跨层级混用。

## 触发条件

当检测到以下关键词或场景时自动激活：符号, 状态标记, 绿灯, 黄灯, 红灯, 格式

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "semantic_layer": {
      "type": "string"
    },
    "status": {
      "type": "string"
    }
  },
  "required": [
    "semantic_layer",
    "status"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "symbol": {
      "type": "string"
    },
    "meaning": {
      "type": "string"
    },
    "usage_rule": {
      "type": "string"
    }
  },
  "required": [
    "symbol",
    "meaning"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

按语义层选择符号：准确性✅/⚡/❓，合规🟢/🟡/🔴，质量⭐⭐⭐/⭐⭐/⭐，平台🟦/🟧/⬛；不同层级不得混用。

## 详细执行逻辑

```text
FUNCTION execute_core_symbol_system(input):
    // ========== 输入校验与初始化 ==========
    ASSERT input.semantic_layer IN ["accuracy","compliance","quality","platform"], "语义层级必须为四层之一"
    ASSERT input.status IS NOT EMPTY, "状态标识不可为空"
    LOAD context_inheritance

    // ========== 符号系统定义：4层 ==========
    SYMBOL_SYSTEM = {
        // 第1层：信息准确性
        "accuracy": {
            "verified": "✅",         // 已验证，信息准确
            "likely_correct": "⚡",   // 大概率正确，尚未完全验证
            "needs_verify": "❓"      // 需要验证，信息存疑
        },
        // 第2层：合规风险
        "compliance": {
            "compliant": "🟢",        // 合规，无风险
            "grey_area": "🟡",        // 灰色地带，需关注
            "violation": "🔴"        // 违规，禁止
        },
        // 第3层：质量等级
        "quality": {
            "excellent": "⭐⭐⭐",     // 优秀，可直接使用
            "adequate": "⭐⭐",       // 合格，可用但可优化
            "needs_improvement": "⭐"  // 需改进，不可直接使用
        },
        // 第4层：平台执行状态
        "platform": {
            "created_callable": "🟦",       // 已创建可调用
            "created_needs_config": "🟧",   // 已创建需配置
            "creation_failed": "⬛"          // 创建失败
        }
    }

    // ========== 使用规则：禁止混用不同层级符号 ==========
    // 检查输入状态是否属于指定语义层
    IF input.status NOT IN KEYS(SYMBOL_SYSTEM[input.semantic_layer]):
        // 状态不属于该层，可能是跨层混用
        // 尝试在其他层查找
        FOR other_layer IN KEYS(SYMBOL_SYSTEM):
            IF other_layer != input.semantic_layer:
                IF input.status IN KEYS(SYMBOL_SYSTEM[other_layer]):
                    RAISE "🚫 符号混用违规：'{input.status}'属于'{other_layer}'层，不可在'{input.semantic_layer}'层使用"
        RAISE "🚫 未知状态：'{input.status}'不属于任何符号层级"

    // 获取符号
    symbol = SYMBOL_SYSTEM[input.semantic_layer][input.status]
    meaning = EXPLAIN_MEANING(input.semantic_layer, input.status)

    // ========== 状态转换规则 ==========
    transition_rules = LOAD_TRANSITION_RULES(input.semantic_layer)
    // 检查是否存在合法转换路径
    IF input.previous_status IS NOT EMPTY:
        // 验证转换合法性
        allowed_transitions = transition_rules[input.previous_status]
        IF input.status NOT IN allowed_transitions:
            RAISE "🚫 非法状态转换：{input.previous_status}→{input.status}，允许的转换为{allowed_transitions}"

    // ========== 各层状态转换规则定义 ==========
    TRANSITION_RULES = {
        // 第1层：信息准确性转换
        "accuracy": {
            "verified": ["needs_verify"],      // ✅→❓ 当新信息推翻已验证结论时
            "likely_correct": ["verified", "needs_verify"],  // ⚡→✅ 验证通过 / ⚡→❓ 验证发现错误
            "needs_verify": ["verified", "likely_correct"]   // ❓→✅ 验证通过 / ❓→⚡ 大概率正确
        },
        // 第2层：合规风险转换
        "compliance": {
            "compliant": ["grey_area"],         // 🟢→🟡 当搜索工具不可用或法规边界模糊时
            "grey_area": ["compliant", "violation"],  // 🟡→🟢 确认合规 / 🟡→🔴 确认违规
            "violation": ["grey_area"]          // 🔴→🟡 仅当修正违规项后可降级
        },
        // 第3层：质量等级转换
        "quality": {
            "excellent": ["adequate"],          // ⭐⭐⭐→⭐⭐ 当需求变更导致不再优秀时
            "adequate": ["excellent", "needs_improvement"],  // ⭐⭐→⭐⭐⭐ 优化 / ⭐⭐→⭐ 退化
            "needs_improvement": ["adequate"]   // ⭐→⭐⭐ 改进后至少为合格，不可直接跳至优秀
        },
        // 第4层：平台执行状态转换
        "platform": {
            "created_callable": ["created_needs_config"],  // 🟦→🟧 当环境变更需重新配置时
            "created_needs_config": ["created_callable", "creation_failed"],  // 🟧→🟦 配置完成 / 🟧→⬛ 配置失败
            "creation_failed": ["created_needs_config"]  // ⬛→🟧 修复后可重新进入配置
        }
    }

    // ========== 特殊场景处理：符号转换触发条件 ==========
    IF input.semantic_layer == "accuracy" AND input.status == "needs_verify":
        // ✅→❓ 当新信息推翻已验证结论时
        IF input.previous_status == "verified":
            OUTPUT "⚠️ 信息准确性降级：已验证结论被新信息推翻，标记为❓需重新验证"
            // 记录推翻原因
            LOG_TRANSITION("accuracy", "verified", "needs_verify", input.overturn_reason)

    IF input.semantic_layer == "compliance" AND input.status == "grey_area":
        // 🟢→🟡 当搜索工具不可用时
        IF input.previous_status == "compliant" AND input.search_tool_unavailable:
            OUTPUT "⚠️ 合规状态变更：搜索工具不可用，无法确认合规，标记为🟡灰色地带"
            LOG_TRANSITION("compliance", "compliant", "grey_area", "搜索工具不可用")

    IF input.semantic_layer == "compliance" AND input.status == "violation":
        OUTPUT "🔴 合规违规警告：检测到违规内容，必须立即修正"
        // 违规不可自行降级，必须修正后经人工确认
        ASSERT input.human_override == TRUE, "违规标记必须经人工确认"

    // ========== 跨层使用规则验证 ==========
    // 每层符号只在其对应语义场景使用
    usage_context_map = {
        "accuracy": ["信息引用", "数据验证", "事实核查"],
        "compliance": ["合规审查", "风险标注", "协议激活"],
        "quality": ["交付物评审", "阶段验收", "质量门控"],
        "platform": ["工具创建", "技能部署", "平台适配"]
    }
    IF input.usage_context IS NOT EMPTY:
        IF input.usage_context NOT IN usage_context_map[input.semantic_layer]:
            OUTPUT "⚠️ 符号使用场景不匹配：'{symbol}'建议在{usage_context_map[input.semantic_layer]}场景使用，当前场景为'{input.usage_context}'"

    // ========== 禁止混用核心规则 ==========
    // 合规红灯🔴不可用于平台创建失败
    // 平台失败必须用⬛
    IF input.semantic_layer == "platform" AND input.status == "creation_failed":
        ASSERT output.symbol == "⬛", "平台创建失败必须使用⬛，禁止使用🔴"
    IF input.semantic_layer == "compliance" AND input.status == "violation":
        ASSERT output.symbol == "🔴", "合规违规必须使用🔴，禁止使用⬛"

    // ========== 组装输出 ==========
    output = {
        symbol: symbol,
        meaning: meaning,
        usage_rule: "仅限{input.semantic_layer}层使用，禁止跨层级混用"
    }
    CALL protocol-quality-gate("symbol_check", output)
    RETURN output

FUNCTION LOAD_TRANSITION_RULES(semantic_layer):
    // 加载指定层级的状态转换规则
    TRANSITION_RULES = {
        "accuracy": {
            "verified": ["needs_verify"],
            "likely_correct": ["verified", "needs_verify"],
            "needs_verify": ["verified", "likely_correct"]
        },
        "compliance": {
            "compliant": ["grey_area"],
            "grey_area": ["compliant", "violation"],
            "violation": ["grey_area"]
        },
        "quality": {
            "excellent": ["adequate"],
            "adequate": ["excellent", "needs_improvement"],
            "needs_improvement": ["adequate"]
        },
        "platform": {
            "created_callable": ["created_needs_config"],
            "created_needs_config": ["created_callable", "creation_failed"],
            "creation_failed": ["created_needs_config"]
        }
    }
    RETURN TRANSITION_RULES[semantic_layer]
```

## Few-shot 示例

### 示例 1：正常流程

**输入**:
```json
{
  "user_input": "小红书内容团队要从选题到发布形成稳定流程",
  "context": {
    "domain_type": "A",
    "platform": "workbuddy"
  }
}
```

**输出**:
```json
{
  "status": "completed",
  "decision": "符号系统已按A型内容传播场景执行",
  "next_action": "进入下一阶段或触发质量门控"
}
```

### 示例 2：边界/异常

**输入**:
```json
{
  "user_input": "我们做医疗科普，但想尽量直接承诺效果",
  "context": {
    "domain_type": "A",
    "regulated": true
  }
}
```

**输出**:
```json
{
  "status": "blocked_or_review",
  "risk": "强监管合规风险",
  "required_call": "protocol-compliance-engine"
}
```

### 示例 3：快速通道变体

**输入**:
```json
{
  "user_input": "只有我一个人，先要一个能用的提示词版客服助手",
  "context": {
    "role_count": 1,
    "deliverable_count": 2,
    "channel": "fast"
  }
}
```

**输出**:
```json
{
  "status": "simplified",
  "strategy": "保留核心交付物与兜底方案，跳过或内联低风险阶段"
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://doc1/core-symbol-system/rules` — Doc1对应SK原始规则
- **[dynamic]** `file://runtime/core-symbol-system/state` — 运行时状态
- **[rag]** `file://rag/core-symbol-system/references` — 向量检索参考资料

## 依赖关系

无前置依赖。

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系修复生成，版本1.0.0，日期2026-06-15*
