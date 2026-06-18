---
name: protocol-single-question-guidance
description: 在信息采集阶段每次只问一个问题，生成2-4个具体选项和自定义入口，并做选项覆盖检查。 Use when: 用户说"protocol-single-question-guidance、单问引导协议、L2单问"等触发词。
version: 1.1.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [l2]
    related_skills: []
    requires_toolsets: []
---

> **注意**：本 skill 的核心规则已内联至 `team-orchestrator/SKILL.md` 的 `L2` 章节。
> 执行时优先读取 team-orchestrator 的内联指引，仅在需要完整逻辑时再读取本文件。
>
# 单问引导协议

> **层级**: L2 | **版本**: 1.1.0 | **ID**: `protocol-single-question-guidance` | **中文名**: 单问引导协议 | **英文名**: Single Question Guidance Protocol
# 单问引导协议 (Single Question Guidance Protocol)

> **层级**: L2 | **版本**: 1.0.0 | **ID**: `protocol-single-question-guidance`
> **编排关系**: 本skill由 `team-orchestrator` 按需自动加载执行，属于全域专家团构建skills系统的内部组件，用户不应直接触发。

## 概述

在信息采集阶段每次只问一个问题，生成2-4个具体选项和自定义入口，并做选项覆盖检查。

## 触发条件

当检测到以下关键词或场景时自动激活：单问, 只问一个, 选项, 信息采集, 引导

## 输入规范 (input_schema)

```json
{
  "type": "object",
  "properties": {
    "stage": {
      "type": "string"
    },
    "question": {
      "type": "object"
    },
    "user_profile": {
      "type": "object"
    }
  },
  "required": [
    "stage",
    "question"
  ]
}
```

## 输出规范 (output_schema)

```json
{
  "type": "object",
  "properties": {
    "question_text": {
      "type": "string"
    },
    "options": {
      "type": "array"
    },
    "summary": {
      "type": "string"
    }
  },
  "required": [
    "question_text",
    "options"
  ]
}
```

## 工具声明 (tool_declarations)

本Skill无外部工具依赖，纯提示词可执行。

## 执行逻辑

封闭到开放递进；每轮只问一题；所有选项必须具体；需要先验知识时先给例子；确认阶段可展示汇总卡。

## 详细执行逻辑

```text
FUNCTION execute_protocol_single_question_guidance(input):
    ASSERT input.stage IS NOT EMPTY
    ASSERT input.question IS NOT EMPTY

    // === 6大约束规则 ===
    // 约束1: 每轮只问一题(ONE_QUESTION_ONLY)
    // 约束2: 所有选项必须具体(非抽象描述)
    // 约束3: 封闭到开放递进(先选项后自定义)
    // 约束4: 需要先验知识时先给例子
    // 约束5: 选项覆盖检查(确保覆盖所有可能)
    // 约束6: 确认阶段可展示汇总卡(例外)

    RULE ONE_QUESTION_ONLY  // 约束1: 每轮只问一题

    // === 第一步：先验知识检测(约束4) ===
    IF question_requires_prior_knowledge(input.question):
        // 需要先验知识时先给例子
        domain = input.user_profile.domain IF input.user_profile EXISTS ELSE "通用"
        example = contextual_example(input.question, domain)

        IF domain == "疑似医疗" OR domain == "疑似金融" OR domain == "疑似法律":
            // 强监管行业先验知识示例需更详尽
            example = contextual_example_with_regulatory_warning(input.question, domain)
            OUTPUT example
        ELSE:
            OUTPUT example

    // === 第二步：生成2-4个具体选项(约束2+3) ===
    options = generate_2_to_4_specific_options(input.question, input.user_profile)

    // 约束2: 所有选项必须具体(非抽象描述)
    FOR option IN options:
        IF IS_ABSTRACT(option):
            option = MAKE_SPECIFIC(option, input.user_profile)
        ASSERT NOT IS_ABSTRACT(option)  // 确保选项具体

    // 约束3: 封闭到开放递进 — 最后添加自定义入口
    APPEND options WITH "自定义：___"

    // === 第三步：选项覆盖检查(约束5) ===
    coverage = self_check_option_coverage(options, input.user_profile.domain)
    IF NOT coverage.complete:
        FOR missing IN coverage.missing_scenarios:
            APPEND options WITH missing

    // 强监管行业额外覆盖检查
    IF input.user_profile.domain CONTAINS "医疗":
        IF NOT ANY(options, o => o CONTAINS "在线问诊"):
            APPEND options WITH "在线问诊 — 涉及医患交互和诊疗建议"
        IF NOT ANY(options, o => o CONTAINS "医疗科普"):
            APPEND options WITH "医疗科普 — 面向公众的健康知识传播"
    IF input.user_profile.domain CONTAINS "金融":
        IF NOT ANY(options, o => o CONTAINS "理财"):
            APPEND options WITH "理财营销 — 涉及金融产品推荐"

    // === 第四步：术语翻译(用户层) ===
    question_text = input.question.text
    IF input.user_profile EXISTS AND input.user_profile.experience == "beginner":
        // 术语首次出现附通俗解释
        terms = EXTRACT_JARGON(question_text)
        FOR term IN terms:
            plain_explanation = TRANSLATE_TO_PLAIN_LANGUAGE(term)
            question_text = REPLACE(question_text, term, term + "(" + plain_explanation + ")")

    // === 第五步：确认阶段例外处理(约束6) ===
    summary = GENERATE_ONE_SENTENCE_SUMMARY(question_text, options)

    IF input.stage == "confirmation" OR input.stage_type == "confirmation":
        // 约束6: 确认阶段可展示汇总卡
        summary_card = GENERATE_SUMMARY_CARD(input.user_profile, options)
        summary = summary + " | 汇总卡: " + summary_card

    // === 第六步：快速通道已确认信息跳过 ===
    IF input.user_profile EXISTS AND input.user_profile.channel == "fast":
        // 已确认信息跳过重复提问
        confirmed_info = GET_CONFIRMED_INFO(input.user_profile)
        IF ALL_REQUIRED_CONFIRMED(confirmed_info, input.question):
            question_text = "根据前面信息，" + AUTO_FILL(confirmed_info, input.question)
            options = ["确认，继续", "不确定，帮我先评估一下", "自定义：___"]
            summary = "快速通道：已根据前序信息自动判定，跳过详细询问直接确认。"

    // === 第七步：最终断言与输出 ===
    ASSERT LENGTH(options) >= 2  // 至少2个选项
    ASSERT LENGTH(options) <= 5  // 最多4个选项+1个自定义
    ASSERT question_text IS NOT EMPTY
    ASSERT NOT CONTAINS_MULTIPLE_QUESTIONS(question_text)  // 约束1确认

    CALL protocol-quality-gate before final output
    RETURN {question_text, options, summary}
```

