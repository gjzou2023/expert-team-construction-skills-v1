---
name: protocol-compliance-engine
description: 按领域类型和监管等级激活合规子协议，执行4级合规审查(法规>平台>服务>品牌)，输出合规审查报告。与protocol-quality-gate的5.3合规层联动 Use when: 用户说"protocol-compliance-engine、合规引擎、L2合规"等触发词。
tools: Read
---

# 合规协议引擎

> **层级**: L2 | **版本**: 1.4.0 | **ID**: `protocol-compliance-engine` | **中文名**: 合规协议引擎 | **英文名**: Compliance Engine
# 合规协议引擎 (Compliance Engine)

> **层级**: L2 | **版本**: 1.4.0 | **ID**: `protocol-compliance-engine`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

按领域类型和监管等级激活合规子协议，执行4级合规审查(法规>平台>服务>品牌)，输出合规审查报告。与protocol-quality-gate的5.3合规层联动。分四模块条件激活：(1)4.1内容合规(2)4.2行业专项(3)4.3合规审查流程(4)4.4强监管协议(5)4.5违规应急。风险三级分流：🟢绿灯/🟡黄灯/🔴红灯。

## 触发条件

当检测到以下关键词或场景时自动激活：合规, 审查, 违规, 禁用词, 导流, 监管, 发布

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "content": {
      "type": "string",
      "description": "待审查内容"
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
    "target_platform": {
      "type": "string"
    },
    "industry_regulations": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "content",
    "domain_type",
    "target_platform"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "review_result": {
      "type": "string",
      "enum": [
        "green",
        "yellow",
        "red"
      ]
    },
    "details": {
      "type": "array",
      "items": {
        "type": "object"
      }
    },
    "action_required": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "review_result",
    "details",
    "action_required"
  ]
}
```

## 工具声明 (tool_declarations)

- **web_search**: 搜索目标平台最新合规规则 (required: False)

## 执行逻辑

分四模块条件激活：(1)4.1内容合规:按目标平台规则检查导流/绝对化用语/虚假宣传→(2)4.2行业专项:按行业类型激活对应法规(医疗/金融/法律/教育)→(3)4.3合规审查流程:三阶段(发布前/发布中/发布后)→(4)4.4强监管协议:强制信息来源标注+禁用词+免责声明→(5)4.5违规应急:5种场景响应。10项检查清单(§4.3)：0.最新规则验证;1.导流信息;2.绝对化用语;3.未核实引用;4.风险提示缺失;5.虚假宣传;6.侵权风险;7.CTA合规;8.资质标注;9.国际法规。风险三级分流：🟢绿灯→可直接发布;🟡黄灯→标注风险+替代方案+人工确认;🔴红灯→必须修改→重审。强监管禁用词下限：低复杂度≥3个;高复杂度/强监管≥8个。合规知识来源三种工具状态：有搜索工具且成功→使用最新规则;有工具但失败/无工具→静态清单+⚡标注+全🟢降级为🟡。

## 4级合规审查规则（v1.4.0新增）

| 级别 | 名称 | 优先级 | 审查内容 | 违规后果 |
|------|------|--------|---------|---------|
| L1 | 法规合规 | 最高(不可绕过) | 医疗/金融/教育/数据安全等法规要求 | 🔴阻断输出 |
| L2 | 平台合规 | 高 | 目标平台的内容发布规则和禁词 | 🔴阻断或🟡降级 |
| L3 | 服务合规 | 中 | 行业服务标准和职业道德规范 | 🟡警告 |
| L4 | 品牌合规 | 低 | 品牌声音、调性、禁用表述 | 🟡建议修改 |

## 按领域类型的合规子协议（v1.4.0新增）

### 强监管领域(自动激活)
- **医疗健康**: 4.1内容审查协议（禁用词≥8个，强制免责声明，诊疗建议🔴标注）
- **金融保险**: 4.2风险提示协议（投资风险声明，收益承诺禁止，适当性义务）
- **法律**: 4.3法律意见声明协议（非律师声明，管辖权说明，时效性声明）
- **教育**: 4.4教育内容审核协议（未成年人保护，双减合规，学历真实性）

### 弱监管领域(条件激活)
- **自媒体**: 4.5广告法合规（虚假宣传禁止，广告标识要求）
- **电商**: 4.6消费者权益保护（价格透明，退换货声明）

## Few-shot 示例

### 示例 1：正常流程 — 内容合规审查绿灯

**输入**:
```json
{
  "content": "这款保湿面霜质地轻盈，适合日常使用。了解更多请查看主页介绍。",
  "domain_type": "A",
  "target_platform": "小红书"
}
```

**输出**:
```json
{
  "review_result": "green",
  "details": [
    { "check_item": "绝对化用语", "result": "green" },
    { "check_item": "导流信息", "result": "green" },
    { "check_item": "虚假宣传", "result": "green" },
    { "check_item": "风险提示", "result": "green" }
  ],
  "action_required": []
}
```

### 示例 2：异常流程 — 金融合规审查红灯

**输入**:
```json
{
  "content": "本理财产品年化收益保底8%，稳赚不赔，点击立即购买！",
  "domain_type": "B",
  "target_platform": "微信",
  "industry_regulations": ["金融营销宣传管理办法", "银行理财销售规定"]
}
```

**输出**:
```json
{
  "review_result": "red",
  "details": [
    { "check_item": "绝对化用语", "result": "red", "reason": "'稳赚不赔'属绝对化承诺" },
    { "check_item": "风险提示缺失", "result": "red", "reason": "金融产品必须标注'投资有风险'" },
    { "check_item": "虚假宣传", "result": "red", "reason": "'保底8%'无依据" },
    { "check_item": "CTA合规", "result": "red", "reason": "'立即购买'缺少冷静期提示" }
  ],
  "action_required": [
    "删除'稳赚不赔'→添加标准风险提示语",
    "删除'保底8%'→引用真实历史数据并标注'过往业绩不预示未来'",
    "CTA改为'了解详情'并添加'市场有风险，投资需谨慎'",
    "添加信息来源于官方渠道的资质标注"
  ]
}
```

### 示例 3：快速通道 — 简化审查黄灯

**输入**:
```json
{
  "content": "今天我们聊聊如何高效管理时间",
  "domain_type": "A",
  "target_platform": "知乎",
  "channel": "fast"
}
```

**输出**:
```json
{
  "review_result": "yellow",
  "details": [
    { "check_item": "最新规则验证", "result": "yellow", "reason": "快速通道跳过web_search，使用静态清单" },
    { "check_item": "导流信息", "result": "green" },
    { "check_item": "绝对化用语", "result": "green" }
  ],
  "action_required": [
    "快速通道：已使用静态合规清单，⚡标注'知识来源为本地清单非实时规则'"
  ]
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://compliance/checklist-10-items` — 10项合规检查清单
- **[dynamic]** `file://compliance/platform-latest-rules` — 目标平台最新规则(搜索获取)

## 依赖关系

- `core-mental-model-engine`

## 详细执行逻辑

```text
FUNCTION execute_protocol_compliance_engine(input):
    ASSERT input.content IS NOT EMPTY
    ASSERT input.domain_type IN ["A","B","C","D","E","F"]
    ASSERT input.target_platform IS NOT EMPTY

    // === 第一步：判断工具状态(A型强制激活) ===
    tool_status = DETERMINE_TOOL_STATUS()
    // 三种工具状态：有搜索工具且成功 / 有工具但失败 / 无工具
    IF input.domain_type == "A":
        // A型强制激活合规协议
        FORCE_ACTIVATE("4.1内容合规+4.2行业专项")

    IF tool_status == "search_available_and_success":
        latest_rules = CALL web_search(input.target_platform + " 最新合规规则")
        rules_source = "实时搜索"
    ELIF tool_status == "search_available_but_failed":
        latest_rules = LOAD file://compliance/checklist-10-items
        rules_source = "静态清单(搜索失败)"
        // 全🟢降级为🟡
        WARN "⚡知识来源为本地清单非实时规则"
    ELSE:
        latest_rules = LOAD file://compliance/checklist-10-items
        rules_source = "静态清单"
        WARN "⚡知识来源为本地清单非实时规则"

    // === 第二步：执行10项检查清单(§4.3) ===
    details = []
    action_required = []
    risk_level = "green"  // 初始绿灯

    checklist_10 = [
        "0.最新规则验证", "1.导流信息", "2.绝对化用语",
        "3.未核实引用", "4.风险提示缺失", "5.虚假宣传",
        "6.侵权风险", "7.CTA合规", "8.资质标注", "9.国际法规"
    ]

    FOR check_item IN checklist_10:
        result = evaluate_compliance(check_item, input.content, latest_rules)
        APPEND details WITH result

        IF result.status == "red":
            risk_level = "red"
            APPEND action_required WITH result.fix_action
        ELIF result.status == "yellow":
            IF risk_level != "red":
                risk_level = "yellow"
            APPEND action_required WITH result.warning_action

    // === 第三步：按模块条件激活(4.1-4.5) ===
    // 模块1: 4.1内容合规 — 检查导流/绝对化用语/虚假宣传
    content_compliance = execute_content_compliance(input.content, input.target_platform)

    // 模块2: 4.2行业专项 — 按行业类型激活对应法规
    IF input.industry_regulations IS NOT EMPTY:
        industry_result = execute_industry_specific(input.content, input.industry_regulations)
        IF industry_result.has_violation:
            risk_level = "red"
            APPEND details WITH industry_result.violations
            APPEND action_required WITH industry_result.fix_actions

    // 模块3: 4.3合规审查流程 — 三阶段(发布前/发布中/发布后)
    review_flow = execute_three_stage_review(input.content, risk_level)

    // 模块4: 4.4强监管协议 — 强制信息来源标注+禁用词+免责声明
    IF input.domain_type IN ["B","C"] OR IS_STRONGLY_REGULATED(input):
        forced_banned_words = GET_BANNED_WORDS(input.domain_type)
        // 强监管禁用词下限：低复杂度≥3个; 高复杂度/强监管≥8个
        IF input.complexity == "low":
            ASSERT LENGTH(forced_banned_words) >= 3
        ELSE:
            ASSERT LENGTH(forced_banned_words) >= 8
        disclaimer_added = ADD_DISCLAIMER(input.content)

    // 模块5: 4.5违规应急 — 5种场景响应
    IF risk_level == "red":
        emergency_result = execute_violation_emergency(input.content, details)

    // === 第四步：三级风险分流与替代方案 ===
    IF risk_level == "green":
        // 🟢绿灯→可直接发布
        review_result = "green"
    ELIF risk_level == "yellow":
        // 🟡黄灯→标注风险+替代方案+人工确认
        review_result = "yellow"
        APPEND action_required WITH "需人工确认后发布"
        FOR detail IN details:
            IF detail.status == "yellow":
                APPEND action_required WITH "替代方案: " + detail.alternative
    ELIF risk_level == "red":
        // 🔴红灯→必须修改→重审
        review_result = "red"
        APPEND action_required WITH "🔴必须修改后重新触发protocol-compliance-engine审查"

    // === 第五步：最终断言与输出 ===
    ASSERT review_result IN ["green","yellow","red"]
    ASSERT LENGTH(details) > 0

    CALL protocol-quality-gate before final output
    RETURN {review_result, details, action_required}
```

## 版本

1.4.0

---
*本Skill由全域专家团构建skills体系生成，版本1.4.0，日期2026-06-17*