## Few-shot 示例

### 示例 1：正常流程 — 信息采集阶段单问引导

**输入**:
```json
{
  "stage": "S2_消歧",
  "question": {
    "text": "请选择您的业务领域类型",
    "type": "single_choice"
  },
  "user_profile": {
    "domain": "未知",
    "experience": "intermediate"
  }
}
```

**输出**:
```json
{
  "question_text": "您的业务主要属于以下哪种类型？",
  "options": [
    "A. 内容传播 — 如自媒体运营、品牌营销、社媒内容创作",
    "B. 客户服务 — 如客服助手、售后支持、咨询应答",
    "C. 知识管理 — 如文档库、内部培训、知识问答",
    "D. 数据驱动 — 如数据分析、自动化报告、监控告警",
    "E. 复合场景 — 以上两种或更多类型的组合",
    "自定义：___（请输入您的业务描述）"
  ],
  "summary": "选择最匹配的一个业务类型，帮助我为您定制最佳方案。"
}
```

### 示例 2：异常流程 — 监管行业选项覆盖检查

**输入**:
```json
{
  "stage": "S2_消歧",
  "question": {
    "text": "请选择您的行业",
    "type": "single_choice"
  },
  "user_profile": {
    "domain": "疑似医疗",
    "experience": "beginner"
  }
}
```

**输出**:
```json
{
  "question_text": "您的业务涉及以下哪个具体领域？",
  "options": [
    "A. 医疗科普 — 面向公众的健康知识传播",
    "B. 在线问诊 — 涉及医患交互和诊疗建议",
    "C. 药品信息 — 药品说明书、用药指导",
    "D. 医疗器械 — 器械使用说明、操作指南",
    "E. 健康管理 — 体检报告解读、健康建议",
    "F. 医疗机构 — 医院/诊所官方信息发布",
    "自定义：___（请输入具体医疗场景）"
  ],
  "summary": "医疗行业受强监管，我需要确认具体场景以激活对应的合规协议。属于以上之一吗？"
}
```

### 示例 3：快速通道 — 已确认信息跳过重复提问

**输入**:
```json
{
  "stage": "S4_通道选择",
  "question": {
    "text": "请确认项目复杂度",
    "type": "confirmation"
  },
  "user_profile": {
    "domain": "A",
    "role_count": 1,
    "experience": "beginner",
    "channel": "fast"
  }
}
```

**输出**:
```json
{
  "question_text": "根据前面信息，您的项目属于低复杂度单人场景。我将按快速通道处理：",
  "options": [
    "确认，继续快速通道",
    "不确定，帮我先评估一下复杂度",
    "自定义：___"
  ],
  "summary": "快速通道：已根据S2-S3信息自动判定为低复杂度，跳过详细询问直接确认。"
}
```

## 知识库挂载点 (knowledge_base_mount_points)

- **[static]** `file://doc1/protocol-single-question-guidance/rules` — Doc1对应SK原始规则
- **[dynamic]** `file://runtime/protocol-single-question-guidance/state` — 运行时状态
- **[rag]** `file://rag/protocol-single-question-guidance/references` — 向量检索参考资料

## 依赖关系

- `core-mental-model-engine`

## 版本

1.0.0

---
*本Skill由全域专家团构建skills体系修复生成，版本1.0.0，日期2026-06-15*
